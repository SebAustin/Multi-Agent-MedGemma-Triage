# System Architecture

## High-Level Overview

The MedGemma AI Medical Triage System implements a multi-agent architecture where specialized AI agents collaborate to perform comprehensive patient triage.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Patient Input                            │
│                    "I have chest pain..."                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Intake Agent                                │
│  • Greets patient                                               │
│  • Collects symptoms                                            │
│  • Asks clarifying questions                                    │
│  • Structures information                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Symptom Assessment Agent                        │
│  • Analyzes symptoms                                            │
│  • Identifies potential conditions                              │
│  • Detects red flags                                            │
│  • Asks follow-up questions                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ├──────────────────────┐
                         │                      │
                         ▼                      ▼
┌────────────────────────────────┐   ┌─────────────────────────────┐
│   Medical Knowledge Agent      │   │  Red Flag Detection         │
│  • Provides medical context    │   │  • Emergency symptoms       │
│  • References guidelines       │   │  • Automatic escalation     │
│  • Supports other agents       │   │                             │
└────────────────────────────────┘   └──────────┬──────────────────┘
                                                 │
                         ┌───────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Urgency Classification Agent                        │
│  • Classifies urgency level                                     │
│  • Uses triage protocols                                        │
│  • Provides reasoning                                           │
│  • Determines time sensitivity                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               Care Recommendation Agent                          │
│  • Recommends care setting                                      │
│  • Suggests next steps                                          │
│  • Provides timeline                                            │
│  • Includes self-care guidance                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Communication Agent                              │
│  • Translates to patient-friendly language                      │
│  • Creates comprehensive report                                 │
│  • Ensures clarity and empathy                                  │
│  • Adds medical disclaimers                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Final Triage Report                           │
│  • Urgency level                                                │
│  • Care recommendations                                         │
│  • Next steps                                                   │
│  • Warning signs to watch                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Core Components

#### MedGemma Client (`src/models/medgemma_client.py`)
- Manages connection to MedGemma model
- Handles model loading and inference
- Implements retry logic and error handling
- Provides generation methods with configurable parameters

#### Agent Coordinator (`src/workflows/agent_coordinator.py`)
- Manages session state
- Coordinates agent execution
- Tracks conversation history
- Stores intermediate results
- Handles state transitions

#### Triage Workflow (`src/workflows/triage_workflow.py`)
- Orchestrates the full triage process
- Manages agent sequence
- Handles multi-turn conversations
- Implements decision logic
- Returns comprehensive results

### 2. Agent Components

Each agent inherits from `BaseAgent` and implements the `process()` method:

```python
class BaseAgent(ABC):
    def __init__(self, name: str, client: MedGemmaClient)
    def process(self, input_data: Dict) -> Dict
    def _generate(self, prompt: str) -> str
```

**Agent Communication Pattern:**
1. Receive structured input from coordinator
2. Format prompt using templates
3. Generate response via MedGemma
4. Parse and structure output
5. Return results to coordinator

### 3. Data Flow

```
User Input
    ↓
Intake Agent (collects information)
    ↓
Session State (stores conversation)
    ↓
Symptom Agent (analyzes symptoms)
    ↓
Session State (stores analysis)
    ↓
Knowledge Agent (provides context as needed)
    ↓
Urgency Agent (classifies urgency)
    ↓
Session State (stores classification)
    ↓
Care Agent (recommends actions)
    ↓
Session State (stores recommendations)
    ↓
Communication Agent (creates report)
    ↓
Final Output (structured triage result)
```

### 4. State Management

**TriageSession State Machine:**

```
INTAKE → SYMPTOM_ASSESSMENT → URGENCY_CLASSIFICATION → 
CARE_RECOMMENDATION → COMMUNICATION → COMPLETED
                                    ↓
                                  ERROR (if any step fails)
```

**Session Data Structure:**
```python
{
    "session_id": "uuid",
    "state": "INTAKE | SYMPTOM_ASSESSMENT | ...",
    "case_summary": "structured patient information",
    "symptom_analysis": "analyzed symptoms",
    "urgency_level": "EMERGENCY | URGENT | SEMI-URGENT | NON-URGENT",
    "care_setting": "recommended care location",
    "final_report": "patient-friendly triage report",
    ...
}
```

