from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agents.final_response import final_response_node
from src.agents.specialists import (
    flight_agent_node,
    hotel_agent_node,
    itinerary_agent_node,
    weather_agent_node,
)
from src.agents.supervisor import route_to_specialists, supervisor_node
from src.core.state import TravelState
from src.guardrails.validator import validate_input_node


def route_after_human(state: TravelState) -> str:
    """Routes based on user feedback provided during the interrupt."""
    if state.get("hitl_approved"):
        return "final_response"
   
    return "supervisor"

def build_graph():
    """
    Constructs the TripMate execution graph.
    """
    workflow = StateGraph(TravelState)
    
    workflow.add_node("validate", validate_input_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("weather", weather_agent_node)
    workflow.add_node("flight", flight_agent_node)
    workflow.add_node("hotel", hotel_agent_node)
    workflow.add_node("itinerary", itinerary_agent_node)
    
    def human_review_node(state: TravelState) -> dict:
        return {}

    workflow.add_node("human_review", human_review_node)
    workflow.add_node("final_response", final_response_node)

    workflow.add_edge(START, "validate")
    
    def check_validation(state: TravelState) -> str:
        if state.get("rejection_reason"):
            return END
        return "supervisor"
        
    workflow.add_conditional_edges("validate", check_validation)
    
    workflow.add_conditional_edges(
        "supervisor", 
        route_to_specialists,
        {
            "weather": "weather",
            "flight": "flight",
            "hotel": "hotel",
            "itinerary": "itinerary",
        }
    )
    
    workflow.add_edge("weather", "itinerary")
    workflow.add_edge("flight", "itinerary")
    workflow.add_edge("hotel", "itinerary")
    workflow.add_edge("itinerary", "human_review")
    workflow.add_conditional_edges(
        "human_review",
        route_after_human,
        {"final_response": "final_response", "supervisor": "supervisor"}
    )
    
    workflow.add_edge("final_response", END)
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory, interrupt_before=["human_review"])
    
    return app

app = build_graph()
