from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Web Search Server")

@mcp.tool()
def search_hotels(location: str, check_in: str = "", check_out: str = "") -> list[dict]:
    """
    Searches the web for hotel options in a given location.
    Args:
        location: City or area to search.
        check_in: Check-in date (YYYY-MM-DD), optional.
        check_out: Check-out date (YYYY-MM-DD), optional.
    """
    if check_in and check_out:
        query = f"top hotels in {location} available from {check_in} to {check_out} reviews"
    else:
        query = f"top hotels in {location} reviews recommendations"
    
    results = []
    
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")
                })
    except Exception as e:  # noqa: BLE001 
        results.append({
            "error": f"Search failed: {e!s}",
            "title": f"Fallback recommendations for {location}",
            "body": f"Unable to fetch live web results. Consider popular hotels in {location}."
        })
            
    return results

if __name__ == "__main__":
    mcp.run()
