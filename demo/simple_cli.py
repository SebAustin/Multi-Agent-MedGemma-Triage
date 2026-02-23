"""
Simple CLI interface for testing the triage system without Gradio.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.triage_workflow import TriageWorkflow
from src.utils.logger import logger


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70 + "\n")


def main():
    """Run simple CLI interface."""
    print_separator()
    print("MedGemma AI Medical Triage System - CLI Demo")
    print_separator()
    
    print("⚠️  DISCLAIMER: This is a demo system for research purposes only.")
    print("For medical emergencies, call 911 immediately.")
    print_separator()
    
    # Initialize workflow
    print("Loading MedGemma models... (this may take a minute)")
    try:
        workflow = TriageWorkflow()
        print("✓ System ready!")
    except Exception as e:
        print(f"✗ Error loading system: {e}")
        return
    
    print_separator()
    print("Describe your symptoms (or 'quit' to exit):")
    
    while True:
        print("\n> ", end="")
        user_input = input().strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        print("\nProcessing your symptoms...")
        print_separator()
        
        try:
            # Run triage
            result = workflow.run_triage(user_input)
            
            if result.get("error"):
                print(f"Error: {result['error']}")
            elif result.get("needs_more_info"):
                print(result["response"])
                print("\n(Note: CLI mode doesn't support follow-up questions well)")
                print("Try providing more details in your initial description.")
            else:
                # Display formatted report
                print(result.get("formatted_report", result.get("report", "No report available")))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\nError processing triage: {e}")
        
        print_separator()
        print("Describe more symptoms (or 'quit' to exit):")


if __name__ == "__main__":
    main()
