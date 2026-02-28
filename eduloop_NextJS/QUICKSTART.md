# EduLoop DSE - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

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
# Edit .env with your credentials:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - MINIMAX_API_KEY
# - MINIMAX_GROUP_ID
```

### 4. Run Tests (Verify Setup)
```bash
pytest tests/ -v
```

### 5. Start Frontend
```bash
streamlit run frontend/app.py
```

Visit: `http://localhost:8501`

---

## 📁 What's Where

| Component | Location | Owner |
|-----------|----------|-------|
| **State Management** | `core/loop_manager.py` | Member A |
| **AWS Orchestration** | `core/bedrock_orchestrator.py` | Member A |
| **Lesson Generation** | `agents/teaching_agent.py` | Member B |
| **Assessment Logic** | `agents/assessment_agent.py` | Member C |
| **Web Interface** | `frontend/app.py` | Member C |
| **Configuration** | `config/` | All |
| **Tests** | `tests/` | All |

---

## 🎯 Development Workflow

### Member A (Orchestrator)
```bash
# Test state machine
pytest tests/test_loop_manager.py -v

# Develop locally
python -c "from core.loop_manager import LoopManager; ..."
```

### Member B (Teaching Specialist)
```bash
# Test teaching agent
pytest tests/test_teaching_agent.py -v

# Integrate MiniMax
# Edit: agents/teaching_agent.py _generate_audio_narration()
```

### Member C (Assessment & UI)
```bash
# Test assessment agent
pytest tests/test_assessment_agent.py -v

# Test frontend locally
streamlit run frontend/app.py
```

---

## 📝 File Checklist for 8-Hour Sprint

### ✅ Completed
- [x] Core orchestration (LoopManager, BedrockOrchestrator)
- [x] Dual agents (Teaching, Assessment)
- [x] Streamlit frontend (5 pages)
- [x] Configuration system
- [x] Utility helpers
- [x] Test suite
- [x] Documentation

### 🔄 To Complete During Hackathon
- [ ] AWS Bedrock model invocation
- [ ] MiniMax API integration for TTS
- [ ] Vector DB RAG implementation
- [ ] DSE curriculum indexing
- [ ] Live testing with real data
- [ ] Performance optimization
- [ ] Demo video recording

---

## 🧪 Testing Commands

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_loop_manager.py -v

# With coverage
pytest tests/ --cov=core --cov=agents --cov=utils

# Specific test
pytest tests/test_assessment_agent.py::test_level_assessment -v
```

---

## 🛠️ Debugging Tips

**AWS Credentials Error:**
```bash
# Verify credentials
aws sts get-caller-identity

# If fails, update .env and restart
```

**MiniMax API Error:**
```bash
# Test API key
curl -X POST https://api.minimaxi.com/v1/test \
  -H "Authorization: Bearer YOUR_KEY"
```

**Streamlit Port Error:**
```bash
# Use different port
streamlit run frontend/app.py --server.port 8502
```

**Module Import Error:**
```bash
# Ensure current directory in path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| Total Files | 20+ |
| Lines of Code | ~3,150 |
| Test Coverage | Core modules |
| Estimated Dev Time | 8 hours |
| Frontend Pages | 5 |
| Agent Types | 2 |

---

## 🎓 HKDSE Integration

The system is designed for:
- **Subjects:** Mathematics, English, Physics, Chemistry, Biology
- **Papers:** Paper 1, Paper 2 (+ Paper 3 if applicable)
- **Levels:** Foundational, Intermediate, Advanced
- **Assessment:** Automatic scoring using HKDSE marking schemes
- **Feedback:** Personalized based on knowledge gaps

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Project overview |
| DEVELOPMENT.md | Detailed development guide |
| ARCHITECTURE.md | System architecture diagrams |
| FILE_STRUCTURE.md | Complete file listing & summary |
| config/protocol.py | Agent communication protocol |

---

## 🚦 Team Communication Protocol

**Agent Handshake JSON** (defined in `config/protocol.py`)
- Teaching → Assessment: lesson content, objectives
- Assessment → Teaching: knowledge gaps, error analysis, difficulty adjustment
- Shared: session ID, student profile, curriculum reference

---

## 💡 Quick Tips

1. **Use IDE with Python support** (VSCode, PyCharm) for better development
2. **Git workflow**: Create branches per feature/agent
3. **Test early and often** - use pytest before committing
4. **Comment your code** - future maintainers will thank you
5. **Document API changes** - update protocol.py when modifying handshake

---

## 🏁 Demo Preparation

For the 2-minute demo video:
1. **0:00-0:30** - Show student logging in and profile
2. **0:30-1:15** - Demo lesson generation → audio playback
3. **1:15-1:50** - Show assessment taking → instant feedback
4. **1:50-2:00** - Show progress report with recommendations

Use: `streamlit run frontend/app.py` with pre-loaded demo data

---

## 📞 Support

- **AWS Issues:** Check AWS Bedrock documentation
- **MiniMax Issues:** Visit https://platform.minimax.io/docs/
- **Streamlit Issues:** Check https://docs.streamlit.io/
- **Python Issues:** Use Python 3.8+

---

**Good luck! 🎯**

Start with Hour 1 tasks in DEVELOPMENT.md and follow the timeline.
All core code is ready - focus on integration and testing!
