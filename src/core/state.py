from typing import Annotated, TypedDict, Any
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class TravelState(TypedDict):
    """
    Shared state for the TripMate multi-agent workflow.
    Every node reads from and writes updates to this state.
    """
    messages: Annotated[list[AnyMessage], add_messages]

    user_query: str
    trip_constraints: dict[str, Any]
    
    selected_agents: list[str]
    
    flight_results: dict[str, Any] | None
    hotel_results: dict[str, Any] | None
    weather_info: dict[str, Any] | None
    budget_analysis: dict[str, Any] | None
    
    itinerary_plan: dict[str, Any] | None
    hitl_approved: bool
    rejection_reason: str | None