## Prompt Engineering Strategy

### Prompt Template Structure

Each agent uses a consistent prompt structure:

```
1. Base Medical Context (role and safety guidelines)
2. Agent-Specific Instructions (task and responsibilities)
3. Input Data (patient information or previous agent outputs)
4. Output Format Requirements (structured response)
5. Examples (few-shot learning when needed)
```

### Example: Urgency Classification Prompt

```
You are a medical AI assistant powered by MedGemma...

You are the Urgency Classification Agent. Your role is to:
1. Classify the case urgency level using established triage protocols
2. Provide clear reasoning for the classification
...

Patient case:
[case summary]

Classify the urgency level as one of:
- EMERGENCY: Immediate life-threatening...
- URGENT: Needs medical attention within hours...
...

Provide:
1. Urgency level with confidence
2. Key factors supporting this classification
...
```

## Safety Mechanisms

### 1. Red Flag Detection
- Automatic scanning for life-threatening symptoms
- Immediate escalation to EMERGENCY
- Hardcoded list of critical symptoms
- Multiple checkpoints across agents

### 2. Conservative Defaults
- If uncertain, default to higher urgency
- Recommend professional evaluation when in doubt
- Clear disclaimers in all outputs

### 3. Human-in-the-Loop Ready
- Confidence scores for review
- Complete audit trail
- Transparent reasoning
- Recommendation, not diagnosis

### 4. Error Handling
- Graceful degradation
- Fallback responses
- Comprehensive logging
- Session recovery

## Scalability Considerations

### Horizontal Scaling
- Stateless design (except sessions)
- Each request is independent
- Can deploy multiple instances behind load balancer
- Session storage can be externalized (Redis, etc.)

### Vertical Scaling
- Model quantization (8-bit, 4-bit)
- Batch inference for multiple patients
- GPU acceleration when available
- Caching of common patterns

### Performance Optimization
- Knowledge Agent uses caching
- Prompt reuse where possible
- Efficient tokenization
- Streaming responses (future)

## Deployment Options

### Option 1: Cloud Deployment
```
User → Load Balancer → Multiple App Instances → Shared Model Server
                            ↓
                      Shared Session Store (Redis)
```

### Option 2: On-Premise
```
User → Local Network → Single App Instance → Local Model
                            ↓
                      Local Session Store
```

### Option 3: Edge Deployment
```
User → Mobile/Tablet App → Quantized Model (on-device)
```

## Technology Stack

**Core:**
- Python 3.9+
- PyTorch
- Transformers (Hugging Face)
- MedGemma models

**Agent Framework:**
- LangChain (coordination)
- Custom agent implementations

**API/Interface:**
- Gradio (web demo)
- FastAPI (production API)
- Streamlit (alternative UI)

**Infrastructure:**
- Docker (containerization)
- YAML/JSON (configuration)
- Logging (loguru)

**Testing:**
- Pytest (unit tests)
- Custom scenario evaluation
- Jupyter notebooks (analysis)

## Security & Privacy

**Data Handling:**
- No persistent storage of patient data by default
- Session data in memory only
- Optional encrypted session storage
- HIPAA-compliant deployment possible

**Access Control:**
- API key authentication (production)
- Rate limiting
- User session isolation
- Audit logging

**Model Security:**
- Local model deployment option
- No data sent to external services
- Secure model loading
- Version pinning

## Monitoring & Observability

**Logging Levels:**
- INFO: Agent execution, state transitions
- DEBUG: Prompt details, intermediate results
- WARNING: Red flags detected, unusual patterns
- ERROR: Failures, exceptions

**Metrics to Track:**
- Triage completion rate
- Average processing time
- Urgency distribution
- Agent-specific performance
- Error rates by type

**Audit Trail:**
- All agent decisions logged
- Complete prompt/response pairs
- Session lifecycle events
- User interactions

## Future Enhancements

**Technical:**
- Streaming responses for real-time feedback
- Multi-lingual support
- Voice interface integration
- EHR system integration
- Federated learning for privacy

**Clinical:**
- Specialized agents for specific conditions
- Integration with medical databases
- Real-time clinical guideline updates
- Outcome tracking and feedback loop

**Operational:**
- Dashboard for monitoring
- Analytics and reporting
- A/B testing framework
- Continuous evaluation pipeline
