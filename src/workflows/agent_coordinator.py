"""
Agent Coordinator - Manages agent communication and state.
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from src.utils.logger import logger


class TriageState(Enum):
    """States in the triage workflow."""
    INTAKE = "intake"
    SYMPTOM_ASSESSMENT = "symptom_assessment"
    URGENCY_CLASSIFICATION = "urgency_classification"
    CARE_RECOMMENDATION = "care_recommendation"
    COMMUNICATION = "communication"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class TriageSession:
    """Represents a triage session with state and data."""
    session_id: str
    state: TriageState = TriageState.INTAKE
    started_at: datetime = field(default_factory=datetime.now)
    
    # Patient data
    patient_input_history: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    
    # Agent outputs
    case_summary: str = ""
    symptom_analysis: str = ""
    primary_symptoms: List[str] = field(default_factory=list)
    differential_diagnosis: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    
    urgency_level: str = ""
    urgency_reasoning: str = ""
    urgency_confidence: str = ""
    time_sensitive: bool = False
    
    care_setting: str = ""
    timeline: str = ""
    next_steps: List[str] = field(default_factory=list)
    self_care: List[str] = field(default_factory=list)
    preparation: List[str] = field(default_factory=list)
    
    final_report: str = ""
    report_summary: str = ""
    formatted_report: str = ""
    
    # Metadata
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "case_summary": self.case_summary,
            "urgency_level": self.urgency_level,
            "care_setting": self.care_setting,
            "timeline": self.timeline,
            "red_flags": self.red_flags,
            "final_report": self.final_report,
            "report_summary": self.report_summary
        }


class AgentCoordinator:
    """Coordinates agent execution and manages triage state."""
    
    def __init__(self):
        self.sessions: Dict[str, TriageSession] = {}
        logger.info("AgentCoordinator initialized")
    
    def create_session(self, session_id: str) -> TriageSession:
        """Create a new triage session."""
        session = TriageSession(session_id=session_id)
        self.sessions[session_id] = session
        logger.info(f"Created session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[TriageSession]:
        """Get an existing session."""
        return self.sessions.get(session_id)
    
    def update_session_state(
        self,
        session_id: str,
        new_state: TriageState
    ) -> None:
        """Update session state."""
        if session_id in self.sessions:
            old_state = self.sessions[session_id].state
            self.sessions[session_id].state = new_state
            logger.info(f"Session {session_id} state: {old_state.value} -> {new_state.value}")
    
    def store_intake_data(
        self,
        session_id: str,
        conversation_history: List[Dict[str, str]],
        case_summary: str
    ) -> None:
        """Store intake agent results."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.conversation_history = conversation_history
            session.case_summary = case_summary
            logger.debug(f"Stored intake data for session {session_id}")
    
    def store_symptom_data(
        self,
        session_id: str,
        symptom_analysis: str,
        primary_symptoms: List[str],
        differential_diagnosis: List[str],
        red_flags: List[str]
    ) -> None:
        """Store symptom assessment results."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.symptom_analysis = symptom_analysis
            session.primary_symptoms = primary_symptoms
            session.differential_diagnosis = differential_diagnosis
            session.red_flags = red_flags
            logger.debug(f"Stored symptom data for session {session_id}")
    
    def store_urgency_data(
        self,
        session_id: str,
        urgency_level: str,
        reasoning: str,
        confidence: str,
        time_sensitive: bool
    ) -> None:
        """Store urgency classification results."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.urgency_level = urgency_level
            session.urgency_reasoning = reasoning
            session.urgency_confidence = confidence
            session.time_sensitive = time_sensitive
            logger.debug(f"Stored urgency data for session {session_id}: {urgency_level}")
    
    def store_care_data(
        self,
        session_id: str,
        care_setting: str,
        timeline: str,
        next_steps: List[str],
        self_care: List[str],
        preparation: List[str]
    ) -> None:
        """Store care recommendation results."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.care_setting = care_setting
            session.timeline = timeline
            session.next_steps = next_steps
            session.self_care = self_care
            session.preparation = preparation
            logger.debug(f"Stored care data for session {session_id}")
    
    def store_communication_data(
        self,
        session_id: str,
        report: str,
        summary: str,
        formatted_report: str
    ) -> None:
        """Store communication agent results."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.final_report = report
            session.report_summary = summary
            session.formatted_report = formatted_report
            logger.debug(f"Stored communication data for session {session_id}")
    
    def mark_completed(self, session_id: str) -> None:
        """Mark session as completed."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.state = TriageState.COMPLETED
            session.completed_at = datetime.now()
            logger.info(f"Session {session_id} completed")
    
    def mark_error(self, session_id: str, error_message: str) -> None:
        """Mark session as having an error."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.state = TriageState.ERROR
            session.error_message = error_message
            logger.error(f"Session {session_id} error: {error_message}")
    
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get all data for a session."""
        session = self.get_session(session_id)
        if session:
            return session.to_dict()
        return {}
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Remove old sessions. Returns number of sessions removed."""
        from datetime import timedelta
        now = datetime.now()
        cutoff = now - timedelta(hours=max_age_hours)
        
        to_remove = []
        for session_id, session in self.sessions.items():
            session_time = session.completed_at or session.started_at
            if session_time < cutoff:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old sessions")
        
        return len(to_remove)


__all__ = ["AgentCoordinator", "TriageSession", "TriageState"]
