<p align="center">
  <img src="https://img.shields.io/badge/AWS-Bedrock%20AgentCore-FF9900?style=for-the-badge&logo=amazonaws" />
  <img src="https://img.shields.io/badge/MiniMax-Multi--Modal%20AI-6C5CE7?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
</p>

<h1 align="center">EduLoop DSE</h1>
<h3 align="center">A Dual-Agent Mastery Learning Ecosystem for HKDSE</h3>

<p align="center">
  <strong>Two AI agents. One closed loop. Zero knowledge gaps.</strong><br/>
  EduLoop transforms HKDSE exam preparation through an autonomous feedback loop between a <em>Teaching Agent</em> and an <em>Assessment Agent</em>, orchestrated by AWS Bedrock AgentCore and powered by MiniMax's multi-modal creative AI.
</p>

---

## The Problem

> **60,000+** Hong Kong students sit the HKDSE every year. Classrooms are overcrowded (30-40 students per teacher). Feedback is delayed by weeks. Tutoring costs HKD 300-800/hour. **Students who fall behind stay behind.**

Traditional ed-tech offers static quizzes or one-shot explanations — but learning is a **loop**, not a line. When a student gets a question wrong, they need **targeted re-teaching on exactly what and when they misunderstood**, not a generic "try again."The misunderstanding cannot wait until it causes more harm.

## Our Solution

EduLoop is an **AI-native 1-on-1 private tutor** that never sleeps, never loses patience, and continuously adapts. It implements a **closed-loop mastery learning system** where two specialized agents communicate autonomously:

```
┌────────────────────────────────────────────────────────────────┐
│                     🎓 STUDENT INPUT                          │
│              "Teach me about linear inequalities"              │
└──────────────────────────┬─────────────────────────────────────┘
                           ▼
            ┌──────────────────────────┐
            │   🧠 ORCHESTRATOR AGENT  │  ← AWS Bedrock AgentCore
            │  (State Machine + Router)│
            └─────┬──────────────┬─────┘
                  │              │
         ┌────────▼──────┐  ┌───▼──────────────┐
         │ 📚 TEACHING   │  │ ✏️ ASSESSMENT     │
         │    AGENT      │  │    AGENT          │
         │               │  │                   │
         │ • Micro-lesson│  │ • Diagnostic quiz │
         | • Video Demo  |  | • Trial and Hint  |
         │ • Examples    │  │ • Error analysis  │
         │ • Audio (TTS) │  │ • Misconception   │
         │ • DSE tips    │  │   detection       │
         │               │  │ • Mastery scoring │
         │  MiniMax API  │  │  MiniMax API      │
         └───────┬───────┘  └────────┬──────────┘
                 │                   │
                 │   ◄── FEEDBACK ──►│
                 │ "Student confused │
                 │  inequality sign  │
                 │  when multiplying │
                 │  by negatives"    │
                 │                   │
         ┌───────▼───────────────────▼──────────┐
         │       🔄 CLOSED-LOOP REFINEMENT      │
         │  Teaching Agent receives assessment   │
         │  report → regenerates targeted lesson │
         │  on EXACTLY the misconception found   │
         └───────────────────────────────────────┘
```

**This is not a chatbot.** This is an agentic workflow where two AI agents autonomously collaborate to drive a student from confusion to mastery.

---

## Key Features

### Autonomous Dual-Agent Architecture
- **Teaching Agent** generates personalized micro-lessons with worked examples, DSE exam tips, and key concept breakdowns
- **Assessment Agent** creates 3-5 diagnostic questions per lesson, detects misconceptions, and produces structured feedback reports
- **Orchestrator** manages the state machine: Teach → Assess → Analyze → Re-teach

### Multi-Modal Learning (MiniMax Creative AI)
- **Text Generation**: DSE-aligned explanations using MiniMax M2.5 LLM with curriculum-specific prompts
- **Audio Narration**: TTS-powered lesson delivery in English/Cantonese via MiniMax Speech API
- **Structured Visuals**: Radar charts, progress dashboards, and knowledge gap analysis

### Learning Science Integration
We don't just use AI — we apply **evidence-based pedagogy**:

