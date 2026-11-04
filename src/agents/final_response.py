from langchain_core.messages import HumanMessage, SystemMessage

from src.core.config import get_llm
from src.core.state import TravelState


def final_response_node(state: TravelState) -> dict:
    """
    Generates the final, well-structured travel package after user approval.
    """
    llm = get_llm()
    
    draft = state.get("itinerary_plan", {}).get("draft", "")
    if isinstance(draft, list):
        draft_text = "\n".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in draft
        )
    else:
        draft_text = str(draft)
        
    sys_msg = SystemMessage(
        content="You are the final response agent for TripMate. Format the approved itinerary into a highly polished, friendly, and structured final travel plan."
    )
    user_msg = HumanMessage(
        content=f"The user has approved the following itinerary draft. Please produce the final formatted travel package:\n\n{draft_text}"
    )
    
    response = llm.invoke([sys_msg, user_msg])
    return {"messages": [response]}
