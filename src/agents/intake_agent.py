"""
Intake Agent - Collects initial patient information.
"""
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.models.prompt_templates import PromptTemplates
from src.utils.logger import logger


class IntakeAgent(BaseAgent):
    """Agent responsible for initial patient intake and information gathering."""
    
    def __init__(self):
        super().__init__(name="Intake Agent")
        self.conversation_history: List[Dict[str, str]] = []
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process patient input and collect information.
        
        Args:
            input_data: Dict with 'patient_input' and optional 'is_initial'
            
        Returns:
            Dict with 'response', 'needs_more_info', and 'case_summary'
        """
        patient_input = input_data.get("patient_input", "")
        is_initial = input_data.get("is_initial", True)
        
        logger.info(f"{self.name} processing {'initial' if is_initial else 'follow-up'} input")
        
        if is_initial:
            # Initial greeting and intake
            prompt = PromptTemplates.format_intake_greeting(patient_input)
            self.conversation_history = [
                {"role": "user", "content": patient_input}
            ]
        else:
            # Follow-up questions
            conversation_str = self._format_conversation_history()
            prompt = PromptTemplates.format_intake_followup(
                patient_input=patient_input,
                conversation_history=conversation_str
            )
            self.conversation_history.append({
                "role": "user",
                "content": patient_input
            })
        
        # Generate response
        response = self._generate(prompt, temperature=0.7, max_length=1024)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Determine if we have enough information
        needs_more_info = self._check_needs_more_info(patient_input, response)
        
        # Generate case summary if we have enough info
        case_summary = ""
        if not needs_more_info:
            case_summary = self._generate_case_summary()
        
        return {
            "response": response,
            "needs_more_info": needs_more_info,
            "case_summary": case_summary,
            "conversation_history": self.conversation_history
        }
    
    def _format_conversation_history(self) -> str:
        """Format conversation history as a string."""
        history_parts = []
        for msg in self.conversation_history:
            role = msg["role"].upper()
            content = msg["content"]
            history_parts.append(f"{role}: {content}")
        return "\n\n".join(history_parts)
    
    def _check_needs_more_info(self, patient_input: str, response: str) -> bool:
        """
        Determine if more information is needed.
        
        Heuristic: If the response contains questions, we need more info.
        """
        # If the user's input already contains enough triage details, proceed
        user_text = self._get_user_history_text()
        if self._has_basic_info(user_text):
            return False

        question_indicators = ["?", "could you", "can you", "tell me more", "what about"]
        response_lower = response.lower()
        
        for indicator in question_indicators:
            if indicator in response_lower:
                return True
        
        # Also check conversation length - need at least basic info
        if len(self.conversation_history) < 3:
            return True
        
        return False

    def _get_user_history_text(self) -> str:
        """Combine all user messages into a single text block."""
        user_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
        return " ".join(user_messages)

    def _has_basic_info(self, text: str) -> bool:
        """Check if input text includes basic triage details."""
        text_lower = text.lower()

        onset_markers = [
            "started", "start", "began", "since", "for", "ago",
            "yesterday", "today", "hours", "hour", "days", "day",
            "weeks", "week", "months", "month"
        ]
        severity_markers = [
            "mild", "moderate", "severe", "worst", "intense", "scale", "/10"
        ]
        associated_markers = [
            "fever", "nausea", "vomit", "cough", "shortness of breath",
            "sore throat", "headache", "dizziness", "sweating", "chills"
        ]
        location_markers = [
            "chest", "abdomen", "stomach", "head", "arm", "leg",
            "throat", "back", "side"
        ]

        has_onset = any(marker in text_lower for marker in onset_markers)
        has_severity = any(marker in text_lower for marker in severity_markers)
        has_associated = any(marker in text_lower for marker in associated_markers)
        has_location = any(marker in text_lower for marker in location_markers)

        info_points = sum([has_onset, has_severity, has_associated, has_location])
        return info_points >= 2 or len(text_lower) > 140
    
    def _generate_case_summary(self) -> str:
        """Generate a structured case summary."""
        conversation_str = self._format_conversation_history()
        
        summary_prompt = f"""Based on the following conversation, create a concise medical case summary.

Conversation:
{conversation_str}

Provide a structured summary including:
1. Chief Complaint: Main symptom(s)
2. History of Present Illness: Onset, duration, characteristics, severity
3. Associated Symptoms: Other relevant symptoms
4. Relevant Medical History: Medications, conditions, allergies
5. Red Flag Assessment: Any concerning symptoms

Be concise and focus on medically relevant information."""
        
        summary = self._generate(summary_prompt, temperature=0.5, max_length=1024)
        
        logger.info(f"{self.name} generated case summary")
        return summary
    
    def reset(self) -> None:
        """Reset conversation history."""
        self.conversation_history = []
        logger.info(f"{self.name} conversation history reset")


__all__ = ["IntakeAgent"]