| Theory | Implementation |
|--------|---------------|
| **Scaffolding (ZPD)** | Assessment Agent detects errors → Teaching Agent provides hints before answers, gradually removing support as mastery increases |
| **Active Recall** | Micro-lessons pause for student self-summary before proceeding; Assessment Agent validates recall quality |
| **Spaced Repetition** | Each knowledge point gets a `next_review_at` timestamp; system auto-schedules targeted review sessions |
| **Dual Coding** | Every concept delivered via text + audio simultaneously, leveraging MiniMax's multi-modal output |

### HKDSE-Specific Intelligence
- Mapped to official HKDSE syllabus (Paper 1, Paper 2 formats)
- Scoring aligned with DSE Marking Scheme (Level 1–5**)
- Common DSE terminology: "Paper 1", "Level 5**", "Compulsory Part", "Module 1/2"
- Knowledge base built from DSE past papers via RAG pipeline

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│              Streamlit Dashboard (app.py)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐    │
│  │Dashboard │ │  Learn   │ │ Practice │ │  Progress    │    │
│  │  📊      │ │  📖     │ │  ✏️      │ │  📈 Radar   │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / invoke
┌──────────────────────────▼──────────────────────────────────┐
│              ORCHESTRATION LAYER (AWS Bedrock AgentCore)      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Orchestrator Runtime (orchestrator.py)                │  │
│  │  • Session state management                            │  │
│  │  • Agent routing (Teach → Assess → Feedback)           │  │
│  │  • invoke_agent_runtime() cross-agent calls            │  │
│  └───────────┬───────────────────────────┬────────────────┘  │
│              │                           │                    │
│  ┌───────────▼──────────┐  ┌─────────────▼────────────┐     │
│  │  Teaching Runtime    │  │  Assessment Runtime      │     │
│  │  (teaching_agent.py) │  │  (assesment_agent.py)    │     │
│  └───────────┬──────────┘  └─────────────┬────────────┘     │
└──────────────┼───────────────────────────┼──────────────────┘
               │                           │
┌──────────────▼───────────────────────────▼────────────────── ┐
│                   INTELLIGENCE LAYER                         │
│                                                              │
│  ┌─────────────────────┐    ┌──────────────────────────┐     │
│  │  MiniMax M2.5 LLM   │    │  MiniMax Speech / TTS   │      │
│  │  (chatcompletion_v2) │    │  (Audio generation)     │     │
│  │  • Creative teaching │    │  • Cantonese/English    │     │
│  │  • Question gen      │    │  • Engaging narration   │     │
│  └─────────────────────┘    └──────────────────────────┘     │
│                                                              |
│  ┌─────────────────────────────────────────────────────┐     │
│  │  Knowledge Base (RAG)                               │     │
│  │  • HKDSE past papers  • Official syllabus           │     │
│  │  • Marking schemes    • Common misconceptions DB    │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

---

## Agent Communication Protocol

The two agents communicate via a structured JSON handshake — enabling **fully autonomous operation** without human intervention in the loop:

### Teaching Agent → Assessment Agent
```json
{
  "session_id": "session_abc123",
  "topic": "Linear Inequalities",
  "micro_lesson": {
    "explanation": "When multiplying both sides by a negative number, reverse the inequality sign...",
    "worked_examples": ["Example: -2x > 6 → x < -3"]
  },
  "assessment_blueprint": {
    "num_questions": 4,
    "difficulty_mix": {"easy": 1, "medium": 2, "hard": 1}
  }
}
```

### Assessment Agent → Teaching Agent (Feedback Loop)
```json
{
  "session_id": "session_abc123",
  "topic": "Linear Inequalities",
  "items": [
    {
      "question_id": "Q1",
      "skill": "inequality_sign_reversal",
      "is_correct": false,
      "error_type": "conceptual",
      "feedback": "Student did not reverse sign when dividing by -3"
    }
  ],
  "score": {"raw": 2, "total": 4, "mastery_estimate": 0.50},
  "misconceptions": [
    {"tag": "sign_reversal_negative_multiply", "evidence": "Consistent error in Q1, Q3"}
  ],
  "next_teaching_actions": [
    {"action": "reteach_micro", "focus": "inequality sign reversal with negatives", "priority": "high"}
  ]
}
```

