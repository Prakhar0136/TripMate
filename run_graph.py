import uuid
from src.core.graph import app

def main():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "user_query": "I need to know the weather and book a flight to Tokyo for next week."
    }
    
    print("--- Starting TripMate Execution ---")
    for event in app.stream(initial_state, config=config):
        for node_name, node_state in event.items():
            print(f"\n[Node Executed: {node_name}]")
            
            if node_state and node_name == "validate" and node_state.get("rejection_reason"):
                print(f"Blocked: {node_state['rejection_reason']}")
            elif node_state and node_name == "supervisor":
                print(f"Selected Agents: {node_state.get('selected_agents')}")
            elif node_name == "itinerary":
                print("\n=== Generated Itinerary Draft ===")
                if node_state and "itinerary_plan" in node_state:
                    print(node_state["itinerary_plan"].get("draft", ""))

if __name__ == "__main__":
    main()