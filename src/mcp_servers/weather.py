import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Weather Server")

@mcp.tool()
def get_current_weather(latitude: float, longitude: float) -> dict:
    """
    Get current weather conditions for a specific location using Open-Meteo.
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
    """
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return {
            "error": "Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180."
        }

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("current_weather", {})
    except httpx.HTTPError as e:
        return {"error": f"Failed to retrieve weather data: {e!s}"}

@mcp.tool()
def get_weather_by_city(city: str) -> dict:
    """
    Get current weather conditions for a city by name using Open-Meteo geocoding.
    Args:
        city: Name of the city (e.g. 'Paris', 'Tokyo', 'Dubai')
    """
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    try:
        with httpx.Client(timeout=10.0) as client:
            geo_resp = client.get(geo_url)
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()
            
            results = geo_data.get("results")
            if not results:
                return {"error": f"Could not find coordinates for city: {city}"}
            
            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            city_name = results[0].get("name", city)
            country = results[0].get("country", "")

        weather = get_current_weather(lat, lon)
        weather["city"] = city_name
        weather["country"] = country
        weather["latitude"] = lat
        weather["longitude"] = lon
        return weather
    except httpx.HTTPError as e:
        return {"error": f"Failed to lookup city weather: {e!s}"}

if __name__ == "__main__":
    mcp.run()
