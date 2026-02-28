# EduLoop DSE - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EDULOOP DSE PLATFORM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐          ┌──────────────────────────┐ │
│  │  FRONTEND LAYER      │          │   AWS CLOUD SERVICES     │ │
│  │  ──────────────────  │          │   ──────────────────     │ │
│  │                      │          │                          │ │
│  │  • Streamlit UI      │◄────────►│  • AWS Bedrock           │ │
│  │  • Dashboard         │          │  • AgentCore             │ │
│  │  • Learn Page        │          │  • Model Invocation      │ │
│  │  • Practice Page     │          │                          │ │
│  │  • Progress Page     │          └──────────────────────────┘ │
│  │  • Settings Page     │                                        │
│  │                      │          ┌──────────────────────────┐ │
│  └──────────────────────┘          │   MINIMAX AI SERVICES    │ │
│                                    │   ──────────────────     │ │
│  ┌──────────────────────┐          │                          │ │
│  │  ORCHESTRATION CORE  │          │  • Text-to-Speech (TTS)  │ │
│  │  ──────────────────  │          │  • Audio Generation      │ │
│  │                      │◄────────►│  • Multi-modal Support   │ │
│  │  • LoopManager       │          │  • Cantonese/English     │ │
│  │  • SessionState      │          │                          │ │
│  │  • StateTransitions  │          └──────────────────────────┘ │
│  │  • FeedbackLoop      │                                        │
│  │                      │          ┌──────────────────────────┐ │
│  └──────────────────────┘          │   KNOWLEDGE BASE         │ │
│           ▲                         │   ────────────────      │ │
│           │                         │                        │ │
│  ┌────────┴──────────┐               │  • DSE Curriculum      │ │
│  │   DUAL AGENTS     │              │  • Sample Papers       │ │
│  │   ─────────────   │              │  • Learning Resources  │ │
│  │                   │              │  • Vector DB (Chroma)  │ │
│  │  TEACHING AGENT   │◄────────────►│                        │ │
│  │  ───────────────  │              └──────────────────────┘ │
│  │  • Lesson Gen     │                                        │
│  │  • Content Create │              ┌──────────────────────┐ │
│  │  • Audio Narrate  │              │   DATA PERSISTENCE   │ │
│  │  • RAG Retrieval  │              │   ───────────────   │ │
│  │                   │              │                    │ │
│  │  ASSESS AGENT     │◄────────────►│  • Session Storage  │ │
│  │  ──────────────   │              │  • Results DB       │ │
│  │  • Question Gen   │              │  • Analytics        │ │
│  │  • Auto-Grading   │              │                    │ │
│  │  • Feedback Gen   │              └──────────────────┘ │
│  │  • Gap Detection  │                                    │
│  │                   │                                    │
│  └───────────────────┘                                    │
│           ▲                                               │
│           │                                               │
│  ┌────────┴───────────────────────────────────────────┐  │
│  │     FEEDBACK LOOP (CORE INNOVATION)               │  │
│  │                                                    │  │
│  │  Teaching → Assessment → Analysis → Feedback      │  │
│  │     (Lesson) → (Questions) → (Report) → (Gaps)   │  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────┐
│  Student Profile    │
│  • Name, Subject    │
│  • Level, Style     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│        LEARNING LOOP CYCLE (LoopManager)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. TEACHING PHASE                                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Input: Topic, Level, Student Context              │ │
│  │ ▼                                                   │ │
│  │ TeachingAgent.generate_lesson()                    │ │
│  │ • Retrieve curriculum via RAG                      │ │
│  │ • Generate structured lesson content               │ │
│  │ • Create audio narration (MiniMax TTS)             │ │
│  │ ▼                                                   │ │
│  │ Output: {lesson_id, content, audio, objectives}   │ │
│  └────────────────────────────────────────────────────┘ │
│                      │                                   │
│                      ▼                                   │
│  2. ASSESSMENT PHASE                                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Input: Lesson content, Student learning history   │ │
│  │ ▼                                                   │ │
│  │ AssessmentAgent.generate_assessment()              │ │
│  │ • Generate 3-5 HKDSE-aligned questions             │ │
│  │ • Determine difficulty based on lesson             │ │
│  │ ▼                                                   │ │
│  │ Student answers questions                          │ │
│  │ ▼                                                   │ │
│  │ AssessmentAgent.evaluate_student_response()        │ │
│  │ • Score against HKDSE marking scheme               │ │
│  │ • Analyze errors and misconceptions                │ │
│  │ ▼                                                   │ │
│  │ Output: {score, gaps, errors, feedback}            │ │
│  └────────────────────────────────────────────────────┘ │
│                      │                                   │
│                      ▼                                   │
│  3. ANALYSIS PHASE                                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │ AssessmentAgent.generate_diagnostic_report()       │ │
│  │ • Aggregate knowledge gaps                         │ │
│  │ • Identify misconception patterns                  │ │
│  │ • Map HKDSE level (Level 1-5**)                    │ │
│  │ ▼                                                   │ │
│  │ Output: {report, gaps, recommendations, next_step}│ │
│  └────────────────────────────────────────────────────┘ │
│                      │                                   │
│                      ▼                                   │
│  4. FEEDBACK LOOP (THE HANDSHAKE!)                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ LoopManager.process_feedback_loop()                │ │
│  │ • Parse assessment gaps                            │ │
│  │ • Adjust next lesson difficulty                    │ │
│  │ • Select focus areas for reteaching                │ │
│  │ ▼                                                   │ │
│  │ Loop back to TEACHING with:                        │ │
│  │ • New topic or deeper dive                         │ │
│  │ • Adjusted difficulty level                        │ │
│  │ • Personalized focus areas                         │ │
│  └────────────────────────────────────────────────────┘ │
│                      │                                   │
│                      ▼                                   │
│  Repeat until mastery achieved (score > 85%)             │
│                                                          │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Student Progress   │
│  • Mastery Level    │
│  • Learning Path    │
│  • Performance Data │
└─────────────────────┘
```

## Module Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Streamlit)                      │
│                    frontend/app.py                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Dashboard  │ Learn  │ Practice  │ Progress  │ Settings  ││
│  └─────────────────────────────────────────────────────────┘│
└────────────┬───────────────────────────────────────┬─────────┘
             │                                       │
             ▼                                       ▼
┌──────────────────────┐            ┌──────────────────────┐
│   CONFIG LAYER       │            │   UTILS LAYER        │
│ config/config.py     │            │ utils/helpers.py     │
│ config/protocol.py   │            │                      │
│                      │            │ • generate_id()      │
│ • AWS Settings       │            │ • save_json()        │
│ • MiniMax Keys       │            │ • SessionManager     │
│ • DB Config          │            │ • DSE level calc     │
└──────────────────────┘            └──────────────────────┘
             ▲                                       ▲
             │                                       │
         ┌───┴─────────────┬─────────────────────────┴───┐
         │                 │                             │
         ▼                 ▼                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │          CORE ORCHESTRATION LAYER                        │
    │          core/                                           │
    ├─────────────────────────────────────────────────────────┤
    │                                                           │
    │  LoopManager (loop_manager.py)                           │
    │  ├── Session State Machine                              │
    │  ├── INITIALIZED → TEACHING → ASSESSMENT → ANALYSIS     │
    │  ├── process_feedback_loop()                            │
    │  └── Session persistence                               │
    │                                                           │
    │  BedrockAgentOrchestrator (bedrock_orchestrator.py)     │
    │  ├── AWS Bedrock API integration                        │
    │  ├── invoke_teaching_agent()                            │
    │  ├── invoke_assessment_agent()                          │
    │  └── Agent communication protocol                       │
    │                                                           │
    └─────────────────────────────────────────────────────────┘
         ▲                                    ▲
         │                                    │
         └────────────┬─────────────────────┬─┘
                      │                     │
                      ▼                     ▼
         ┌──────────────────────┐   ┌──────────────────────┐
         │   TEACHING AGENT     │   │  ASSESSMENT AGENT    │
         │ agents/teaching_     │   │ agents/assessment_   │
         │ agent.py             │   │ agent.py             │
         │                      │   │                      │
         │ generate_lesson()    │   │ generate_assessment()│
         │ • Content creation   │   │ • Question gen       │
         │ • Audio narration    │   │ • Auto scoring       │
         │ • RAG retrieval      │   │ • Feedback analysis  │
         │                      │   │ • Report generation  │
         │ Output:              │   │                      │
         │ {lesson_id,          │   │ Output:              │
         │  content,            │   │ {assessment_id,      │
         │  audio,              │   │  questions,          │
         │  objectives}         │   │  scores,             │
         │                      │   │  gaps,               │
         │                      │   │  recommendations}    │
         └──────────────────────┘   └──────────────────────┘
                  ▲                          ▲
                  │                          │
                  └────────┬─────────────────┘
                           │
                    ┌──────▼──────┐
                    │ KNOWLEDGE   │
                    │ BASE        │
                    │             │
                    │ • DSE Curri │
                    │ • Past Exam │
                    │ • Vector DB │
                    │ • RAG Data  │
                    └─────────────┘
```

