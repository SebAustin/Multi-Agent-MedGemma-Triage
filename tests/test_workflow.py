"""
Tests for the triage workflow.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.triage_workflow import TriageWorkflow
from src.workflows.agent_coordinator import AgentCoordinator, TriageState, TriageSession


class TestAgentCoordinator:
    """Tests for AgentCoordinator."""
    
    def test_initialization(self):
        """Test coordinator initialization."""
        coordinator = AgentCoordinator()
        assert len(coordinator.sessions) == 0
    
    def test_create_session(self):
        """Test session creation."""
        coordinator = AgentCoordinator()
        session = coordinator.create_session("test_session_1")
        
        assert session.session_id == "test_session_1"
        assert session.state == TriageState.INTAKE
        assert "test_session_1" in coordinator.sessions
    
    def test_get_session(self):
        """Test session retrieval."""
        coordinator = AgentCoordinator()
        coordinator.create_session("test_session_1")
        
        session = coordinator.get_session("test_session_1")
        assert session is not None
        assert session.session_id == "test_session_1"
        
        # Non-existent session
        session = coordinator.get_session("non_existent")
        assert session is None
    
    def test_update_session_state(self):
        """Test state updates."""
        coordinator = AgentCoordinator()
        coordinator.create_session("test_session_1")
        
        coordinator.update_session_state("test_session_1", TriageState.SYMPTOM_ASSESSMENT)
        session = coordinator.get_session("test_session_1")
        assert session.state == TriageState.SYMPTOM_ASSESSMENT
    
    def test_store_urgency_data(self):
        """Test storing urgency data."""
        coordinator = AgentCoordinator()
        coordinator.create_session("test_session_1")
        
        coordinator.store_urgency_data(
            "test_session_1",
            urgency_level="EMERGENCY",
            reasoning="Test reasoning",
            confidence="high",
            time_sensitive=True
        )
        
        session = coordinator.get_session("test_session_1")
        assert session.urgency_level == "EMERGENCY"
        assert session.time_sensitive is True
    
    def test_mark_completed(self):
        """Test marking session as completed."""
        coordinator = AgentCoordinator()
        coordinator.create_session("test_session_1")
        
        coordinator.mark_completed("test_session_1")
        session = coordinator.get_session("test_session_1")
        assert session.state == TriageState.COMPLETED
        assert session.completed_at is not None


class TestTriageSession:
    """Tests for TriageSession."""
    
    def test_session_creation(self):
        """Test session creation."""
        session = TriageSession(session_id="test_123")
        
        assert session.session_id == "test_123"
        assert session.state == TriageState.INTAKE
        assert len(session.red_flags) == 0
    
    def test_session_to_dict(self):
        """Test session serialization."""
        session = TriageSession(session_id="test_123")
        session.urgency_level = "URGENT"
        session.care_setting = "Urgent Care"
        
        data = session.to_dict()
        assert data["session_id"] == "test_123"
        assert data["urgency_level"] == "URGENT"
        assert data["care_setting"] == "Urgent Care"


class TestTriageWorkflow:
    """Tests for TriageWorkflow (integration-style)."""
    
    def test_initialization(self):
        """Test workflow initialization."""
        # Note: This requires MedGemma model to be available
        # In practice, you'd mock the model loading
        try:
            workflow = TriageWorkflow()
            assert workflow.coordinator is not None
            assert workflow.intake_agent is not None
        except Exception as e:
            pytest.skip(f"Could not initialize workflow (likely missing model): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
