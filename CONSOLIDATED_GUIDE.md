# EduLoop DSE — Consolidated Development Guide

This document consolidates the project development guide, file structure summary, and quick-start instructions into a single reference for contributors.

## Table of Contents

- **Development Guide**: detailed development plan and timeline
- **File Structure**: directory tree and component responsibilities
- **Quick Start**: install, configure, and run commands
- **Testing & Debugging**: test commands and troubleshooting
- **HKDSE Integration**: curriculum and assessment notes
- **Team Protocols & Next Steps**

---

## Development Guide

### Project Structure (excerpt)

```
eduloop/
├── core/                           # Orchestration & state management
│   ├── loop_manager.py             # Main learning loop state machine
│   ├── bedrock_orchestrator.py     # AWS Bedrock agent coordination
│   └── __init__.py
│
├── agents/                         # AI agents
│   ├── teaching_agent.py           # Lesson generation & delivery
│   ├── assessment_agent.py         # Question generation & evaluation
│   └── __init__.py
│
├── frontend/                       # Streamlit UI
│   ├── app.py                      # Main application interface
│   └── pages/                      # Multi-page components
│
├── knowledge_base/                 # DSE curriculum & resources
│   ├── dse_curriculum/             # Subject materials
│   ├── sample_papers/              # Past exam papers
│   ├── resources/                  # Learning materials
│   ├── rag_retriever.py
│   ├── pdf_parser.py               # Interpreting PDF
│   ├── ingest.py                   # Processing knowledge
│   ├── __init__.py
│   └── README.md                   # For further development
│
├── utils/                          # Helper utilities
│   ├── helpers.py                  # Common utility functions
|   └── __init__.py
│
├── config/                         # Configuration management
│   ├── protocol.py
│   ├── prompts.py
│   ├── config.py
│   └── __init__.py
│
├── tests/                          # Test suite
│   ├── test_loop_manager.py
│   ├── test_teaching_agent.py
|   ├── test_assessment_agent.py
│   └── __init__.py
│
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── example.env                    # Environment template
├── CONSOLIDATED_GUIDE.md           # Gonsolidated development guide
└── ARCHITECTURE.md                 # Design of application
```

### Team Role Mapping

#### Member A (Orchestrator/System Architect)
Files to focus on: `core/loop_manager.py`, `core/bedrock_orchestrator.py`.

Key tasks:
- AWS Bedrock setup and agent deployment
- Implement session state machine
- Design Teaching–Assessment agent handshake protocol
- Handle session persistence and logging

#### Member B (Teaching Specialist)
Files to focus on: `agents/teaching_agent.py`, `knowledge_base/`.

Key tasks:
- MiniMax LLM and audio integration
- Implement lesson content generation
- RAG integration for DSE curriculum
- Audio narration generation (Cantonese/English)

#### Member C (Assessment & UI)
Files to focus on: `agents/assessment_agent.py`, `frontend/app.py`.

Key tasks:
- Assessment question generation
- Automatic scoring and feedback
- Streamlit UI implementation

### Development Timeline (8 Hours) — Summary

Hour-by-hour plan, deliverables and testing checkpoints are included in the original development guide. Key milestones:
- Protocol & blueprint
- Core agent implementation (LoopManager, TeachingAgent, AssessmentAgent)
- Handshake & feedback loop tests
- UI pages and visualizations
- Polish, localization, and end-to-end demo

---

## File Structure Summary

This section summarizes the file layout and responsibilities.

Key components and locations (excerpt):

- `core/` — Orchestration, `LoopManager`, `BedrockAgentOrchestrator`
- `agents/` — `TeachingAgent`, `AssessmentAgent`
- `frontend/` — Streamlit UI (app.py and pages)
- `knowledge_base/` — DSE curriculum, sample papers
- `utils/` — `helpers.py` and utility functions
- `config/` — `config.py`, `protocol.py` (agent handshake schemas)
- `tests/` — unit tests for core and agents

Features by component (high level):

- Core: session state management, Bedrock integration, feedback processing
- Teaching Agent: multi-modal lesson generation, RAG, MiniMax hooks
- Assessment Agent: HKDSE question generation, auto-scoring, diagnostic reports
- Frontend: 5-page Streamlit app, progress visualizations

Implementation checklist and sprint status (condensed) are retained from the detailed file structure document.

---

## Quick Start

### 1. Clone and Navigate

```bash
cd /path/to/eduloop
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials (AWS, MINIMAX API keys, etc.)
```

### 4. Run Tests

```bash
pytest tests/ -v
```

### 5. Start Frontend

```bash
streamlit run frontend/app.py
```

Visit: `http://localhost:8501`

---

## Testing & Debugging

Common commands:

```bash
# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_loop_manager.py -v

# With coverage for key packages
pytest tests/ --cov=core --cov=agents --cov=utils
```

Debugging tips include verifying AWS credentials, MiniMax keys, and adjusting Streamlit port when necessary.

---

## HKDSE Integration Notes

- Subjects targeted: Mathematics (Compulsory Part)
- Papers: Paper 1 and Paper 2
- Levels: Foundational, Intermediate, Advanced
- Assessment: Automatic scoring with HKDSE marking schemes and personalized feedback

---

## Team Communication & Protocols

Agent handshake JSON is defined in `config/protocol.py`:
- Teaching → Assessment: lesson content, objectives
- Assessment → Teaching: knowledge gaps, error analysis, difficulty adjustment

---

## Next Steps & Recommendations

1. RAG Implementation: index DSE PDFs and enable vector retrieval
2. MiniMax Integration: finalize text-to-speech and LLM endpoints
3. Advanced Analytics: learning curve and predictive mastery models
4. Scalability: multi-user sessions and distributed agents

---

## Resources

- AWS Bedrock docs: https://docs.aws.amazon.com/bedrock/
- MiniMax API docs: https://platform.minimax.io/docs/
- Streamlit docs: https://docs.streamlit.io/
- HKDSE Curriculum: https://www.edb.gov.hk/