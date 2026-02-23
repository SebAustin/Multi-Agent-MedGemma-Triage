"""
Care Recommendation Agent - Recommends appropriate care settings.
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.models.prompt_templates import PromptTemplates
from config import TriageConfig
from src.utils.logger import logger


class CareRecommendationAgent(BaseAgent):
    """Agent responsible for recommending appropriate care settings and next steps."""
    
    def __init__(self):
        super().__init__(name="Care Recommendation Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend appropriate care setting and next steps.
        
        Args:
            input_data: Dict with 'case_summary', 'urgency_level', and 'urgency_reasoning'
            
        Returns:
            Dict with 'care_setting', 'timeline', 'next_steps', 'self_care', 'preparation'
        """
        case_summary = input_data.get("case_summary", "")
        urgency_level = input_data.get("urgency_level", "SEMI-URGENT")
        urgency_reasoning = input_data.get("urgency_reasoning", "")
        
        logger.info(f"{self.name} generating care recommendations for {urgency_level}")
        
        # Generate care recommendations
        prompt = PromptTemplates.format_care_recommendation(
            case_summary=case_summary,
            urgency_level=urgency_level,
            urgency_reasoning=urgency_reasoning
        )
        
        recommendations = self._generate(prompt, temperature=0.5, max_length=1536)
        
        # Extract structured components
        care_setting = self._extract_care_setting(recommendations, urgency_level)
        timeline = self._extract_timeline(recommendations, urgency_level)
        next_steps = self._extract_next_steps(recommendations)
        self_care = self._extract_self_care(recommendations)
        preparation = self._extract_preparation(recommendations)
        
        logger.info(f"{self.name} recommended: {care_setting}")
        
        return {
            "care_setting": care_setting,
            "timeline": timeline,
            "next_steps": next_steps,
            "self_care": self_care,
            "preparation": preparation,
            "full_recommendations": recommendations
        }
    
    def _extract_care_setting(self, recommendations: str, urgency_level: str) -> str:
        """Extract recommended care setting."""
        rec_lower = recommendations.lower()
        
        # Check for each care setting
        if "emergency" in rec_lower or "er" in rec_lower or urgency_level == "EMERGENCY":
            return "Emergency Department (ER)"
        elif "urgent care" in rec_lower or urgency_level == "URGENT":
            return "Urgent Care Center"
        elif "primary care" in rec_lower or "pcp" in rec_lower:
            return "Primary Care Physician"
        elif "telemedicine" in rec_lower or "virtual" in rec_lower:
            return "Telemedicine Consultation"
        elif "self-care" in rec_lower or "home" in rec_lower:
            return "Self-Care at Home"
        else:
            # Default based on urgency
            urgency_to_care = {
                "EMERGENCY": "Emergency Department (ER)",
                "URGENT": "Urgent Care Center",
                "SEMI-URGENT": "Primary Care Physician",
                "NON-URGENT": "Telemedicine Consultation"
            }
            return urgency_to_care.get(urgency_level, "Primary Care Physician")
    
    def _extract_timeline(self, recommendations: str, urgency_level: str) -> str:
        """Extract timeline for seeking care."""
        rec_lower = recommendations.lower()
        
        # Look for timeline indicators
        if "immediately" in rec_lower or "now" in rec_lower or "911" in rec_lower:
            return "Immediately - Call 911 or go to ER now"
        elif "today" in rec_lower or "within hours" in rec_lower:
            return "Today - Seek care within the next few hours"
        elif "1-2 days" in rec_lower or "tomorrow" in rec_lower:
            return "Within 1-2 days - Schedule appointment soon"
        elif "week" in rec_lower:
            return "Within a week - Schedule routine appointment"
        else:
            # Default based on urgency
            urgency_to_timeline = {
                "EMERGENCY": "Immediately - Call 911 or go to ER now",
                "URGENT": "Today - Seek care within the next few hours",
                "SEMI-URGENT": "Within 1-2 days - Schedule appointment soon",
                "NON-URGENT": "Within a week - Schedule routine appointment"
            }
            return urgency_to_timeline.get(urgency_level, "Within 1-2 days")
    
    def _extract_next_steps(self, recommendations: str) -> list[str]:
        """Extract next steps from recommendations."""
        steps = []
        lines = recommendations.split("\n")
        
        in_next_steps = False
        numbered_prefixes = [f"{i}." for i in range(1, 10)]
        bullet_prefixes = ["- ", "* ", "• "]
        line_prefixes = bullet_prefixes + numbered_prefixes
        for line in lines:
            line_lower = line.lower()
            
            if "next step" in line_lower:
                in_next_steps = True
                continue
            
            if in_next_steps and any(keyword in line_lower for keyword in 
                                    ["self-care", "preparation", "warning"]):
                in_next_steps = False
            
            if in_next_steps:
                line = line.strip()
                if any(line.startswith(prefix) for prefix in line_prefixes):
                    step = line.lstrip("- *•0123456789. ").strip()
                    if step and len(step) < 300:
                        steps.append(step)
        
        return steps[:10]
    
    def _extract_self_care(self, recommendations: str) -> list[str]:
        """Extract self-care measures from recommendations."""
        measures = []
        lines = recommendations.split("\n")
        
        in_self_care = False
        numbered_prefixes = [f"{i}." for i in range(1, 10)]
        bullet_prefixes = ["- ", "* ", "• "]
        line_prefixes = bullet_prefixes + numbered_prefixes
        for line in lines:
            line_lower = line.lower()
            
            if "self-care" in line_lower or "self care" in line_lower:
                in_self_care = True
                continue
            
            if in_self_care and any(keyword in line_lower for keyword in 
                                   ["preparation", "warning", "bring"]):
                in_self_care = False
            
            if in_self_care:
                line = line.strip()
                if any(line.startswith(prefix) for prefix in line_prefixes):
                    measure = line.lstrip("- *•0123456789. ").strip()
                    if measure and len(measure) < 300:
                        measures.append(measure)
        
        return measures[:10]
    
    def _extract_preparation(self, recommendations: str) -> list[str]:
        """Extract preparation items from recommendations."""
        items = []
        lines = recommendations.split("\n")
        
        in_preparation = False
        numbered_prefixes = [f"{i}." for i in range(1, 10)]
        bullet_prefixes = ["- ", "* ", "• "]
        line_prefixes = bullet_prefixes + numbered_prefixes
        for line in lines:
            line_lower = line.lower()
            
            if "bring" in line_lower or "prepare" in line_lower or "what to" in line_lower:
                in_preparation = True
                continue
            
            if in_preparation and any(keyword in line_lower for keyword in 
                                     ["warning", "note", "disclaimer"]):
                in_preparation = False
            
            if in_preparation:
                line = line.strip()
                if any(line.startswith(prefix) for prefix in line_prefixes):
                    item = line.lstrip("- *•0123456789. ").strip()
                    if item and len(item) < 300:
                        items.append(item)
        
        return items[:10]


__all__ = ["CareRecommendationAgent"]
