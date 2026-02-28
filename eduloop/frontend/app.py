"""Streamlit frontend application for EduLoop."""

import sys
from pathlib import Path

# Ensure project root is on the path so we can import our modules
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any, Optional

from knowledge_base.rag_retriever import DSERetriever
from agents.teaching_agent import TeachingAgent
from agents.assessment_agent import AssessmentAgent
from config.config import DatabaseConfig, MiniMaxConfig

# Configure page
st.set_page_config(
    page_title="EduLoop DSE",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        color: #1f77b4;
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .progress-section {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    /* Ensure LaTeX blocks render with proper spacing */
    .katex-display {
        margin: 1em 0 !important;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "student_profile" not in st.session_state:
        st.session_state.student_profile = {
            "name": "",
            "subjects": [],
            "level": "intermediate",
            "learning_style": "visual"
        }
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None
    if "lesson_history" not in st.session_state:
        st.session_state.lesson_history = []
    if "assessment_results" not in st.session_state:
        st.session_state.assessment_results = []

    # --- RAG & Agent initialisation (once per session) ---
    if "rag_retriever" not in st.session_state:
        st.session_state.rag_retriever = DSERetriever(
            persist_directory=DatabaseConfig.VECTOR_DB_PATH,
            collection_name=DatabaseConfig.CHROMA_COLLECTION,
            embedding_model=DatabaseConfig.EMBEDDING_MODEL,
        )
    if "teaching_agent" not in st.session_state:
        st.session_state.teaching_agent = TeachingAgent(
            minimax_api_key=MiniMaxConfig.MINIMAX_API_KEY or "",
            rag_vectordb=st.session_state.rag_retriever,
        )
    if "assessment_agent" not in st.session_state:
        st.session_state.assessment_agent = AssessmentAgent(
            minimax_api_key=MiniMaxConfig.MINIMAX_API_KEY or "",
            rag_vectordb=st.session_state.rag_retriever,
        )


def sidebar_navigation():
    """Create sidebar navigation."""
    st.sidebar.title("🎓 EduLoop Navigation")
    
    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Learn", "Practice", "Progress", "Settings"]
    )
    
    return page


def dashboard_page():
    """Display main dashboard."""
    st.markdown('<h1 class="main-title">📚 EduLoop DSE Learning Platform</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Lessons Completed", len(st.session_state.lesson_history), "+2 this week")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Average Score", "75%", "+5% improvement")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Study Streak", "7 days", "Keep it up!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Progress radar chart
    st.subheader("📊 Mastery Progress by Math Syllabus Topic")
    
    subjects = ["Algebra", "Geometry", "Trigonometry", "Calculus", "Statistics"]
    scores = [78, 82, 65, 71, 88]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=subjects,
        fill='toself',
        name='Mastery Level'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="HKDSE Subject Mastery",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("📅 Recent Activity")
    activity_data = {
        "Date": ["2024-02-27", "2024-02-26", "2024-02-25"],
        "Activity": ["Completed: Quadratic Equations", "Assessment: Polynomials", "Lesson: Functions"],
        "Score": ["8/10", "7/10", "N/A"]
    }
    st.dataframe(pd.DataFrame(activity_data), use_container_width=True)


def learn_page():
    """Display lesson content generated by MiniMax LLM + RAG context."""
    st.title("📖 Learn with Your Personal Tutor")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("Select Syllabus")
        syllabus = st.selectbox(
            "Syllabus",
            ["Math Foundation", "Math I", "Math II"],
        )

        topics_map = {
            "Math Foundation": ["Quadratic Equations", "Functions", "Geometry", "Trigonometry"],
            "Math I": ["Calculus", "Probability", "Binomial Distribution"],
            "Math II": ["Matrix Algebra", "Vectors", "System of Linear Equations"],
        }

        topic = st.selectbox("Topic", topics_map[syllabus])

        if st.button("📝 Generate Lesson", use_container_width=True):
            with st.spinner("Querying RAG database & calling MiniMax AI tutor…"):
                st.session_state.current_topic = f"{syllabus} — {topic}"

                retriever: DSERetriever = st.session_state.rag_retriever
                rag_results = retriever.retrieve(topic, k=5)
                st.session_state.rag_context = rag_results

                agent: TeachingAgent = st.session_state.teaching_agent
                lesson = agent.generate_lesson(
                    topic=topic,
                    level=st.session_state.student_profile.get("level", "intermediate"),
                    student_profile=st.session_state.student_profile,
                )
                st.session_state.current_lesson = lesson
                st.success(f"Lesson on **{topic}** ready! ({lesson.get('rag_chunks_used', 0)} RAG chunks used)")

        # API key status indicator
        if MiniMaxConfig.MINIMAX_API_KEY:
            st.caption("✅ MiniMax API key configured")
        else:
            st.warning("⚠️ No API key — set `MINIMAX_API_KEY` in `.env`")

    with col2:
        if st.session_state.current_topic:
            st.subheader(f"Lesson: {st.session_state.current_topic}")

            lesson = st.session_state.get("current_lesson", {})
            llm = lesson.get("llm_response", {})

            # Show error banner if the LLM call failed
            if llm.get("status") == "error":
                st.error(llm.get("error", "Unknown error"))

            tabs = st.tabs([
                "📘 Lesson",
                "🎯 Objectives & Advice",
                "💡 Assessment Ideas",
                "📚 RAG Sources",
            ])

            # ── Tab 0: Lesson (content_blocks from protocol) ─────────
            with tabs[0]:
                blocks = llm.get("content_blocks", [])
                if blocks:
                    for block in blocks:
                        btype = block.get("type", "concept")
                        text  = block.get("text", "")

                        if btype == "introduction":
                            st.markdown("### 📖 Introduction")
                            st.markdown(text)
                        elif btype == "concept":
                            st.markdown("### 📘 Concept")
                            st.markdown(text)
                        elif btype == "example":
                            st.markdown("### 📝 Worked Example")
                            st.markdown(text)
                        elif btype == "common_pitfall":
                            st.markdown("### ⚠️ Common Pitfall")
                            st.warning(text)
                        elif btype == "summary":
                            st.markdown("### ✅ Summary")
                            st.success(text)
                        else:
                            st.markdown(f"### {btype.title()}")
                            st.markdown(text)
                        st.divider()
                else:
                    st.info("Click **Generate Lesson** to begin.")

            # ── Tab 1: Objectives & Constructive Advice ──────────────
            with tabs[1]:
                objectives = llm.get("learning_objectives", [])
                if objectives:
                    st.markdown("### 🎯 Learning Objectives")
                    for obj in objectives:
                        st.markdown(f"- {obj}")
                else:
                    st.info("No learning objectives returned.")

                advice = llm.get("constructive_advice", "")
                if advice:
                    st.divider()
                    st.markdown("### 💬 Constructive Advice from Your Tutor")
                    st.info(advice)

            # ── Tab 2: Assessment question ideas ─────────────────────
            with tabs[2]:
                suggestions = llm.get("suggested_questions_for_assessment", [])
                if suggestions:
                    st.markdown("### 📝 Suggested Practice Questions")
                    for i, q in enumerate(suggestions, 1):
                        st.markdown(f"{i}. {q}")
                else:
                    st.info("No suggested questions returned.")

            # ── Tab 3: RAG Sources ───────────────────────────────────
            with tabs[3]:
                st.markdown("### 📚 RAG Retrieved Sources")
                refs = lesson.get("dse_references", [])
                if refs:
                    st.caption(f"Sources used: {', '.join(refs)}")
                rag_results = st.session_state.get("rag_context", [])
                if rag_results:
                    for i, r in enumerate(rag_results, 1):
                        with st.expander(f"Source {i}: {r['source']} (score {r['score']})"):
                            st.write(r["text"][:800])
                            st.caption(f"Topics: {r['metadata'].get('detected_topics', 'N/A')}")
                else:
                    st.info("No RAG sources — run ingestion first.")


def practice_page():
    """Display assessment page with RAG questions + MiniMax-powered evaluation."""
    st.title("✏️ Practice & Assessment")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("Start Assessment")
        syllabus = st.selectbox(
            "Syllabus Context",
            ["Math Foundation", "Math I", "Math II"],
        )

        topics_map = {
            "Math Foundation": ["Quadratic Equations", "Functions", "Geometry", "Trigonometry"],
            "Math I": ["Calculus", "Probability", "Binomial Distribution"],
            "Math II": ["Matrix Algebra", "Vectors", "System of Linear Equations"],
        }

        topic = st.selectbox("Topic", topics_map[syllabus], key="practice_topic")
        num_questions = st.slider("Number of Questions", 1, 10, 3)
        show_marking = st.checkbox("Show marking schemes", value=False)

        if st.button("🚀 Start Assessment", use_container_width=True):
            retriever: DSERetriever = st.session_state.rag_retriever
            paper_results = retriever.retrieve(
                topic, k=num_questions, where={"document_type": "paper"},
            )
            marking_results = retriever.retrieve(
                topic, k=num_questions, where={"document_type": "marking_scheme"},
            )
            if not paper_results:
                paper_results = retriever.retrieve(topic, k=num_questions)

            raw_questions = paper_results[:num_questions]

            # ── Reformat raw OCR question text with LaTeX via MiniMax ──
            agent: TeachingAgent = st.session_state.teaching_agent
            with st.spinner("Formatting questions with LaTeX via MiniMax…"):
                formatted_questions = []
                for q in raw_questions:
                    q_copy = dict(q)
                    q_copy["text"] = agent.format_question_latex(
                        q.get("text", ""), topic
                    )
                    formatted_questions.append(q_copy)

            st.session_state.current_assessment = {
                "topic": topic,
                "syllabus": syllabus,
                "num_questions": num_questions,
                "started_at": datetime.now().isoformat(),
                "questions": formatted_questions,
                "marking": marking_results[:num_questions],
            }
            # Clear previous evaluations
            st.session_state.pop("evaluation_results", None)
            st.success(
                f"Assessment ready! {len(formatted_questions)} questions loaded & formatted with LaTeX."
            )

        # API key indicator
        if MiniMaxConfig.MINIMAX_API_KEY:
            st.caption("✅ MiniMax API key configured")
        else:
            st.warning("⚠️ No API key — evaluation will be unavailable")

    with col2:
        if "current_assessment" in st.session_state:
            assessment = st.session_state.current_assessment
            questions = assessment.get("questions", [])
            marking = assessment.get("marking", [])

            st.subheader(
                f"Assessment: {assessment['topic']} ({assessment['syllabus']})"
            )
            st.info(
                f"{len(questions)} DSE past-paper questions retrieved from the knowledge base"
            )

            if not questions:
                st.warning(
                    "No past-paper questions found for this topic. "
                    "Add more papers to `knowledge_base/sample_papers/` and re-run ingestion."
                )
                return

            # ── Display each question with answer box + submit ───────
            for i, q in enumerate(questions, 1):
                year = q.get("metadata", {}).get("year", "")
                paper = q.get("metadata", {}).get("paper", "")
                source = q.get("source", "")
                label = f"DSE {year} {paper}" if year else source

                with st.expander(f"Question {i}  —  {label}", expanded=(i == 1)):
                    st.markdown(q.get("text", "_No text_"))
                    st.caption(f"Source: {source} | Relevance: {q.get('score', 'N/A')}")

                    answer = st.text_area(
                        f"Your answer for Q{i}",
                        key=f"answer_{i}",
                        height=120,
                    )

                    if st.button(f"Submit & Evaluate Q{i}", key=f"submit_{i}"):
                        if not answer.strip():
                            st.warning("Please write your answer before submitting.")
                        else:
                            with st.spinner("Evaluating with MiniMax AI examiner…"):
                                agent: AssessmentAgent = st.session_state.assessment_agent
                                result = agent.evaluate(
                                    topic=assessment["topic"],
                                    question_text=q.get("text", ""),
                                    student_answer=answer,
                                    difficulty=st.session_state.student_profile.get("level", "intermediate"),
                                )
                                # Store result in session
                                if "evaluation_results" not in st.session_state:
                                    st.session_state.evaluation_results = {}
                                st.session_state.evaluation_results[i] = result

                    # ── Show evaluation result if available ──────────
                    eval_results = st.session_state.get("evaluation_results", {})
                    if i in eval_results:
                        ev = eval_results[i]
                        llm_r = ev.get("llm_response", {})

                        if llm_r.get("status") == "error":
                            st.error(llm_r.get("error", "Evaluation failed"))
                        else:
                            diag = llm_r.get("diagnostic_report", {})
                            score = llm_r.get("score_percentage")

                            st.divider()
                            st.markdown("#### 📊 AI Evaluation")
                            if score is not None:
                                st.metric("Score", f"{score}%")

                            strengths = diag.get("strengths", [])
                            if strengths:
                                st.markdown("**Strengths:**")
                                for s in strengths:
                                    st.markdown(f"✅ {s}")

                            gaps = diag.get("knowledge_gaps", [])
                            if gaps:
                                st.markdown("**Knowledge Gaps:**")
                                for g in gaps:
                                    st.markdown(f"⚠️ {g}")

                            feedback = diag.get("constructive_feedback", "")
                            if feedback:
                                st.info(f"💬 **Feedback:** {feedback}")

                            misconception = diag.get("misconception_analysis", "")
                            if misconception:
                                st.warning(f"🔍 **Misconception:** {misconception}")

                            nxt = llm_r.get("next_step_recommendation", {})
                            if nxt:
                                st.caption(
                                    f"Next step: **{nxt.get('action', '')}** — "
                                    f"focus on: {', '.join(nxt.get('focus_topics_for_teacher', []))}"
                                )

                    # ── Optionally show raw marking scheme ───────────
                    if show_marking and i - 1 < len(marking):
                        mk = marking[i - 1]
                        st.divider()
                        st.markdown("**📋 Official Marking Scheme**")
                        st.markdown(mk.get("text", "_No marking scheme available_"))
                        st.caption(f"Source: {mk.get('source', '')}")

            # ── Overall summary ──────────────────────────────────────
            st.divider()
            st.markdown("### 📊 Assessment Summary")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Questions", len(questions))
            with c2:
                years = {q.get('metadata', {}).get('year', '?') for q in questions}
                st.metric("Years Covered", ", ".join(sorted(years)))
            with c3:
                st.metric("Topic", assessment["topic"])


def progress_page():
    """Display progress and analytics page."""
    st.title("📈 Your Progress & Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Performance by Topic")
        performance_data = {
            "Topic": ["Linear Equations", "Polynomials", "Functions", "Trigonometry"],
            "Score (%)": [85, 72, 78, 65],
            "Attempts": [3, 2, 4, 1]
        }
        df = pd.DataFrame(performance_data)
        st.bar_chart(df.set_index("Topic")["Score (%)"])
    
    with col2:
        st.subheader("⏰ Learning Time")
        time_data = {
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Minutes": [45, 60, 30, 75, 50, 90, 20]
        }
        df_time = pd.DataFrame(time_data)
        st.line_chart(df_time.set_index("Day")["Minutes"])
    
    st.subheader("🎯 Knowledge Gaps")
    gaps_data = {
        "Area": ["Quadratic Equations", "Function Composition", "Trig Identities"],
        "Frequency": [4, 2, 3],
        "Priority": ["High", "Medium", "Medium"]
    }
    st.dataframe(pd.DataFrame(gaps_data), use_container_width=True)
    
    st.subheader("💡 Recommendations")
    st.info("Based on your performance, focus on:\n\n1. Quadratic Equations - Practice 5 more problems\n2. Review function properties - Complete review lesson\n3. Trigonometric identities - Work through 10 practice sets")


def settings_page():
    """Display settings page."""
    st.title("⚙️ Settings & Profile")
    
    with st.form("student_profile_form"):
        st.subheader("Student Profile")
        
        name = st.text_input(
            "Full Name",
            value=st.session_state.student_profile.get("name", "")
        )
        
        subjects = st.multiselect(
            "Subjects",
            ["Mathematics", "English", "Physics", "Chemistry", "Biology"],
            default=st.session_state.student_profile.get("subjects", [])
        )
        
        level = st.selectbox(
            "Current Level",
            ["Foundational", "Intermediate", "Advanced"],
            index=1
        )
        
        learning_style = st.radio(
            "Preferred Learning Style",
            ["Visual", "Auditory", "Mixed"],
            index=2
        )
        
        language = st.selectbox(
            "Audio Language",
            ["English", "Cantonese (粵語)", "Mixed"]
        )
        
        if st.form_submit_button("💾 Save Profile"):
            st.session_state.student_profile = {
                "name": name,
                "subjects": subjects,
                "level": level,
                "learning_style": learning_style,
                "language": language
            }
            st.success("Profile saved successfully!")
    
    st.divider()
    
    st.subheader("🔧 System Settings")
    st.toggle("Dark Mode", value=False)
    st.toggle("Notifications", value=True)
    st.slider("Text Size", 10, 20, 14)


def main():
    """Main application entry point."""
    initialize_session_state()
    
    page = sidebar_navigation()
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Learn":
        learn_page()
    elif page == "Practice":
        practice_page()
    elif page == "Progress":
        progress_page()
    elif page == "Settings":
        settings_page()
    
    # Footer
    st.divider()
    st.markdown(
        "<p style='text-align: center; font-size: 0.8em; color: #666;'>"
        "EduLoop DSE - AI-Powered Mastery Learning | Powered by AWS Bedrock & MiniMax</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
