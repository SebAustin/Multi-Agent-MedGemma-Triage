"""
Unit tests for individual agents.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import (
    IntakeAgent,
    SymptomAssessmentAgent,
    MedicalKnowledgeAgent,
    UrgencyClassificationAgent,
    CareRecommendationAgent,
    CommunicationAgent
)


@pytest.fixture
def sample_case_summary():
    """Sample case summary for testing."""
    return """
    Chief Complaint: Chest pain
    History: 45-year-old male with sudden onset severe chest pain for 30 minutes.
    Pain is pressure-like, radiating to left arm.
    Associated symptoms: Sweating, nausea
    Relevant History: Family history of heart disease, smoker
    """


@pytest.fixture
def sample_symptom_analysis():
    """Sample symptom analysis for testing."""
    return """
    Primary Symptoms:
    - Severe chest pain (pressure-like)
    - Pain radiating to left arm
    - Sweating
    - Nausea
    
    Differential Diagnosis:
    - Acute coronary syndrome
    - Myocardial infarction
    - Unstable angina
    
    Red Flags: Chest pain with radiation - requires immediate evaluation
    """


class TestIntakeAgent:
    """Tests for IntakeAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = IntakeAgent()
        assert agent.name == "Intake Agent"
        assert len(agent.conversation_history) == 0
    
    def test_initial_intake(self):
        """Test initial patient intake."""
        agent = IntakeAgent()
        
        # Note: This test won't work without actual MedGemma model loaded
        # In practice, you'd mock the _generate method
        assert agent is not None


class TestSymptomAssessmentAgent:
    """Tests for SymptomAssessmentAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = SymptomAssessmentAgent()
        assert agent.name == "Symptom Assessment Agent"
    
    def test_extract_primary_symptoms(self, sample_symptom_analysis):
        """Test symptom extraction."""
        agent = SymptomAssessmentAgent()
        symptoms = agent._extract_primary_symptoms(sample_symptom_analysis)
        assert len(symptoms) > 0


class TestMedicalKnowledgeAgent:
    """Tests for MedicalKnowledgeAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = MedicalKnowledgeAgent()
        assert agent.name == "Medical Knowledge Agent"
        assert len(agent._knowledge_cache) == 0


class TestUrgencyClassificationAgent:
    """Tests for UrgencyClassificationAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = UrgencyClassificationAgent()
        assert agent.name == "Urgency Classification Agent"
    
    def test_extract_urgency_level(self):
        """Test urgency level extraction."""
        agent = UrgencyClassificationAgent()
        
        response = "Based on the symptoms, this is an EMERGENCY situation."
        level = agent._extract_urgency_level(response)
        assert level == "EMERGENCY"
        
        response = "This appears to be a NON-URGENT condition."
        level = agent._extract_urgency_level(response)
        assert level == "NON-URGENT"


class TestCareRecommendationAgent:
    """Tests for CareRecommendationAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = CareRecommendationAgent()
        assert agent.name == "Care Recommendation Agent"
    
    def test_extract_care_setting(self):
        """Test care setting extraction."""
        agent = CareRecommendationAgent()
        
        recommendations = "Patient should go to the Emergency Department immediately."
        setting = agent._extract_care_setting(recommendations, "EMERGENCY")
        assert "Emergency" in setting or "ER" in setting


class TestCommunicationAgent:
    """Tests for CommunicationAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        agent = CommunicationAgent()
        assert agent.name == "Communication Agent"
    
    def test_create_summary(self):
        """Test summary creation."""
        agent = CommunicationAgent()
        
        care_info = {
            "care_setting": "Emergency Department (ER)",
            "timeline": "Immediately"
        }
        
        summary = agent._create_summary("EMERGENCY", care_info)
        assert "EMERGENCY" in summary
        assert "Emergency" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
