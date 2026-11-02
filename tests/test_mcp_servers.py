from unittest.mock import MagicMock, patch

from src.mcp_servers.flights import search_flights
from src.mcp_servers.search import search_hotels
from src.mcp_servers.weather import get_current_weather, get_weather_by_city


def test_search_flights():
    results = search_flights("JFK", "DXB", "2026-12-01")
    assert isinstance(results, list)
    assert len(results) == 3
    for flight in results:
        assert "flight_number" in flight
        assert "airline" in flight
        assert flight["origin"] == "JFK"
        assert flight["destination"] == "DXB"
        assert flight["departure_date"] == "2026-12-01"
        assert isinstance(flight["price_usd"], int)
        assert flight["status"] == "Available"
    
    # Assert sorted ascending by price
    assert results[0]["price_usd"] <= results[1]["price_usd"] <= results[2]["price_usd"]

def test_weather_invalid_coordinates():
    res = get_current_weather(100.0, 50.0)
    assert "error" in res

def test_weather_get_current_weather_mock():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "current_weather": {
            "temperature": 28.5,
            "windspeed": 12.0,
            "weathercode": 0
        }
    }
    with patch("httpx.Client.get", return_value=mock_resp):
        res = get_current_weather(25.2048, 55.2708)
        assert res.get("temperature") == 28.5

def test_weather_by_city_mock():
    geo_resp = MagicMock()
    geo_resp.json.return_value = {
        "results": [{
            "name": "Dubai",
            "country": "United Arab Emirates",
            "latitude": 25.2048,
            "longitude": 55.2708
        }]
    }
    weather_resp = MagicMock()
    weather_resp.json.return_value = {
        "current_weather": {
            "temperature": 30.0
        }
    }
    with patch("httpx.Client.get", side_effect=[geo_resp, weather_resp]):
        res = get_weather_by_city("Dubai")
        assert res.get("city") == "Dubai"
        assert res.get("temperature") == 30.0

def test_search_hotels_mock_success():
    mock_items = [
        {"title": "Grand Hotel", "href": "https://grand.com", "body": "Luxury stay"},
        {"title": "Beach Resort", "href": "https://beach.com", "body": "Sea view"}
    ]
    with patch("src.mcp_servers.search.DDGS") as mock_ddgs:
        instance = MagicMock()
        instance.text.return_value = mock_items
        mock_ddgs.return_value.__enter__.return_value = instance
        
        results = search_hotels("Dubai", "2026-12-01", "2026-12-05")
        assert len(results) == 2
        assert results[0]["title"] == "Grand Hotel"

def test_search_hotels_mock_fallback_on_error():
    with patch("src.mcp_servers.search.DDGS") as mock_ddgs:
        instance = MagicMock()
        instance.text.side_effect = Exception("Rate limit exceeded")
        mock_ddgs.return_value.__enter__.return_value = instance
        
        results = search_hotels("Dubai")
        assert len(results) == 1
        assert "error" in results[0]