## State Machine Diagram

```
                    ┌─────────────────┐
                    │  INITIALIZED    │
                    └────────┬────────┘
                             │
              initialize_session()
                             │
                             ▼
                    ┌─────────────────┐
                    │    TEACHING     │
                    │    PHASE        │
                    └────────┬────────┘
                             │
            Teaching Agent generates lesson
                             │
                             ▼
                    ┌─────────────────┐
                    │  ASSESSMENT     │
                    │  PHASE          │
                    └────────┬────────┘
                             │
            Assessment Agent evaluates student
                             │
                             ▼
                    ┌─────────────────┐
                    │  ANALYSIS       │
                    │  PHASE          │
                    └────────┬────────┘
                             │
        Generate diagnostic report & identify gaps
                             │
                             ▼
                    ┌─────────────────┐
                    │  FEEDBACK       │
                    │  PHASE          │
                    └────────┬────────┘
                             │
         Process feedback, adjust difficulty
                             │
                    ┌────────▼────────┐
                    │ Mastery < 85%?  │
                    └────────┬────────┘
                     YES │      │ NO
                         ▼      └─────► COMPLETED
                    ┌─────────────────┐
                    │    TEACHING     │
                    │  (New Topic)    │
                    └──────────────────┘
                       (Loop continues)
```
