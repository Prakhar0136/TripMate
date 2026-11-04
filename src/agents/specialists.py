import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from src.core.config import get_llm
from src.core.state import TravelState


@tool
def get_weather(latitude: float, longitude: float) -> str:
    """Get current weather conditions for a specific location."""
    import httpx
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    response = httpx.get(url)
    return json.dumps(response.json().get("current_weather", {}))

@tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """Mock search for available flights between two locations."""
    import random
    airlines = ["SkyWay", "AeroGlobal", "CloudAir"]
    results = [{"airline": random.choice(airlines), "price": random.randint(150, 800)} for _ in range(2)]
    return json.dumps(results)

@tool
def search_hotels(location: str, check_in: str = "", check_out: str = "") -> str:
    """Mock search for available hotel options in a given location."""
    import random
    chains = ["Grand Stay", "Central Suites", "Boutique Inn", "Comfort Lodge"]
    results = [
        {
            "hotel": f"{random.choice(chains)} {location}",
            "price_per_night_usd": random.randint(120, 450),
            "rating": round(random.uniform(4.0, 4.9), 1)
        }
        for _ in range(3)
    ]
    return json.dumps(results)

def weather_agent_node(state: TravelState) -> dict:
    """Fetches weather data and updates the state."""
    llm = get_llm().bind_tools([get_weather])
    sys_msg = SystemMessage(content="You are a weather specialist. Use the weather tool based on the user query and constraints.")
    response = llm.invoke([sys_msg, HumanMessage(content=state["user_query"])])
    return {"weather_info": {"data": response.content, "tool_calls": response.tool_calls}}

def flight_agent_node(state: TravelState) -> dict:
    """Searches for flights and updates the state."""
    llm = get_llm().bind_tools([search_flights])
    sys_msg = SystemMessage(content="You are a flight specialist. Find flights based on the user query.")
    response = llm.invoke([sys_msg, HumanMessage(content=state["user_query"])])
    return {"flight_results": {"data": response.content, "tool_calls": response.tool_calls}}

def hotel_agent_node(state: TravelState) -> dict:
    """Searches for hotels and updates the state."""
    llm = get_llm().bind_tools([search_hotels])
    sys_msg = SystemMessage(content="You are a hotel specialist. Find accommodations based on the user query and destination.")
    response = llm.invoke([sys_msg, HumanMessage(content=state["user_query"])])
    return {"hotel_results": {"data": response.content, "tool_calls": response.tool_calls}}

def itinerary_agent_node(state: TravelState) -> dict:
    """Synthesizes all gathered data into a day-by-day itinerary."""
    llm = get_llm()
    prompt = f"""
    You are an expert travel planner. Create a daily itinerary based on this data:
    User Query: {state['user_query']}
    Flights: {state.get('flight_results', 'None')}
    Hotels: {state.get('hotel_results', 'None')}
    Weather: {state.get('weather_info', 'None')}
    Constraints: {state.get('trip_constraints', 'None')}
    """
    sys_msg = SystemMessage(content="You are an expert travel planner. Create a daily itinerary based on the gathered travel data.")
    user_msg = HumanMessage(content=prompt)
    response = llm.invoke([sys_msg, user_msg])
    return {"itinerary_plan": {"draft": response.content}}
