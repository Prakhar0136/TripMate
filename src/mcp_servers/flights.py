import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Flight Search Server")

@mcp.tool()
def search_flights(origin: str, destination: str, date: str) -> list[dict]:
    """
    Searches for available flights between two locations.
    Args:
        origin: Departure city or airport code.
        destination: Arrival city or airport code.
        date: Date of departure (YYYY-MM-DD).
    """

    airlines = ["SkyWay", "AeroGlobal", "CloudAir", "JetStream", "PacificWings"]
    selected_airlines = random.sample(airlines, min(3, len(airlines)))
    
    mock_results = []
    for airline in selected_airlines:
        flight_number = f"{airline[:2].upper()}{random.randint(100, 999)}"
        mock_results.append({
            "flight_number": flight_number,
            "airline": airline,
            "origin": origin,
            "destination": destination,
            "departure_date": date,
            "price_usd": random.randint(150, 800),
            "status": "Available"
        })
        
    return sorted(mock_results, key=lambda x: x["price_usd"])

if __name__ == "__main__":
    mcp.run()
