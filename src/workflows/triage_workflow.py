"""
Triage Workflow - Main orchestration of the multi-agent triage system.
"""
from typing import Dict, Any, Optional
import uuid
from src.agents import (
    IntakeAgent,
    SymptomAssessmentAgent,
    MedicalKnowledgeAgent,
    UrgencyClassificationAgent,
    CareRecommendationAgent,
    CommunicationAgent
)
from src.workflows.agent_coordinator import AgentCoordinator, TriageState
from src.utils.logger import logger
from config import AgentConfig


class TriageWorkflow:
    """
    Main workflow orchestrator for the medical triage system.
    
    Coordinates the execution of multiple specialized agents to perform
    comprehensive patient triage.
    """
    
    def __init__(self):
        """Initialize the workflow with all agents."""
        logger.info("Initializing TriageWorkflow")
        
        # Initialize coordinator
        self.coordinator = AgentCoordinator()
        
        # Initialize all agents
        try:
            self.intake_agent = IntakeAgent()
            self.symptom_agent = SymptomAssessmentAgent()
            self.knowledge_agent = MedicalKnowledgeAgent()
            self.urgency_agent = UrgencyClassificationAgent()
            self.care_agent = CareRecommendationAgent()
            self.communication_agent = CommunicationAgent()
            
            logger.success("All agents initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def start_triage(self, patient_input: str) -> Dict[str, Any]:
        """
        Start a new triage session.
        
        Args:
            patient_input: Initial patient complaint or symptoms
            
        Returns:
            Dict with session_id, response, and session status
        """
        # Create new session
        session_id = str(uuid.uuid4())
        session = self.coordinator.create_session(session_id)
        
        logger.info(f"Starting triage session {session_id}")
        
        try:
            # Run intake
            intake_result = self.intake_agent.process({
                "patient_input": patient_input,
                "is_initial": True
            })
            
            # Store patient input
            session.patient_input_history.append(patient_input)
            
            response = intake_result["response"]
            needs_more_info = intake_result["needs_more_info"]
            
            if needs_more_info:
                # Still in intake phase
                logger.info(f"Session {session_id} needs more information")
                return {
                    "session_id": session_id,
                    "response": response,
                    "needs_more_info": True,
                    "state": "intake"
                }
            else:
                # Have enough info, proceed with full triage
                case_summary = intake_result["case_summary"]
                conversation_history = intake_result["conversation_history"]
                
                self.coordinator.store_intake_data(
                    session_id,
                    conversation_history,
                    case_summary
                )
                
                # Continue with full workflow
                return self._run_full_triage(session_id)
                
        except Exception as e:
            logger.error(f"Error in start_triage: {e}")
            self.coordinator.mark_error(session_id, str(e))
            return {
                "session_id": session_id,
                "error": str(e),
                "state": "error"
            }
    
    def continue_intake(
        self,
        session_id: str,
        patient_input: str
    ) -> Dict[str, Any]:
        """
        Continue an intake conversation.
        
        Args:
            session_id: ID of the session
            patient_input: Patient's response to follow-up questions
            
        Returns:
            Dict with response and session status
        """
        session = self.coordinator.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        logger.info(f"Continuing intake for session {session_id}")
        
        try:
            # Add to history
            session.patient_input_history.append(patient_input)
            
            # Process follow-up
            intake_result = self.intake_agent.process({
                "patient_input": patient_input,
                "is_initial": False
            })
            
            response = intake_result["response"]
            needs_more_info = intake_result["needs_more_info"]
            
            if needs_more_info:
                return {
                    "session_id": session_id,
                    "response": response,
                    "needs_more_info": True,
                    "state": "intake"
                }
            else:
                # Have enough info, proceed
                case_summary = intake_result["case_summary"]
                conversation_history = intake_result["conversation_history"]
                
                self.coordinator.store_intake_data(
                    session_id,
                    conversation_history,
                    case_summary
                )
                
                return self._run_full_triage(session_id)
                
        except Exception as e:
            logger.error(f"Error in continue_intake: {e}")
            self.coordinator.mark_error(session_id, str(e))
            return {
                "session_id": session_id,
                "error": str(e),
                "state": "error"
            }
    
    def run_triage(self, patient_input: str) -> Dict[str, Any]:
        """
        Run complete triage in one go (for direct API usage).
        
        Args:
            patient_input: Patient's symptoms and information
            
        Returns:
            Complete triage results
        """
        # Start session
        result = self.start_triage(patient_input)
        
        # If needs more info, this method doesn't handle it well
        # Better to use start_triage + continue_intake for interactive mode
        if result.get("needs_more_info"):
            logger.warning("run_triage called but more information needed - using intake summary")
        
        return result
    
    def _run_full_triage(self, session_id: str) -> Dict[str, Any]:
        """
        Run the full triage workflow after intake is complete.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Complete triage results
        """
        session = self.coordinator.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        logger.info(f"Running full triage for session {session_id}")
        
        try:
            # Step 1: Symptom Assessment
            self.coordinator.update_session_state(session_id, TriageState.SYMPTOM_ASSESSMENT)
            logger.info(f"Session {session_id}: Symptom Assessment")
            
            # Pass original patient input for red flag detection
            original_input = "\n".join(session.patient_input_history) if session.patient_input_history else session.case_summary
            
            symptom_result = self.symptom_agent.process({
                "case_summary": session.case_summary,
                "original_input": original_input
            })
            
            self.coordinator.store_symptom_data(
                session_id,
                symptom_result["symptom_analysis"],
                symptom_result["primary_symptoms"],
                symptom_result["differential_diagnosis"],
                symptom_result["red_flags"]
            )
            
            # Step 2: Urgency Classification
            self.coordinator.update_session_state(session_id, TriageState.URGENCY_CLASSIFICATION)
            logger.info(f"Session {session_id}: Urgency Classification")
            
            urgency_result = self.urgency_agent.process({
                "case_summary": session.case_summary,
                "symptom_analysis": symptom_result["symptom_analysis"],
                "red_flags": symptom_result["red_flags"]
            })
            
            self.coordinator.store_urgency_data(
                session_id,
                urgency_result["urgency_level"],
                urgency_result["reasoning"],
                urgency_result["confidence"],
                urgency_result["time_sensitive"]
            )
            
            # Step 3: Care Recommendation
            self.coordinator.update_session_state(session_id, TriageState.CARE_RECOMMENDATION)
            logger.info(f"Session {session_id}: Care Recommendation")
            
            care_result = self.care_agent.process({
                "case_summary": session.case_summary,
                "urgency_level": urgency_result["urgency_level"],
                "urgency_reasoning": urgency_result["reasoning"]
            })
            
            self.coordinator.store_care_data(
                session_id,
                care_result["care_setting"],
                care_result["timeline"],
                care_result["next_steps"],
                care_result["self_care"],
                care_result["preparation"]
            )
            
            # Step 4: Communication/Report Generation
            self.coordinator.update_session_state(session_id, TriageState.COMMUNICATION)
            logger.info(f"Session {session_id}: Communication/Report Generation")
            
            communication_result = self.communication_agent.process({
                "case_summary": session.case_summary,
                "urgency_level": urgency_result["urgency_level"],
                "care_recommendation": care_result,
                "red_flags": symptom_result["red_flags"]
            })
            
            self.coordinator.store_communication_data(
                session_id,
                communication_result["report"],
                communication_result["summary"],
                communication_result["formatted_report"]
            )
            
            # Mark as completed
            self.coordinator.mark_completed(session_id)
            
            logger.success(f"Session {session_id} completed successfully")
            
            # Return comprehensive results
            return {
                "session_id": session_id,
                "state": "completed",
                "needs_more_info": False,
                
                # Summary
                "summary": communication_result["summary"],
                
                # Key results
                "urgency_level": urgency_result["urgency_level"],
                "time_sensitive": urgency_result["time_sensitive"],
                "red_flags": symptom_result["red_flags"],
                
                "care_setting": care_result["care_setting"],
                "timeline": care_result["timeline"],
                
                # Reports
                "report": communication_result["report"],
                "formatted_report": communication_result["formatted_report"],
                
                # Detailed results (optional to display)
                "details": {
                    "case_summary": session.case_summary,
                    "primary_symptoms": symptom_result["primary_symptoms"],
                    "differential_diagnosis": symptom_result["differential_diagnosis"],
                    "urgency_confidence": urgency_result["confidence"],
                    "next_steps": care_result["next_steps"],
                    "self_care": care_result["self_care"],
                    "preparation": care_result["preparation"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in full triage: {e}")
            self.coordinator.mark_error(session_id, str(e))
            return {
                "session_id": session_id,
                "error": str(e),
                "state": "error"
            }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session."""
        return self.coordinator.get_session_data(session_id)


__all__ = ["TriageWorkflow"]
