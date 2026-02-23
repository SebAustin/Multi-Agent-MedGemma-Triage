"""
Gradio Demo Application for MedGemma AI Medical Triage System.
"""
import gradio as gr
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.triage_workflow import TriageWorkflow
from src.utils.logger import logger
from config import DemoConfig

# Initialize workflow
logger.info("Initializing demo application...")
workflow = TriageWorkflow()

# Session state
current_session_id = None


def process_input(message, history):
    """
    Process user input and return response.
    
    Args:
        message: User's message
        history: Chat history
        
    Returns:
        Updated history
    """
    global current_session_id
    
    try:
        if current_session_id is None or len(history) == 0:
            # Start new triage session
            logger.info("Starting new triage session")
            result = workflow.start_triage(message)
            current_session_id = result["session_id"]
            
            if result.get("needs_more_info"):
                # Still in intake phase
                response = result["response"]
            else:
                # Completed triage
                response = _format_complete_response(result)
                current_session_id = None  # Reset for next session
        else:
            # Continue existing session
            logger.info(f"Continuing session {current_session_id}")
            result = workflow.continue_intake(current_session_id, message)
            
            if result.get("needs_more_info"):
                # Still gathering info
                response = result["response"]
            else:
                # Completed triage
                response = _format_complete_response(result)
                current_session_id = None  # Reset for next session
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        current_session_id = None
        return f"I apologize, but an error occurred: {str(e)}\n\nPlease start a new conversation."


def _format_complete_response(result):
    """Format the complete triage result for display."""
    if result.get("error"):
        return f"Error: {result['error']}"
    
    # Use the formatted report
    return result.get("formatted_report", result.get("report", "Triage completed."))


def reset_session():
    """Reset the current session."""
    global current_session_id
    current_session_id = None
    logger.info("Session reset")
    return None


# Example scenarios
EXAMPLES = [
    ["I've had severe chest pain for the last hour that won't go away."],
    ["I have a mild headache and stuffy nose that started yesterday."],
    ["I twisted my ankle while running and now it's swollen and painful."],
    ["I've had a high fever (103°F) for two days with body aches."],
    ["I'm feeling short of breath and my heart is racing."]
]


# Custom CSS
custom_css = """
.disclaimer {
    background-color: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    font-size: 14px;
}
.disclaimer-title {
    font-weight: bold;
    color: #856404;
    margin-bottom: 8px;
}
.disclaimer-text {
    color: #856404;
}
"""


def create_demo():
    """Create the Gradio demo interface."""
    
    with gr.Blocks(
        theme=gr.themes.Soft(),
        css=custom_css,
        title=DemoConfig.TITLE
    ) as demo:
        
        gr.Markdown(f"# {DemoConfig.TITLE}")
        gr.Markdown(DemoConfig.DESCRIPTION)
        
        # Disclaimer
        with gr.Row():
            gr.HTML("""
            <div class="disclaimer">
                <div class="disclaimer-title">⚠️ IMPORTANT MEDICAL DISCLAIMER</div>
                <div class="disclaimer-text">
                    This is a demonstration system for research and educational purposes only.
                    It does NOT provide medical advice, diagnosis, or treatment.
                    <br><br>
                    <strong>For medical emergencies, call 911 immediately.</strong>
                    <br><br>
                    Always consult qualified healthcare professionals for medical concerns.
                    This AI system is not a substitute for professional medical care.
                </div>
            </div>
            """)
        
        # Main chat interface
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="AI Triage Assistant",
                    height=500,
                    show_copy_button=True
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        label="Describe your symptoms",
                        placeholder="Tell me about your symptoms, when they started, and how severe they are...",
                        lines=3,
                        scale=4
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
                
                with gr.Row():
                    clear_btn = gr.Button("New Patient / Clear", variant="secondary")
                
                # Examples
                gr.Examples(
                    examples=EXAMPLES,
                    inputs=msg,
                    label="Try these example scenarios:"
                )
            
            # Info panel
            with gr.Column(scale=1):
                gr.Markdown("### How It Works")
                gr.Markdown("""
                This system uses **six specialized AI agents** powered by MedGemma:
                
                1. **Intake Agent** - Collects your symptoms
                2. **Symptom Assessment Agent** - Analyzes your condition
                3. **Medical Knowledge Agent** - Provides medical context
                4. **Urgency Classification Agent** - Determines urgency level
                5. **Care Recommendation Agent** - Suggests appropriate care
                6. **Communication Agent** - Creates clear reports
                
                The agents work together to provide comprehensive triage assessment.
                """)
                
                gr.Markdown("### Urgency Levels")
                gr.Markdown("""
                - 🚨 **EMERGENCY** - Immediate attention (call 911)
                - ⚡ **URGENT** - Care needed within hours
                - ⚠️ **SEMI-URGENT** - Care needed within 1-2 days
                - ℹ️ **NON-URGENT** - Routine care sufficient
                """)
                
                gr.Markdown("### About MedGemma")
                gr.Markdown("""
                MedGemma is Google's medical AI model from the Health AI Developer Foundations (HAI-DEF) collection, 
                designed specifically for healthcare applications.
                
                [Learn more about HAI-DEF](https://ai.google.dev/gemma/docs/medgemma)
                """)
        
        # Event handlers
        def user_message(message, history):
            """Add user message to history."""
            return "", history + [[message, None]]
        
        def bot_response(history):
            """Generate bot response."""
            user_msg = history[-1][0]
            response = process_input(user_msg, history[:-1])
            history[-1][1] = response
            return history
        
        msg.submit(
            user_message,
            [msg, chatbot],
            [msg, chatbot],
            queue=False
        ).then(
            bot_response,
            chatbot,
            chatbot
        )
        
        submit_btn.click(
            user_message,
            [msg, chatbot],
            [msg, chatbot],
            queue=False
        ).then(
            bot_response,
            chatbot,
            chatbot
        )
        
        clear_btn.click(
            lambda: (reset_session(), None),
            None,
            chatbot,
            queue=False
        )
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("""
        <div style="text-align: center; font-size: 12px; color: #666;">
            Built with MedGemma and HAI-DEF | MedGemma Impact Challenge 2026
            <br>
            This is a demonstration project and not approved for clinical use.
        </div>
        """)
    
    return demo


if __name__ == "__main__":
    logger.info("Starting demo application...")
    
    demo = create_demo()
    
    demo.queue()
    demo.launch(
        server_name=DemoConfig.SERVER_NAME,
        server_port=DemoConfig.PORT,
        share=DemoConfig.SHARE,
        show_error=True
    )
