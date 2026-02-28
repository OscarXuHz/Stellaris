# EduLoop DSE - Development Guide

## Project Structure

```
eduloop/
├── core/                          # Orchestration & state management
│   ├── loop_manager.py           # Main learning loop state machine
│   ├── bedrock_orchestrator.py   # AWS Bedrock agent coordination
│   └── __init__.py
│
├── agents/                        # AI agents
│   ├── teaching_agent.py         # Lesson generation & delivery
│   ├── assessment_agent.py       # Question generation & evaluation
│   └── __init__.py
│
├── frontend/                      # Streamlit UI
│   ├── app.py                    # Main application interface
│   └── pages/                    # Multi-page components
│
├── knowledge_base/                # DSE curriculum & resources
│   ├── dse_curriculum/           # Subject materials
│   ├── sample_papers/            # Past exam papers
│   ├── resources/                # Learning materials
│   └── README.md
│
├── utils/                         # Helper utilities
│   ├── helpers.py                # Common utility functions
│   └── __init__.py
│
├── config/                        # Configuration management
│   ├── config.py                 # Config classes & environment
│   └── __init__.py
│
├── tests/                         # Test suite
│   ├── test_loop_manager.py
│   ├── test_teaching_agent.py
│   ├── test_assessment_agent.py
│   └── __init__.py
│
├── requirements.txt               # Python dependencies
├── .env.example                  # Environment template
└── README.md                      # Project documentation
```

## Team Role Mapping

### Member A (Orchestrator/System Architect)
**Files to Focus On:**
- `core/loop_manager.py` - State management and learning loop
- `core/bedrock_orchestrator.py` - AWS Bedrock integration
- `core/__init__.py` - Module exports

**Key Tasks:**
1. AWS Bedrock setup and agent deployment
2. Implement session state machine
3. Design Teaching-Assessment agent handshake protocol
4. Handle session persistence and logging

### Member B (Teaching Specialist)
**Files to Focus On:**
- `agents/teaching_agent.py` - Lesson generation
- `knowledge_base/` - DSE curriculum integration
- MiniMax API integration (new file needed)

**Key Tasks:**
1. MiniMax LLM and audio integration
2. Implement lesson content generation
3. RAG integration for DSE curriculum
4. Audio narration generation (Cantonese/English)

### Member C (Assessment & UI)
**Files to Focus On:**
- `agents/assessment_agent.py` - Question generation & grading
- `frontend/app.py` - Streamlit interface
- Dashboard and visualization components

**Key Tasks:**
1. Assessment question generation
2. Automatic scoring and feedback
3. Streamlit UI implementation
4. Progress visualization and reports

## Development Timeline (8 Hours)

### Hour 1: Blueprint & Protocol (All Members)
- [ ] Review project structure
- [ ] Define Teaching→Assessment JSON protocol
- [ ] Initialize AWS Bedrock environment (Member A)
- [ ] Design system prompts (Members B & C)

**Deliverable:** `protocol.json` in `config/` directory

### Hours 2-3: Core Agent Building
**Member A:**
- [ ] Implement `LoopManager` state machine
- [ ] Create session management in `bedrock_orchestrator.py`

**Member B:**
- [ ] Implement `TeachingAgent` with lesson generation
- [ ] Create `_create_lesson_structure()` method

**Member C:**
- [ ] Implement `AssessmentAgent` with question generation
- [ ] Create evaluation and scoring logic

### Hour 4: Data Handshake Integration
- [ ] Test feedback loop in `loop_manager.py`
- [ ] Implement error analysis in assessment
- [ ] Unit tests for integration points

**Deliverable:** Passing integration tests

### Hours 5-6: UI & Visualization
**Member C:**
- [ ] Build Streamlit dashboard pages
- [ ] Implement progress radar chart
- [ ] Add assessment interface
- [ ] Create performance analytics

**Member B:**
- [ ] DSE curriculum RAG integration
- [ ] Implement PDF parsing

### Hour 7: Polish & Localization
**Member B:**
- [ ] Test MiniMax audio with Cantonese
- [ ] DSE terminology integration

**Member A:**
- [ ] Performance optimization
- [ ] Logging and monitoring

### Hour 8: Testing & Demo
- [ ] End-to-end testing
- [ ] Generate demo dataset
- [ ] Record 2-minute demo video

## Running the Application

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS and MiniMax credentials
```

### Development
```bash
# Run tests
pytest tests/ -v

# Run Streamlit frontend
streamlit run frontend/app.py

# Run specific tests
pytest tests/test_loop_manager.py -v
```

### Configuration
- AWS credentials in `.env`
- MiniMax API key in `.env`
- Database paths in `config/config.py`

## Key Implementation Notes

### Teaching-Assessment Handshake
The protocol defined in `BedrockAgentOrchestrator.create_agent_handshake_protocol()` ensures smooth communication:
- Teaching Agent → Assessment Agent: lesson content, objectives
- Assessment Agent → Teaching Agent: knowledge gaps, error analysis, difficulty adjustment

### State Machine
States: `INITIALIZED` → `TEACHING` → `ASSESSMENT` → `ANALYSIS` → `FEEDBACK` → repeat

### Vector Database
Currently configured for Chroma, can be switched to Pinecone via `config/config.py`

### HKDSE Integration
- Level mapping: percentage → Level 1 through 5**
- Paper distinction: Paper 1 and Paper 2
- Subject support: Mathematics, English, Physics, Chemistry, Biology, etc.

## Testing Strategy

- **Unit Tests:** Individual components (agents, managers)
- **Integration Tests:** Agent-to-agent communication
- **E2E Tests:** Full learning loop from lesson to assessment

Run with: `pytest tests/ --cov=` for coverage

## Next Steps for Extended Development

1. **RAG Implementation**
   - Index DSE curriculum PDFs
   - Implement retrieval with vector similarity

2. **MiniMax Integration**
   - Text-to-speech for multiple languages
   - Video content generation

3. **Advanced Analytics**
   - Learning curve analysis
   - Predictive mastery modeling

4. **Scalability**
   - Multi-user session management
   - Distributed agent architecture
   - Database optimization

## Troubleshooting

**AWS Bedrock Connection Error:**
- Verify AWS credentials in `.env`
- Check IAM permissions for Bedrock

**MiniMax API Issues:**
- Validate API key format
- Check rate limits
- Review API documentation

**Test Failures:**
- Clear pytest cache: `pytest --cache-clear`
- Check Python version: 3.8+

## Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [MiniMax API Docs](https://platform.minimax.io/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [HKDSE Curriculum](https://www.edb.gov.hk/)
