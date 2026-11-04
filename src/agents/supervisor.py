from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.core.config import get_llm
from src.core.state import TravelState


class SupervisorDecision(BaseModel):
    selected_agents: list[
        Literal["flight", "hotel", "weather", "budget"]
    ]  

    trip_constraints: dict[str, str] = Field(
        description="Extracted parameters such as destination, dates, budget limit, and party size."
    )
    reasoning: str = Field(
        description="Brief explanation of why these specific agents were chosen."
    )

def supervisor_node(state: TravelState) -> dict:
    """
    LangGraph node: Analyzes intent and dynamically routes to specialist agents.
    Replaces manual workflow definitions with intelligent orchestration.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(SupervisorDecision)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the Supervisor Agent for TripMate.
        Your task is to analyze the user's travel request and decide which specialist agents are needed.
        - If they mention flights, airlines, or tickets, select 'flight'.
        - If they mention staying, accommodation, or hotels, select 'hotel'.
        - If they ask about climate, temperature, or packing, select 'weather'.
        - If they mention cost limits or tracking expenses, select 'budget'.
        
        Extract any constraints (e.g., {{"destination": "Dubai", "duration": "4 days"}}).
        """),
        ("user", "{user_query}")
    ])
    
    chain = prompt | structured_llm
    
    decision: SupervisorDecision = chain.invoke({"user_query": state.get("user_query", "")})
    
    return {
        "selected_agents": decision.selected_agents,
        "trip_constraints": decision.trip_constraints
    }

AVAILABLE_SPECIALISTS = {"flight", "weather", "hotel"}

def route_to_specialists(state: TravelState) -> list[str]:
    """
    Conditional edge function for LangGraph.
    Reads the 'selected_agents' from the state and maps them to actual graph nodes.
    If no specialists are needed, it routes directly to the itinerary agent.
    """
    selected = state.get("selected_agents", [])
    valid_selected = [agent for agent in selected if agent in AVAILABLE_SPECIALISTS]
    
    if not valid_selected:
        return ["itinerary"]
        
    return valid_selected
