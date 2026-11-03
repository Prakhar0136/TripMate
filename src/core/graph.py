from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.core.state import TravelState
from src.guardrails.validator import validate_input_node
from src.agents.supervisor import supervisor_node, route_to_specialists
from src.agents.specialists import weather_agent_node, flight_agent_node, itinerary_agent_node

def build_graph():
    """
    Constructs the TripMate execution graph.
    """
    workflow = StateGraph(TravelState)
    
    workflow.add_node("validate", validate_input_node)
    workflow.add_node("supervisor", supervisor_node)
    
    workflow.add_node("weather", weather_agent_node)
    workflow.add_node("flight", flight_agent_node)
    
    workflow.add_node("itinerary", itinerary_agent_node)
    
    workflow.add_edge(START, "validate")
    
    def check_validation(state: TravelState) -> str:
        if state.get("rejection_reason"):
            return END
        return "supervisor"
        
    workflow.add_conditional_edges("validate", check_validation)
    
    workflow.add_conditional_edges(
        "supervisor", 
        route_to_specialists,
        {"weather": "weather", "flight": "flight", "itinerary": "itinerary"}
    )
    
    workflow.add_edge("weather", "itinerary")
    workflow.add_edge("flight", "itinerary")
    
    workflow.add_edge("itinerary", END)
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

app = build_graph()