The Orchestrator reads `next_teaching_actions` and **automatically triggers a new Teaching cycle** focused on the identified misconception — completing the loop; or it finds that the score is high enough to move on to next part or stops the cycle.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Orchestration** | AWS Bedrock AgentCore | Multi-agent runtime hosting, cross-agent invocation via `invoke_agent_runtime()` |
| **LLM** | MiniMax M2.5 (chatcompletion_v2) | Teaching content generation, assessment question creation |
| **Audio** | MiniMax Speech/TTS API | Cantonese & English lesson narration |
| **Frontend** | Streamlit + Plotly | Dashboard, radar charts, learning analytics |
| **Data** | ChromaDB (Vector DB) | RAG knowledge base for DSE curriculum |
| **Language** | Python 3.11+ | All agents and orchestration logic |
| **Cloud** | AWS (IAM, Bedrock AgentCore) | Production deployment and scaling |

---

## Project Structure

```
Stellaris/
├── deploy/                          # Production AgentCore deployments
│   ├── orchestrator/
│   │   ├── orchestrator.py          # State machine + cross-agent calls
│   │   └── requirements.txt
│   ├── teaching_agent/
│   │   ├── teaching_agent.py        # MiniMax-powered lesson generator
│   │   └── requirements.txt
│   └── assesment_agent/
│       ├── assesment_agent.py       # Diagnostic quiz + misconception detector
│       └── requirements.txt
│
├── eduloop/                         # Local development environment
│   ├── core/
│   │   ├── bedrock_orchestrator.py  # AWS Bedrock integration
│   │   └── loop_manager.py         # Learning loop state machine
│   ├── agents/
│   │   ├── teaching_agent.py       # Teaching Agent class
│   │   └── assessment_agent.py     # Assessment Agent class
│   ├── frontend/
│   │   └── app.py                  # Streamlit UI (5 pages)
│   ├── config/
│   │   ├── config.py               # Environment configuration
│   │   └── protocol.py             # Agent handshake protocol spec
│   ├── knowledge_base/             # DSE curriculum RAG resources
│   ├── tests/                      # Unit tests for all agents
│   └── utils/
│       └── helpers.py              # Shared utilities
│
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- AWS Account with Bedrock AgentCore access
- MiniMax API Key(s)

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-team/stellaris-eduloop.git
cd stellaris-eduloop/eduloop

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials:
#   AWS_REGION=us-east-1
#   MINIMAX_API_KEY=your_key_here

# Launch the UI
streamlit run frontend/app.py
```

### AWS Deployment (3 AgentCore Runtimes)

```bash
# 1. Deploy Teaching Agent
#    Runtime ARN: arn:aws:bedrock-agentcore:us-east-1:775964394588:runtime/teaching-F4k9ST6N84
#    Env vars: MINIMAX_API_KEY, MINIMAX_MODEL=MiniMax-M2.5

# 2. Deploy Assessment Agent
#    Runtime ARN: arn:aws:bedrock-agentcore:us-east-1:775964394588:runtime/Assesment-O8T4Lm6FAN
#    Env vars: MINIMAX_API_KEY, MINIMAX_MODEL=MiniMax-M2.5

# 3. Deploy Orchestrator
#    Runtime ARN: arn:aws:bedrock-agentcore:us-east-1:775964394588:runtime/Orchestrator-TdzHi4CXlj
#    Env vars: TEACHING_RUNTIME_ARN, ASSESSMENT_RUNTIME_ARN, AWS_REGION
```

---

## Demo Walkthrough

### Scenario: A student struggles with "inequality sign reversal"

