"""
Urgency Classification Agent - Classifies case urgency.
"""
from typing import Dict, Any
import re
from src.agents.base_agent import BaseAgent
from src.models.prompt_templates import PromptTemplates
from config import TriageConfig
from src.utils.logger import logger


class UrgencyClassificationAgent(BaseAgent):
    """Agent responsible for classifying case urgency level."""
    
    def __init__(self):
        super().__init__(name="Urgency Classification Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify the urgency level of the case with severity-aware logic.
        
        Args:
            input_data: Dict with 'case_summary', 'symptom_analysis', and 'red_flags'
            
        Returns:
            Dict with 'urgency_level', 'reasoning', 'confidence', and 'time_sensitive'
        """
        case_summary = input_data.get("case_summary", "")
        symptom_analysis = input_data.get("symptom_analysis", "")
        red_flags = input_data.get("red_flags", [])
        
        logger.info(f"{self.name} classifying urgency")
        
        # Separate critical and warning flags with stricter severity checking
        critical_flags = [rf for rf in red_flags if isinstance(rf, dict) and 
                         rf.get("type") == "critical" and rf.get("severity") == "critical"]
        high_severity_flags = [rf for rf in red_flags if isinstance(rf, dict) and 
                              rf.get("severity") in ["high", "critical"]]
        warning_flags = [rf for rf in red_flags if isinstance(rf, dict) and 
                        rf.get("type") == "warning" and rf.get("severity") not in ["critical", "high"]]
        
        # Handle legacy format (list of strings)
        if red_flags and not isinstance(red_flags[0], dict):
            # Convert to new format for backward compatibility - but check severity
            critical_flags = [{"flag": flag, "severity": "critical", "type": "critical"} 
                            for flag in red_flags]
            warning_flags = []
        
        # If CRITICAL red flags with CRITICAL severity present, automatic emergency classification
        # Requires both critical type AND critical severity to auto-escalate
        if critical_flags:
            flag_names = [rf.get("flag", str(rf)) for rf in critical_flags]
            # Calculate confidence based on flag count and severity consistency
            confidence = "high" if len(critical_flags) >= 2 else "medium"
            
            logger.warning(f"{self.name} detected {len(critical_flags)} CRITICAL red flags with critical severity - auto-classifying as EMERGENCY: {flag_names}")
            return {
                "urgency_level": "EMERGENCY",
                "reasoning": f"CRITICAL RED FLAG SYMPTOMS DETECTED: {', '.join(flag_names)}. "
                           "Immediate medical attention required. Call 911 or go to ER immediately.",
                "confidence": confidence,
                "time_sensitive": True,
                "red_flags": red_flags
            }
        
        # If high severity flags but not critical type, don't auto-escalate to EMERGENCY
        # Let AI classification handle these with guidance
        if high_severity_flags and not critical_flags:
            logger.info(f"{self.name} detected {len(high_severity_flags)} high-severity flags but not critical type - will guide AI classification")
        
        # Calculate minimum suggested urgency based on warning flags
        suggested_min_urgency = self._calculate_min_urgency(warning_flags)
        
        # Generate urgency classification with AI
        prompt = PromptTemplates.format_urgency_classification(
            case_summary=case_summary,
            symptom_analysis=symptom_analysis,
            warning_flags=warning_flags,
            suggested_min_urgency=suggested_min_urgency
        )
        
        classification_response = self._generate(
            prompt,
            temperature=0.1,  # Very low temperature for more consistent classification
            max_length=1024
        )
        
        # Extract urgency level
        urgency_level = self._extract_urgency_level(classification_response)
        logger.error(f"DEBUG edge_case: After extraction: '{urgency_level}'")
        
        # Log the raw AI response for debugging if it's problematic
        if "unknown" in classification_response.lower() or urgency_level == "SEMI-URGENT":
            logger.debug(f"{self.name} AI response snippet: {classification_response[:300]}")
        
        # IMMEDIATE ENFORCEMENT: Block UNKNOWN right after extraction
        if urgency_level == "UNKNOWN" or urgency_level not in ["EMERGENCY", "URGENT", "SEMI-URGENT", "NON-URGENT"]:
            logger.warning(f"{self.name} IMMEDIATE ENFORCEMENT: Got invalid level '{urgency_level}' - defaulting to SEMI-URGENT")
            urgency_level = "SEMI-URGENT"
        logger.error(f"DEBUG edge_case: After immediate check: '{urgency_level}'")
        
        # ENFORCEMENT LAYER 0.5: Override SEMI-URGENT if clear URGENT indicators present
        if urgency_level == "SEMI-URGENT" and len(red_flags) >= 3:
            # Check if we have multiple high-severity warning flags suggesting URGENT
            high_sev_flags = [rf for rf in red_flags if isinstance(rf, dict) and rf.get("severity") in ["high", "critical"]]
            
            if len(high_sev_flags) >= 2:
                logger.warning(f"{self.name} ENFORCEMENT OVERRIDE: AI returned SEMI-URGENT but {len(high_sev_flags)} high-severity flags present - upgrading to URGENT")
                urgency_level = "URGENT"
            elif len(red_flags) >= 4:
                logger.warning(f"{self.name} ENFORCEMENT OVERRIDE: AI returned SEMI-URGENT but {len(red_flags)} warning flags present - upgrading to URGENT")
                urgency_level = "URGENT"
        
        # ENFORCEMENT LAYER 1: Block EMERGENCY without critical flags
        critical_flags_present = any(
            isinstance(rf, dict) and rf.get("severity") == "critical" and rf.get("type") == "critical"
            for rf in red_flags
        )
        
        if urgency_level == "EMERGENCY" and not critical_flags_present:
            logger.warning(f"{self.name} ENFORCEMENT: Blocking EMERGENCY classification - no critical flags detected")
            # Downgrade based on what flags we have
            high_flags = [rf for rf in red_flags if isinstance(rf, dict) and rf.get("severity") == "high"]
            if len(high_flags) >= 2 or len(red_flags) >= 3:
                urgency_level = "URGENT"
                logger.info(f"{self.name} ENFORCEMENT: Downgraded to URGENT (high severity flags present)")
            elif len(red_flags) >= 1:
                urgency_level = "SEMI-URGENT"
                logger.info(f"{self.name} ENFORCEMENT: Downgraded to SEMI-URGENT (warning flags present)")
            else:
                urgency_level = "SEMI-URGENT"
                logger.info(f"{self.name} ENFORCEMENT: Downgraded to SEMI-URGENT (no red flags)")
        
        # ENFORCEMENT LAYER 2: Block URGENT without sufficient severity flags
        if urgency_level == "URGENT":
            # URGENT requires at least 2 high-severity warning flags OR 3+ warning flags OR 1 critical flag
            high_severity_warning_flags = [rf for rf in red_flags if isinstance(rf, dict) and 
                                           rf.get("severity") in ["high", "critical"]]
            
            if len(critical_flags) == 0 and len(high_severity_warning_flags) < 2 and len(red_flags) < 3:
                logger.warning(f"{self.name} ENFORCEMENT: Downgrading URGENT to SEMI-URGENT - insufficient severity flags")
                logger.warning(f"  Critical: {len(critical_flags)}, High severity: {len(high_severity_warning_flags)}, Total: {len(red_flags)}")
                urgency_level = "SEMI-URGENT"
            else:
                logger.info(f"{self.name} ENFORCEMENT: URGENT allowed - sufficient flags (Critical: {len(critical_flags)}, High: {len(high_severity_warning_flags)}, Total: {len(red_flags)})")
        
        # ENFORCEMENT LAYER 2.5: Prevent over-classification of healing/minor issues (STRENGTHENED)
        case_lower = case_summary.lower()
        healing_indicators = ["healing well", "healing normally", "no redness", "no swelling", "no infection"]
        
        # If healing + no concerning signs → force NON-URGENT
        if any(indicator in case_lower for indicator in healing_indicators):
            no_concerning_signs = all(sign not in case_lower for sign in ["worse", "worsening", "spreading", "painful", "severe"])
            if len(red_flags) == 0 and no_concerning_signs:
                logger.info(f"{self.name} ENFORCEMENT: Detected healing indicators with no red flags or concerning signs - forcing NON-URGENT")
                urgency_level = "NON-URGENT"
        
        # ENFORCEMENT LAYER 2.6: Prevent over-classification of mild, stable symptoms (FINAL FIX)
        mild_indicators = ["mild", "slight", "minor", "occasional"]
        no_fever_indicators = ["no fever", "without fever", "no temperature"]
        persistent_indicators = ["week", "weeks", "days", "persistent", "ongoing", "several"]
        short_duration_indicators = ["yesterday", "today", "this morning", "just started"]
        
        # If explicitly mild + no fever + short/no persistence + no red flags → cap at NON-URGENT
        if len(red_flags) == 0:
            mild_count = sum(1 for ind in mild_indicators if ind in case_lower)
            no_fever_present = any(ind in case_lower for ind in no_fever_indicators)
            has_persistence = any(ind in case_lower for ind in persistent_indicators)
            is_short_duration = any(ind in case_lower for ind in short_duration_indicators)
            
            # Downgrade if: (mild + no fever) OR (mild + short duration) AND not persistent
            if not has_persistence:
                if (mild_count >= 1 and no_fever_present) or (mild_count >= 2) or (mild_count >= 1 and is_short_duration):
                    if urgency_level in ["URGENT", "SEMI-URGENT"]:
                        logger.info(f"{self.name} ENFORCEMENT: Mild + no fever/short duration detected - capping at NON-URGENT")
                        urgency_level = "NON-URGENT"
        
        # ENFORCEMENT LAYER 2.7: Prevent over-classification of resolving/occasional symptoms
        resolving_indicators = ["go away", "goes away", "resolves", "better", "improving"]
        occasional_indicators = ["occasional", "sometimes", "now and then"]
        
        # If occasional + resolving + no red flags → force NON-URGENT
        if len(red_flags) == 0:
            is_occasional = any(ind in case_lower for ind in occasional_indicators)
            is_resolving = any(ind in case_lower for ind in resolving_indicators)
            no_other_symptoms = "no other symptoms" in case_lower or "no other" in case_lower
            
            if (is_occasional and is_resolving) or (mild_count >= 1 and is_resolving and no_other_symptoms):
                if urgency_level in ["URGENT", "SEMI-URGENT"]:
                    logger.info(f"{self.name} ENFORCEMENT: Occasional/resolving symptoms detected - forcing NON-URGENT")
                    urgency_level = "NON-URGENT"
        
        # Apply minimum urgency constraint from warning flags
        if suggested_min_urgency:
            original_level = urgency_level
            urgency_level = self._apply_min_urgency(urgency_level, suggested_min_urgency)
            if urgency_level != original_level:
                logger.info(f"{self.name} upgraded urgency from {original_level} to {urgency_level} due to warning flags")
        
        # Handle invalid/unknown urgency levels
        if urgency_level not in ["EMERGENCY", "URGENT", "SEMI-URGENT", "NON-URGENT"]:
            logger.warning(f"{self.name} ENFORCEMENT: Invalid urgency level '{urgency_level}' - defaulting to SEMI-URGENT")
            urgency_level = "SEMI-URGENT"
        
        # Determine if time-sensitive
        time_sensitive = urgency_level in ["EMERGENCY", "URGENT"]
        
        # Extract confidence
        confidence = self._extract_confidence(classification_response)
        
        # Calculate confidence score based on multiple factors
        confidence_score = self._calculate_confidence_score(
            urgency_level, red_flags, case_summary, symptom_analysis
        )
        
        # Validate classification
        validation_result = self._validate_classification(
            urgency_level, red_flags, confidence_score
        )
        
        # ENFORCEMENT LAYER 3: Apply validation suggestions if confidence is low
        if validation_result.get("should_adjust") and validation_result.get("suggested_level"):
            # Only apply suggestion if confidence is low or validation is strong
            if confidence_score < 0.5:
                suggested_level = validation_result.get("suggested_level")
                logger.warning(f"{self.name} ENFORCEMENT: Applying validation suggestion - {urgency_level} → {suggested_level}")
                logger.warning(f"  Reason: {validation_result.get('reason')}")
                urgency_level = suggested_level
                confidence = "low"
            else:
                logger.warning(f"{self.name} validation suggests adjustment but confidence acceptable: {validation_result.get('reason')}")
        
        # FINAL UNKNOWN CHECK: Ensure no UNKNOWN slips through
        if urgency_level == "UNKNOWN":
            logger.error(f"{self.name} CRITICAL: UNKNOWN level detected after all enforcement - forcing SEMI-URGENT")
            urgency_level = "SEMI-URGENT"
        logger.error(f"DEBUG edge_case: After final check: '{urgency_level}'")
        
        logger.info(f"{self.name} FINAL classification: {urgency_level} (confidence: {confidence}, score: {confidence_score:.2f})")
        
        # ULTIMATE SAFETY CHECK: Right before return
        if urgency_level == "UNKNOWN":
            logger.error(f"{self.name} CRITICAL BUG: UNKNOWN at return - forcing SEMI-URGENT")
            urgency_level = "SEMI-URGENT"
        logger.error(f"DEBUG edge_case: Before return: '{urgency_level}'")
        
        # NUCLEAR OPTION: Check result dict before returning
        result = {
            "urgency_level": urgency_level,
            "reasoning": classification_response,
            "confidence": confidence,
            "confidence_score": confidence_score,
            "time_sensitive": time_sensitive,
            "red_flags": red_flags,
            "validation": validation_result
        }
        
        # Final validation of return value
        if result["urgency_level"] == "UNKNOWN":
            logger.error(f"{self.name} NUCLEAR FIX: UNKNOWN in result dict - forcing SEMI-URGENT")
            result["urgency_level"] = "SEMI-URGENT"
        
        return result
    
    def _calculate_min_urgency(self, warning_flags: list) -> str:
        """
        Calculate minimum urgency level based on warning flags with stricter thresholds.
        
        Args:
            warning_flags: List of warning flag dicts
            
        Returns:
            Minimum urgency level string or empty string
        """
        if not warning_flags:
            return ""
        
        # Count severity levels with weighting
        high_severity_count = sum(1 for rf in warning_flags 
                                 if rf.get("severity") == "high")
        moderate_severity_count = sum(1 for rf in warning_flags 
                                     if rf.get("severity") == "moderate")
        low_severity_count = sum(1 for rf in warning_flags 
                                if rf.get("severity") == "low")
        
        # More conservative thresholds - require stronger evidence
        # URGENT: need 3+ high severity flags
        if high_severity_count >= 3:
            return "URGENT"
        # SEMI-URGENT: need 2 high OR 1 high + 3 moderate OR 4+ moderate
        elif high_severity_count >= 2 or (high_severity_count >= 1 and moderate_severity_count >= 3) or moderate_severity_count >= 4:
            return "SEMI-URGENT"
        # Otherwise, let AI decide (no minimum constraint)
        else:
            return ""
    
    def _apply_min_urgency(self, ai_urgency: str, min_urgency: str) -> str:
        """
        Apply minimum urgency constraint to AI classification.
        
        Args:
            ai_urgency: AI-suggested urgency level
            min_urgency: Minimum urgency level from warning flags
            
        Returns:
            Final urgency level
        """
        urgency_order = ["NON-URGENT", "SEMI-URGENT", "URGENT", "EMERGENCY"]
        
        try:
            ai_index = urgency_order.index(ai_urgency)
            min_index = urgency_order.index(min_urgency)
            
            # Return the higher urgency level
            return urgency_order[max(ai_index, min_index)]
        except ValueError:
            # If either urgency level is invalid, return AI urgency
            return ai_urgency
    
    def _extract_urgency_level(self, response: str) -> str:
        """
        Extract urgency level from classification response with robust fallback handling.
        Always returns a valid urgency level, never UNKNOWN or empty.
        """
        if not response or not response.strip():
            logger.warning(f"{self.name} received empty response - defaulting to SEMI-URGENT")
            return "SEMI-URGENT"
        
        response_upper = response.upper()
        response_lower = response.lower()
        
        # Check for vague/uncertain responses - force SEMI-URGENT for vague symptoms
        vague_phrases = ["not sure", "unclear", "vague", "cannot determine", "insufficient", 
                        "hard to classify", "difficult to assess", "unable to determine"]
        if any(phrase in response_lower for phrase in vague_phrases):
            logger.warning(f"{self.name} Response indicates uncertainty - defaulting to SEMI-URGENT")
            return "SEMI-URGENT"
        
        # Check for invalid responses first
        if "UNKNOWN" in response_upper or "UNCLEAR" in response_upper or "UNSURE" in response_upper:
            logger.warning(f"{self.name} received UNKNOWN/UNCLEAR response - defaulting to SEMI-URGENT")
            return "SEMI-URGENT"
        
        # Prefer exact labels and avoid substring collisions (URGENT in SEMI-URGENT)
        patterns = [
            ("SEMI-URGENT", r"\bSEMI[- ]?URGENT\b"),
            ("NON-URGENT", r"\bNON[- ]?URGENT\b"),
            ("EMERGENCY", r"\bEMERGENCY\b"),
            ("URGENT", r"\bURGENT\b"),
        ]
        for label, pattern in patterns:
            if re.search(pattern, response_upper):
                return label
        
        # Additional fallback checks for common variations
        if "CRITICAL" in response_upper or "LIFE THREATENING" in response_upper:
            logger.warning(f"{self.name} found 'critical/life-threatening' but no urgency label - defaulting to URGENT")
            return "URGENT"
        
        if "MILD" in response_upper or "MINOR" in response_upper or "LOW PRIORITY" in response_upper:
            logger.warning(f"{self.name} found 'mild/minor' but no urgency label - defaulting to NON-URGENT")
            return "NON-URGENT"
        
        # Default to SEMI-URGENT if unclear (safe middle ground)
        logger.warning(f"{self.name} could not determine urgency from response - defaulting to SEMI-URGENT")
        logger.debug(f"Response was: {response[:200]}")
        return "SEMI-URGENT"
    
    def _extract_confidence(self, response: str) -> str:
        """Extract confidence level from response."""
        response_lower = response.lower()
        
        if "high confidence" in response_lower or "clearly" in response_lower:
            return "high"
        elif "low confidence" in response_lower or "unclear" in response_lower:
            return "low"
        else:
            return "medium"
    
    def _calculate_confidence_score(
        self, 
        urgency_level: str, 
        red_flags: list, 
        case_summary: str,
        symptom_analysis: str
    ) -> float:
        """
        Calculate a numerical confidence score (0-1) based on multiple factors.
        
        Args:
            urgency_level: Classified urgency level
            red_flags: List of detected red flags
            case_summary: Patient case summary
            symptom_analysis: Symptom analysis text
            
        Returns:
            Float between 0 and 1 indicating confidence
        """
        score = 0.5  # Start at neutral
        
        # Factor 1: Red flag consistency with urgency level
        if urgency_level == "EMERGENCY":
            # EMERGENCY should have critical red flags
            critical_flags = [rf for rf in red_flags if isinstance(rf, dict) and 
                            rf.get("severity") == "critical"]
            if len(critical_flags) >= 2:
                score += 0.3
            elif len(critical_flags) == 1:
                score += 0.15
            else:
                score -= 0.2  # EMERGENCY without critical flags is suspicious
        
        elif urgency_level == "URGENT":
            # URGENT should have high severity flags or multiple moderate
            high_flags = [rf for rf in red_flags if isinstance(rf, dict) and 
                         rf.get("severity") in ["high", "critical"]]
            if len(high_flags) >= 1:
                score += 0.2
            elif len(red_flags) >= 2:
                score += 0.1
        
        elif urgency_level == "SEMI-URGENT":
            # SEMI-URGENT should have moderate flags or persistent symptoms
            if len(red_flags) >= 1:
                score += 0.1
            # Check for persistence indicators
            if any(word in case_summary.lower() for word in ["days", "week", "persistent", "ongoing"]):
                score += 0.1
        
        elif urgency_level == "NON-URGENT":
            # NON-URGENT should have no or low severity flags
            if not red_flags:
                score += 0.2
            elif all(isinstance(rf, dict) and rf.get("severity") == "low" for rf in red_flags):
                score += 0.15
            else:
                score -= 0.1  # NON-URGENT with concerning flags is suspicious
        
        # Factor 2: Symptom clarity and completeness
        case_lower = case_summary.lower()
        clarity_indicators = ["onset", "duration", "severity", "pain", "fever", "started"]
        clarity_count = sum(1 for indicator in clarity_indicators if indicator in case_lower)
        score += min(0.15, clarity_count * 0.03)
        
        # Factor 3: Red flag count consistency
        if urgency_level in ["EMERGENCY", "URGENT"] and len(red_flags) == 0:
            score -= 0.15  # High urgency without flags is questionable
        elif urgency_level == "NON-URGENT" and len(red_flags) > 2:
            score -= 0.15  # Low urgency with many flags is questionable
        
        # Clamp score between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _validate_classification(
        self, 
        urgency_level: str, 
        red_flags: list,
        confidence_score: float
    ) -> dict:
        """
        Validate the classification against red flags and confidence.
        
        Args:
            urgency_level: Classified urgency level
            red_flags: List of detected red flags
            confidence_score: Calculated confidence score
            
        Returns:
            Dict with validation results and suggestions
        """
        validation = {
            "is_valid": True,
            "should_adjust": False,
            "reason": "",
            "suggested_level": None
        }
        
        # Check for mismatches between urgency and red flags
        critical_flags = [rf for rf in red_flags if isinstance(rf, dict) and 
                         rf.get("severity") == "critical"]
        high_flags = [rf for rf in red_flags if isinstance(rf, dict) and 
                     rf.get("severity") == "high"]
        
        # Validation rule 1: EMERGENCY should have critical flags
        if urgency_level == "EMERGENCY" and not critical_flags:
            validation["should_adjust"] = True
            validation["reason"] = "EMERGENCY classification without critical severity flags"
            if len(high_flags) >= 2:
                validation["suggested_level"] = "URGENT"
            elif len(red_flags) >= 1:
                validation["suggested_level"] = "SEMI-URGENT"
        
        # Validation rule 2: NON-URGENT shouldn't have high/critical flags
        if urgency_level == "NON-URGENT" and (critical_flags or high_flags):
            validation["should_adjust"] = True
            validation["reason"] = "NON-URGENT classification with high/critical severity flags"
            if critical_flags:
                validation["suggested_level"] = "EMERGENCY"
            elif len(high_flags) >= 2:
                validation["suggested_level"] = "URGENT"
            else:
                validation["suggested_level"] = "SEMI-URGENT"
        
        # Validation rule 3: Low confidence score suggests review
        if confidence_score < 0.4:
            validation["should_adjust"] = True
            validation["reason"] = f"Low confidence score ({confidence_score:.2f})"
        
        # Validation rule 4: URGENT with no flags is questionable
        if urgency_level == "URGENT" and len(red_flags) == 0:
            validation["should_adjust"] = True
            validation["reason"] = "URGENT classification without any red flags"
            validation["suggested_level"] = "SEMI-URGENT"
        
        # CRITICAL: Ensure validation never suggests UNKNOWN
        if validation.get("suggested_level") == "UNKNOWN":
            validation["suggested_level"] = "SEMI-URGENT"
            logger.warning(f"{self.name} Validation suggested UNKNOWN - changing to SEMI-URGENT")
        
        return validation


__all__ = ["UrgencyClassificationAgent"]
