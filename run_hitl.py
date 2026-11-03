import sys
import uuid
from src.core.graph import app

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {"user_query": "Plan a short trip to Paris with flights and weather."}
    
    print("--- Starting Execution ---")
    for event in app.stream(initial_state, config=config):
        for node, output in event.items():
            print(f"[Node Executed: {node}]")
        
    state = app.get_state(config)
    print("\n--- GRAPH PAUSED FOR HUMAN REVIEW ---")
    draft = state.values.get("itinerary_plan", {}).get("draft", "N/A")
    if isinstance(draft, list):
        draft_str = "\n".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in draft
        )
        print(f"Draft Itinerary:\n{draft_str}")
    else:
        print(f"Draft Itinerary:\n{draft}")
    
    print("\n--- RESUMING WITH APPROVAL ---")
    app.update_state(config, {"hitl_approved": True}, as_node="human_review")
    
    for event in app.stream(None, config=config):
        for node, output in event.items():
            print(f"\n[Node Executed: {node}]")
            if node == "final_response" and output and "messages" in output:
                msg = output["messages"][-1]
                content = getattr(msg, "content", msg)
                if isinstance(content, list):
                    text = "".join(
                        item.get("text", str(item)) if isinstance(item, dict) else str(item)
                        for item in content
                    )
                    print(text)
                else:
                    print(content)

if __name__ == "__main__":
    main()