1. **Student asks**: *"Teach me about solving linear inequalities"*
2. **Teaching Agent** generates a micro-lesson covering sign reversal rules, with a worked example: `-2x > 6 → x < -3`
3. **Assessment Agent** creates 4 diagnostic questions targeting common misconceptions
4. **Student answers** — gets Q1 and Q3 wrong (both involve multiplying by negatives)
5. **Assessment Agent detects** misconception: `sign_reversal_negative_multiply`
6. **Orchestrator automatically** routes feedback back to Teaching Agent
7. **Teaching Agent re-teaches** with targeted scaffolding: provides a hint first, then a simplified example, and only gives the full explanation if the student still struggles
8. **Loop continues** until mastery estimate reaches 80%+

> *This entire cycle runs autonomously through AWS Bedrock AgentCore — no human teacher in the loop.*

---

## Team — Stellaris

| Role | Responsibility | Core Tools |
|------|---------------|------------|
| **LIU Jiawei** — System Architect | AWS Bedrock AgentCore orchestration, agent handshake protocol, session state management | AWS Bedrock, Boto3, Python |
| **So Cheuk Ki** — Teaching Specialist | MiniMax API integration, multi-modal output, DSE knowledge RAG, audio generation | MiniMax API, Python |
| **XU Jiahang** — Assessment & UI | Assessment logic, auto-scoring (DSE Marking Scheme), Streamlit frontend, visualization | Streamlit, Plotly, Python |

---

## Awards We're Building For

| Award | How EduLoop Addresses Criteria |
|-------|-------------------------------|
| **Main Awards** | Novel dual-agent architecture; clear AI/ML technique (multi-agent orchestration + RAG); meaningful impact (60K+ HKDSE students); production-grade on AWS |
| **MiniMax Creative Usage** | Creative use of MiniMax LLM for *pedagogically-structured* teaching content + TTS audio narration in Cantonese — not just Q&A, but a full learning experience |
| **RevisionDojo Future of Learning** | Built on 4 learning science theories (scaffolding, spaced repetition, active recall, dual coding); adaptive difficulty; real mastery progression |
| **Ingram Micro & AWS Agentic AI Champion** | 3 agents running on Bedrock AgentCore with cross-runtime invocation; demonstrates real business value for HK's $4.7B education market |

---

## What Makes EduLoop Different

| Feature | Traditional Ed-Tech | EduLoop |
|---------|-------------------|---------|
| Feedback speed | Days/weeks | **Instant** (sub-minute) |
| Personalization | One-size-fits-all | **Misconception-targeted** re-teaching |
| Agent interaction | Single LLM call | **Autonomous multi-agent loop** |
| Content format | Text only | **Multi-modal** (text + audio + visuals) |
| Pedagogy | None | **4 learning science theories** baked in |
| Scalability | Per-teacher limit | **Serverless** on AWS AgentCore |
| DSE alignment | Generic | **Syllabus-mapped** with marking scheme scoring |

---
## Commercial Advantages & Future Development

### 1. Affordable 24/7 Personalized Tutoring
A private HKDSE tutor costs **HKD 300–800/hour**. EduLoop delivers the same misconception-targeted, adaptive teaching — around the clock, at a fraction of the cost — while continuously learning each student's study pattern.

### 2. High Flexibility via AWS Multi-Agent Architecture
Because every agent runs as an **independent AWS Bedrock AgentCore Runtime**, we can:
- Swap in models from **different providers** (MiniMax, Anthropic, Cohere, etc.) per agent without rewriting the system
- Scale each agent independently based on demand
- Add new specialist agents (e.g., a **Cantonese Explanation Agent** or a **Past Paper Analysis Agent**) with zero downtime

### 3. More Efficient Than a Single Monolithic Education Model
| Approach | EduLoop (Multi-Agent) | Single Large Model |
|----------|----------------------|--------------------|
| **Prompt focus** | Each agent has a dedicated system prompt → higher precision | One prompt tries to do everything → diluted quality |
| **Model selection** | Use a smaller, task-specific model for assessment (cheaper, faster) | Must use the largest model for all tasks |
| **Token cost** | Only the relevant agent processes each step | Every token pays for the full context of teaching + assessment + scoring |
| **Maintainability** | Update one agent without affecting others | Any change risks breaking the whole system |

> **Bottom line:** Separate agents = sharper focus, lower cost, easier iteration.
## License


MIT License — Built with ❤️ in Hong Kong for HKDSE students everywhere.

