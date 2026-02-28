# EduLoop DSE - Dual-Agent Mastery Learning Ecosystem

A revolutionary AI-native education platform transforming HKDSE preparation through autonomous feedback loops between specialized Teaching and Assessment agents.

## Project Overview

EduLoop combines AWS Bedrock AgentCore orchestration with MiniMax's creative multi-modal content generation to simulate a 1-on-1 private tutor experience. The Teaching Agent delivers personalized modular lessons while the Assessment Agent dynamically generates syllabus-aligned tests and diagnostic reports.

## Architecture

```
eduloop/
├── core/                    # Orchestration & agent management
├── agents/                  # Teaching & Assessment agents
├── frontend/                # Streamlit UI
├── knowledge_base/          # DSE curriculum & RAG resources
├── utils/                   # Shared utilities & helpers
├── tests/                   # Unit & integration tests
└── config/                  # Configuration files
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment: `.env` setup with AWS & MiniMax credentials
3. Run frontend: `streamlit run frontend/app.py`

## Team Roles

- **Member A (Orchestrator)**: AWS Bedrock, state management, agent handshake protocol
- **Member B (Teaching Specialist)**: MiniMax integration, DSE knowledge RAG, audio generation
- **Member C (Assessment & UI)**: Streamlit UI, assessment logic, visualization

## Development Timeline

8-hour sprint with core milestones:

1. Protocol definition (1h)
2. Dual-agent core building (2h)
3. Data integration & handshake (1h)
4. UI & visualization (2h)
5. Multimodal & localization (1h)
6. Testing & demo (1h)
