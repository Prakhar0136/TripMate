import base64
import uuid

import gradio as gr

from src.core.graph import app


def generate_thread_id():
    return str(uuid.uuid4())

def format_content(content) -> str:
    if isinstance(content, list):
        return "\n".join(
            item.get("text", str(item)) if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)

def process_input(query: str, image_path: str | None, thread_id: str):
    """Starts the LangGraph execution and pauses at the HITL breakpoint."""
    config = {"configurable": {"thread_id": thread_id}}
    
    combined_query = query
    if image_path:
        with open(image_path, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
        combined_query += f"\n[User provided an image attachment. Base64: {img_b64[:50]}...]"

    initial_state = {"user_query": combined_query}
    
    for _ in app.stream(initial_state, config=config):
        pass 
        
    state = app.get_state(config)
    raw_draft = state.values.get("itinerary_plan", {}).get("draft", "Failed to generate draft.")
    draft = format_content(raw_draft)
    
    return draft, gr.update(visible=True)

def approve_plan(thread_id: str):
    """Resumes the graph with an approval state."""
    config = {"configurable": {"thread_id": thread_id}}
    
    app.update_state(config, {"hitl_approved": True}, as_node="human_review")
    
    final_output = ""
    for event in app.stream(None, config=config):
        if "final_response" in event:
            raw_msg = event["final_response"]["messages"][-1].content
            final_output = format_content(raw_msg)
            
    return final_output, gr.update(visible=False)

def request_changes(thread_id: str, feedback: str):
    """Resumes the graph by rejecting the draft and appending user feedback."""
    config = {"configurable": {"thread_id": thread_id}}
    
    current_state = app.get_state(config).values
    new_query = f"{current_state.get('user_query')} \nFeedback on draft: {feedback}"
    
    app.update_state(config, {
        "hitl_approved": False, 
        "user_query": new_query
    }, as_node="human_review")
    
    for _ in app.stream(None, config=config):
        pass
        
    new_state = app.get_state(config)
    raw_draft = new_state.values.get("itinerary_plan", {}).get("draft", "Failed to update draft.")
    new_draft = format_content(raw_draft)
    return new_draft, gr.update(value="") 

with gr.Blocks(title="TripMate AI") as ui:
    gr.Markdown("# ✈️ TripMate AI Planner")
    session_id = gr.State(generate_thread_id)
    
    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(label="Where do you want to go?", placeholder="e.g., Plan a 4 day trip to Dubai...")
            image_input = gr.Image(type="filepath", label="Upload Inspiration Image (Optional)")
            submit_btn = gr.Button("Generate Draft", variant="primary")
            
        with gr.Column():
            draft_output = gr.Markdown("### Draft Itinerary will appear here.")
            
            with gr.Group(visible=False) as hitl_controls:
                approve_btn = gr.Button("✅ Approve Plan", variant="secondary")
                feedback_input = gr.Textbox(label="Request Changes", placeholder="e.g., Make it cheaper, change hotel...")
                modify_btn = gr.Button("🔄 Update Draft")
                
    final_output = gr.Markdown("### Final Plan:")
    
    submit_btn.click(
        process_input, 
        inputs=[user_input, image_input, session_id], 
        outputs=[draft_output, hitl_controls]
    )
    
    approve_btn.click(
        approve_plan, 
        inputs=[session_id], 
        outputs=[final_output, hitl_controls]
    )
    
    modify_btn.click(
        request_changes,
        inputs=[session_id, feedback_input],
        outputs=[draft_output, feedback_input]
    )

if __name__ == "__main__":
    ui.launch(server_port=7860)
