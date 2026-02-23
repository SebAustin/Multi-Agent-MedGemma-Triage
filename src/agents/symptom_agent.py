"""
Symptom Assessment Agent - Analyzes patient symptoms.
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.models.prompt_templates import PromptTemplates
from src.utils.logger import logger


class SymptomAssessmentAgent(BaseAgent):
    """Agent responsible for analyzing and assessing patient symptoms."""
    
    def __init__(self):
        super().__init__(name="Symptom Assessment Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patient symptoms.
        
        Args:
            input_data: Dict with 'case_summary' and optionally 'original_input'
            
        Returns:
            Dict with 'symptom_analysis', 'primary_symptoms', 
            'differential_diagnosis', and 'red_flags'
        """
        case_summary = input_data.get("case_summary", "")
        # Use original_input for red flag checking to avoid false positives from AI text
        original_input = input_data.get("original_input", case_summary)
        
        logger.info(f"{self.name} analyzing symptoms")
        
        # Generate symptom analysis with lower temperature for more focused analysis
        prompt = PromptTemplates.format_symptom_assessment(case_summary)
        analysis = self._generate(prompt, temperature=0.4, max_length=1536)
        
        # Extract key components
        primary_symptoms = self._extract_primary_symptoms(analysis)
        differential_diagnosis = self._extract_differential_diagnosis(analysis)
        # CRITICAL: Use original_input for red flag detection, NOT case_summary or analysis
        red_flags = self._check_red_flags(original_input)
        
        logger.info(f"{self.name} identified {len(primary_symptoms)} primary symptoms")
        if red_flags:
            logger.warning(f"{self.name} detected red flags: {red_flags}")
        
        return {
            "symptom_analysis": analysis,
            "primary_symptoms": primary_symptoms,
            "differential_diagnosis": differential_diagnosis,
            "red_flags": red_flags
        }
    
    def _extract_primary_symptoms(self, analysis: str) -> list[str]:
        """Extract primary symptoms from analysis."""
        # Simple extraction - look for numbered lists or bullet points
        symptoms = []
        lines = analysis.split("\n")
        
        for line in lines:
            line = line.strip()
            # Look for lines that appear to be symptoms
            if any(line.startswith(prefix) for prefix in ["- ", "* ", "• "]):
                symptom = line.lstrip("- *•").strip()
                if symptom and len(symptom) < 200:
                    symptoms.append(symptom)
            elif line and line[0].isdigit() and "." in line:
                parts = line.split(".", 1)
                if len(parts) > 1:
                    symptom = parts[1].strip()
                    if symptom and len(symptom) < 200:
                        symptoms.append(symptom)
        
        return symptoms[:10]  # Limit to top 10
    
    def _extract_differential_diagnosis(self, analysis: str) -> list[str]:
        """Extract potential diagnoses from analysis."""
        # Look for diagnosis section
        diagnoses = []
        lines = analysis.split("\n")
        
        in_diagnosis_section = False
        for line in lines:
            line_lower = line.lower()
            
            # Check if entering diagnosis section
            if any(keyword in line_lower for keyword in 
                   ["differential", "diagnosis", "potential condition", "possible condition"]):
                in_diagnosis_section = True
                continue
            
            # Check if leaving diagnosis section
            if in_diagnosis_section and any(keyword in line_lower for keyword in 
                                           ["red flag", "follow-up", "recommendation"]):
                in_diagnosis_section = False
            
            # Extract diagnosis items
            if in_diagnosis_section:
                line = line.strip()
                if any(line.startswith(prefix) for prefix in ["- ", "* ", "• "]):
                    diagnosis = line.lstrip("- *•").strip()
                    if diagnosis and len(diagnosis) < 200:
                        diagnoses.append(diagnosis)
                elif line and line[0].isdigit() and "." in line:
                    parts = line.split(".", 1)
                    if len(parts) > 1:
                        diagnosis = parts[1].strip()
                        if diagnosis and len(diagnosis) < 200:
                            diagnoses.append(diagnosis)
        
        return diagnoses[:5]  # Limit to top 5
    
    def _check_red_flags(self, patient_input: str) -> list[Dict[str, Any]]:
        """
        Check for red flag symptoms with severity assessment.
        
        CRITICAL: Only checks the PATIENT'S original input for red flags,
        NOT AI-generated analysis which may contain false positive matches.
        
        Args:
            patient_input: The patient's original symptom description (NOT AI analysis)
        
        Returns:
            List of dicts with 'flag', 'severity', 'context', and 'type' keys
        """
        # Use dedicated red flag detection prompt - only on patient's actual input
        red_flag_prompt = PromptTemplates.format_red_flag_check(patient_input)
        red_flag_response = self._generate(
            red_flag_prompt,
            temperature=0.1,  # Very low temperature for safety-critical detection
            max_length=512
        )
        
        # Extract red flags with severity
        red_flags = []
        response_lower = red_flag_response.lower()
        patient_input_lower = patient_input.lower()

        # If model indicates no red flags, return empty
        if "no" in response_lower and "yes" not in response_lower and "red flag" not in response_lower:
            return red_flags
        
        # Check if red flags are present
        if "yes" in response_lower or "red flag" in response_lower:
            from config import TriageConfig
            
            # Check critical red flags first - ONLY in patient's actual input
            for flag in TriageConfig.CRITICAL_RED_FLAGS:
                flag_lower = flag.lower()
                if self._flag_mentioned(flag_lower, patient_input_lower):
                    severity = self._assess_severity(flag, patient_input)
                    context = self._extract_context(flag, patient_input)
                    red_flags.append({
                        "flag": flag,
                        "severity": severity,
                        "context": context,
                        "type": "critical"
                    })
            
            # Check warning flags - ONLY in patient's actual input
            for flag in TriageConfig.WARNING_FLAGS:
                flag_lower = flag.lower()
                # Skip if already detected as critical
                if any(rf["flag"].lower() in flag_lower or flag_lower in rf["flag"].lower() 
                       for rf in red_flags):
                    continue
                    
                if self._flag_mentioned(flag_lower, patient_input_lower):
                    severity = self._assess_severity(flag, patient_input)
                    context = self._extract_context(flag, patient_input)
                    red_flags.append({
                        "flag": flag,
                        "severity": severity,
                        "context": context,
                        "type": "warning"
                    })
        
        return red_flags
    
    def _assess_severity(self, flag: str, text: str) -> str:
        """
        Assess the severity level of a red flag based on context with stricter thresholds.
        
        Returns:
            'critical', 'high', 'moderate', or 'low'
        """
        import re
        from config import TriageConfig
        
        text_lower = text.lower()
        
        # Extract context around the flag (within 50 chars)
        context = self._extract_context(flag, text, window=50).lower()
        
        # Check for negation in context - if negated, default to low
        negation_words = ['no', 'not', 'without', 'denies', 'deny', 'absent']
        if any(neg in context for neg in negation_words):
            return "low"
        
        # Special case: High fever (103°F+) is automatically high severity
        if "fever" in flag.lower():
            if any(indicator in text_lower for indicator in ["103", "104", "105", "over 103", "above 103"]):
                # Check for compound symptoms that elevate severity
                compound_indicators = ["can't keep", "cannot keep", "vomiting", "severe", "days"]
                if sum(1 for ind in compound_indicators if ind in text_lower) >= 2:
                    return "high"
                return "high"
        
        # Special case: Injury with multiple concerning features
        if any(word in flag.lower() for word in ["swollen", "purple", "walk", "weight"]):
            injury_severity_count = 0
            if "extremely" in text_lower or "extreme" in text_lower:
                injury_severity_count += 2
            if "purple" in text_lower or "discolor" in text_lower:
                injury_severity_count += 2
            if "can't" in text_lower or "cannot" in text_lower:
                injury_severity_count += 2
            if "worse" in text_lower or "worsening" in text_lower:
                injury_severity_count += 1
            if "swollen" in text_lower:
                injury_severity_count += 1
            
            if injury_severity_count >= 4:
                return "high"
            elif injury_severity_count >= 2:
                return "moderate"
        
        # Count severity keywords with proximity weighting
        # Keywords closer to the flag get more weight
        critical_count = 0
        high_count = 0
        moderate_count = 0
        low_count = 0
        
        for keyword in TriageConfig.SEVERITY_KEYWORDS["critical"]:
            if keyword in context:  # In close context (high weight)
                critical_count += 2
            elif keyword in text_lower:  # In full text (lower weight)
                critical_count += 1
                
        for keyword in TriageConfig.SEVERITY_KEYWORDS["high"]:
            if keyword in context:
                high_count += 2
            elif keyword in text_lower:
                high_count += 1
                
        for keyword in TriageConfig.SEVERITY_KEYWORDS["moderate"]:
            if keyword in context:
                moderate_count += 2
            elif keyword in text_lower:
                moderate_count += 1
                
        for keyword in TriageConfig.SEVERITY_KEYWORDS["low"]:
            if keyword in context:
                low_count += 2
            elif keyword in text_lower:
                low_count += 1
        
        # More conservative thresholds - require stronger evidence
        # Critical: need 3+ critical keywords OR 2 critical + 2 high
        if critical_count >= 3 or (critical_count >= 2 and high_count >= 2):
            return "critical"
        # High: need 2+ critical OR 1 critical + 3 high OR 4+ high
        elif critical_count >= 2 or (critical_count >= 1 and high_count >= 3) or high_count >= 4:
            return "high"
        # Moderate: need 1 critical OR 2+ high OR 3+ moderate
        elif critical_count >= 1 or high_count >= 2 or moderate_count >= 3:
            return "moderate"
        # Low: explicit low indicators OR not enough evidence
        elif low_count >= 2:
            return "low"
        else:
            # Default to low instead of moderate (more conservative)
            return "low"
    
    def _extract_context(self, flag: str, text: str, window: int = 100) -> str:
        """
        Extract surrounding context for a red flag mention.
        Enhanced to check for negation and temporal markers.
        """
        import re
        
        text_lower = text.lower()
        flag_lower = flag.lower()
        
        # Find the position of the flag using regex for word boundaries
        pattern = re.escape(flag_lower)
        match = re.search(pattern, text_lower)
        
        if not match:
            # Try finding individual words from the flag
            words = flag_lower.split()
            for word in words:
                if len(word) > 3:  # Only search for meaningful words
                    match = re.search(r'\b' + re.escape(word) + r'\b', text_lower)
                    if match:
                        break
        
        if not match:
            return ""
        
        pos = match.start()
        
        # Extract context window
        start = max(0, pos - window)
        end = min(len(text), pos + len(flag) + window)
        context = text[start:end].strip()
        
        # Check for negation markers in context
        negation_patterns = [
            r'\bno\b', r'\bnot\b', r'\bwithout\b', 
            r'\bdeny\b', r'\bdenies\b', r'\babsent\b',
            r'\bnever\b', r'\bneither\b'
        ]
        
        has_negation = any(re.search(pattern, context, re.IGNORECASE) for pattern in negation_patterns)
        
        # Check for past/hypothetical markers that reduce urgency
        temporal_patterns = [
            r'\bhistory of\b', r'\bpreviously\b', r'\bpast\b',
            r'\bused to\b', r'\bif i\b', r'\bwhat if\b'
        ]
        
        has_temporal = any(re.search(pattern, context, re.IGNORECASE) for pattern in temporal_patterns)
        
        # Add markers to context for severity assessment
        if has_negation:
            context = "[NEGATED] " + context
        if has_temporal:
            context = "[HISTORICAL] " + context
        
        return context[:250]  # Slightly increased limit for markers

    def _flag_mentioned(self, flag: str, text: str) -> bool:
        """
        Check if a specific red flag is mentioned in text with stricter matching.
        Uses phrase-based matching and checks for negation to reduce false positives.
        """
        import re
        
        # First check for negation - if symptom is negated, don't flag it
        negation_patterns = [
            r'\bno\s+(?:\w+\s+){0,3}' + re.escape(flag),
            r'\bnot\s+(?:\w+\s+){0,3}' + re.escape(flag),
            r'\bwithout\s+(?:\w+\s+){0,3}' + re.escape(flag),
            r'\bdeny\s+(?:\w+\s+){0,3}' + re.escape(flag),
            r'\bdenies\s+(?:\w+\s+){0,3}' + re.escape(flag),
        ]
        
        for pattern in negation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False  # Negated, don't flag
        
        # Enhanced synonyms with phrase-based matching
        synonyms = {
            "severe allergic reaction": ["anaphylaxis", "severe allergic"],
            "anaphylaxis": ["severe allergic reaction", "throat swelling with difficulty breathing"],
            "stroke symptoms": ["face drooping", "facial droop", "arm weakness", "one sided weakness"],
            "face drooping": ["facial droop", "face sagging", "one side of face"],
            "arm weakness": ["cannot move arm", "arm paralysis", "arm won't move"],
            "speech difficulty": ["cannot speak", "slurred speech", "trouble speaking", "speech problems"],
            "altered consciousness": ["unresponsive", "unconscious", "not responding", "confused and disoriented"],
            "unresponsive": ["not responding", "unconscious", "won't wake"],
            "severe bleeding": ["hemorrhage", "bleeding heavily", "won't stop bleeding", "bleeding profusely"],
            "hemorrhage": ["severe bleeding", "bleeding heavily", "massive bleeding"],
            "severe chest pain": ["crushing chest pain", "severe chest pressure", "intense chest pain"],
            "crushing chest pressure": ["severe chest pain", "crushing pain in chest"],
            "chest pain radiating": ["pain radiating to arm", "pain spreading to", "radiating down arm"],
            "severe difficulty breathing": ["cannot breathe", "can't breathe", "gasping for air", "severe shortness of breath"],
            "blue lips": ["cyanosis", "lips turning blue", "blue tinge"],
            "chest pain": ["chest pain", "pain in chest", "chest hurts"],
            "chest discomfort": ["chest discomfort", "discomfort in chest", "chest feels"],
            "difficulty breathing": ["shortness of breath", "breathing difficulty", "hard to breathe"],
            "shortness of breath": ["difficulty breathing", "breathing difficulty", "short of breath"],
            "severe abdominal pain": ["severe stomach pain", "intense abdominal pain", "extreme belly pain"],
            "high fever": ["fever over 103", "103 degrees", "103°f", "fever 103", "very high fever"],
            "fever over 103": ["high fever 103", "103 degree fever", "fever of 103"],
            "103°f": ["103 degrees", "fever 103", "103 degree fever"],
            "extremely swollen": ["extreme swelling", "very swollen", "massively swollen"],
            "extreme swelling": ["extremely swollen", "severe swelling", "significant swelling"],
            "turning purple": ["purple discoloration", "going purple", "bruising purple"],
            "purple discoloration": ["turning purple", "purple bruising", "discolored purple"],
            "can't bear weight": ["cannot bear weight", "unable to bear weight", "can't put weight"],
            "can't put weight": ["cannot put weight", "can't bear weight", "unable to walk on"],
            "can't walk": ["cannot walk", "unable to walk", "can't put weight"],
            "unable to walk": ["can't walk", "cannot walk", "can't bear weight"],
            "can't keep food down": ["cannot keep food down", "can't keep anything down", "vomiting everything"],
            "can't keep fluids down": ["cannot keep fluids down", "can't keep anything down"],
            "cannot keep fluids down": ["can't keep fluids down", "vomiting everything"],
            "pain getting worse": ["worsening pain", "pain worsening", "progressively worse"],
            "progressively worse": ["getting worse", "worsening", "increasingly worse"],
        }

        # Exact phrase match (case insensitive)
        if re.search(r'\b' + re.escape(flag) + r'\b', text, re.IGNORECASE):
            return True

        # For multi-word flags, require words to be close together (within 5 words)
        words = flag.split()
        if len(words) > 1:
            # Create pattern that allows up to 5 words between flag words
            pattern_parts = [re.escape(word) for word in words]
            pattern = r'\b' + r'(?:\s+\w+){0,5}\s+'.join(pattern_parts) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                # Additional check: for chest/pain combinations, ensure both are present
                if 'chest' in flag and 'pain' in flag:
                    # Require explicit mention of both "chest" and "pain" close together
                    if re.search(r'\b(?:chest\s+(?:\w+\s+){0,3}pain|pain\s+(?:\w+\s+){0,3}chest)\b', text, re.IGNORECASE):
                        return True
                    else:
                        return False
                return True

        # Check synonyms with phrase matching
        for synonym in synonyms.get(flag, []):
            if re.search(r'\b' + re.escape(synonym) + r'\b', text, re.IGNORECASE):
                return True
            
            # For multi-word synonyms, check proximity
            syn_words = synonym.split()
            if len(syn_words) > 1:
                pattern_parts = [re.escape(word) for word in syn_words]
                pattern = r'\b' + r'(?:\s+\w+){0,5}\s+'.join(pattern_parts) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    return True

        return False


__all__ = ["SymptomAssessmentAgent"]
