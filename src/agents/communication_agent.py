"""
Communication Agent - Creates patient-friendly triage reports.
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.models.prompt_templates import PromptTemplates
from src.utils.logger import logger


class CommunicationAgent(BaseAgent):
    """Agent responsible for creating clear, patient-friendly triage reports."""
    
    def __init__(self):
        super().__init__(name="Communication Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate patient-friendly triage report.
        
        Args:
            input_data: Dict with all triage information including:
                - case_summary
                - urgency_level
                - care_recommendation (full dict)
                - symptom_analysis
                - red_flags
            
        Returns:
            Dict with 'report', 'summary', and 'formatted_report'
        """
        case_summary = input_data.get("case_summary", "")
        urgency_level = input_data.get("urgency_level", "")
        care_info = input_data.get("care_recommendation", {})
        red_flags = input_data.get("red_flags", [])
        
        logger.info(f"{self.name} generating patient report")
        
        # Prepare care recommendation text
        care_recommendation_text = self._format_care_info(care_info)
        
        # Generate patient-friendly report
        prompt = PromptTemplates.format_communication_report(
            case_summary=case_summary,
            urgency_level=urgency_level,
            care_recommendation=care_recommendation_text
        )
        
        report = self._generate(prompt, temperature=0.6, max_length=2048)
        
        # Create structured formatted report
        formatted_report = self._create_formatted_report(
            report=report,
            urgency_level=urgency_level,
            care_info=care_info,
            red_flags=red_flags
        )
        
        # Create brief summary
        summary = self._create_summary(urgency_level, care_info)
        
        logger.info(f"{self.name} completed patient report")
        
        return {
            "report": report,
            "summary": summary,
            "formatted_report": formatted_report
        }
    
    def _format_care_info(self, care_info: Dict[str, Any]) -> str:
        """Format care information into text."""
        parts = []
        
        if "care_setting" in care_info:
            parts.append(f"Care Setting: {care_info['care_setting']}")
        
        if "timeline" in care_info:
            parts.append(f"Timeline: {care_info['timeline']}")
        
        if "next_steps" in care_info and care_info["next_steps"]:
            parts.append("Next Steps:")
            for step in care_info["next_steps"]:
                parts.append(f"  - {step}")
        
        if "self_care" in care_info and care_info["self_care"]:
            parts.append("Self-Care Measures:")
            for measure in care_info["self_care"]:
                parts.append(f"  - {measure}")
        
        return "\n".join(parts)
    
    def _create_formatted_report(
        self,
        report: str,
        urgency_level: str,
        care_info: Dict[str, Any],
        red_flags: list
    ) -> str:
        """Create a well-formatted report with sections."""
        sections = []
        
        # Header
        sections.append("=" * 60)
        sections.append("MEDICAL TRIAGE REPORT")
        sections.append("=" * 60)
        sections.append("")
        
        # Urgency Alert
        if urgency_level == "EMERGENCY" or red_flags:
            sections.append("⚠️  URGENT MEDICAL ATTENTION REQUIRED  ⚠️")
            if red_flags:
                # Handle both dict and string formats
                flag_names = []
                for rf in red_flags:
                    if isinstance(rf, dict):
                        flag_names.append(rf.get("flag", str(rf)))
                    else:
                        flag_names.append(str(rf))
                sections.append(f"Red Flag Symptoms: {', '.join(flag_names)}")
            sections.append("")
        
        # Urgency Level
        urgency_emoji = {
            "EMERGENCY": "🚨",
            "URGENT": "⚡",
            "SEMI-URGENT": "⚠️",
            "NON-URGENT": "ℹ️"
        }
        emoji = urgency_emoji.get(urgency_level, "ℹ️")
        sections.append(f"{emoji} URGENCY LEVEL: {urgency_level}")
        sections.append("")
        
        # Main Report
        sections.append("ASSESSMENT:")
        sections.append("-" * 60)
        sections.append(report)
        sections.append("")
        
        # Care Recommendations
        sections.append("RECOMMENDED CARE:")
        sections.append("-" * 60)
        sections.append(f"Care Setting: {care_info.get('care_setting', 'N/A')}")
        sections.append(f"Timeline: {care_info.get('timeline', 'N/A')}")
        sections.append("")
        
        if care_info.get("next_steps"):
            sections.append("Next Steps:")
            for i, step in enumerate(care_info["next_steps"], 1):
                sections.append(f"  {i}. {step}")
            sections.append("")
        
        if care_info.get("self_care"):
            sections.append("Self-Care Measures:")
            for measure in care_info["self_care"]:
                sections.append(f"  • {measure}")
            sections.append("")
        
        if care_info.get("preparation"):
            sections.append("What to Bring/Prepare:")
            for item in care_info["preparation"]:
                sections.append(f"  • {item}")
            sections.append("")
        
        # Disclaimer
        sections.append("=" * 60)
        sections.append("IMPORTANT DISCLAIMER:")
        sections.append("=" * 60)
        sections.append("This is an AI-assisted triage tool for informational purposes only.")
        sections.append("It does NOT replace professional medical advice, diagnosis, or treatment.")
        sections.append("Always seek the advice of qualified healthcare providers.")
        sections.append("For life-threatening emergencies, call 911 immediately.")
        sections.append("=" * 60)
        
        return "\n".join(sections)
    
    def _create_summary(self, urgency_level: str, care_info: Dict[str, Any]) -> str:
        """Create a brief summary of the triage result."""
        care_setting = care_info.get("care_setting", "medical care")
        timeline = care_info.get("timeline", "")
        
        summary = f"Urgency: {urgency_level}. "
        summary += f"Recommended: {care_setting}. "
        if timeline:
            summary += f"{timeline}."
        
        return summary


__all__ = ["CommunicationAgent"]
