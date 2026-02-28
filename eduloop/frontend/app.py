"""Streamlit frontend application for EduLoop."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any, Optional

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
    """Display lesson content page."""
    st.title("📖 Learn with Your Personal Tutor")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Select Syllabus")
        syllabus = st.selectbox(
            "Syllabus",
            ["Math Foundation", "Math I", "Math II"]
        )
        
        # Dynamically change topics based on syllabus
        topics_map = {
            "Math Foundation": ["Quadratic Equations", "Functions", "Geometry", "Trigonometry"],
            "Math I": ["Calculus", "Probability", "Binomial Distribution"],
            "Math II": ["Matrix Algebra", "Vectors", "System of Linear Equations"]
        }
        
        topic = st.selectbox(
            "Topic",
            topics_map[syllabus]
        )
        
        if st.button("📝 Generate Lesson", use_container_width=True):
            with st.spinner("Retrieving DSE Database and creating personalized lesson..."):
                st.session_state.current_topic = f"{syllabus} - {topic}"
                st.success(f"Lesson on {topic} ready!")
    
    with col2:
        if st.session_state.current_topic:
            st.subheader(f"Lesson: {st.session_state.current_topic}")
            
            # Display lesson content structure
            tabs = st.tabs(["Concept", "Examples", "Key Points", "Audio"])
            
            with tabs[0]:
                st.write("### Introduction to the Topic")
                st.write("Welcome to this lesson! Here's what you'll learn...")
                st.write("- Core concepts and definitions")
                st.write("- Practical applications in HKDSE exams")
                st.write("- Problem-solving strategies")
            
            with tabs[1]:
                st.write("### Worked Examples")
                st.write("**Example 1:** Solve this equation...")
                st.code("Solution: Step-by-step breakdown...")
            
            with tabs[2]:
                st.write("### Key Takeaways")
                st.write("Remember these important points:")
                st.write("✓ Key concept 1")
                st.write("✓ Key concept 2")
                st.write("✓ Key concept 3")
            
            with tabs[3]:
                st.write("### Audio Narration")
                st.write("🔊 Click below to listen to the lesson:")
                st.info("Audio generation pending - will use MiniMax TTS with Cantonese support")


def practice_page():
    """Display assessment/practice page."""
    st.title("✏️ Practice & Assessment")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Start Assessment")
        syllabus = st.selectbox(
            "Syllabus Context",
            ["Math Foundation", "Math I", "Math II"]
        )
        
        topics_map = {
            "Math Foundation": ["Quadratic Equations", "Functions", "Geometry", "Trigonometry"],
            "Math I": ["Calculus", "Probability", "Binomial Distribution"],
            "Math II": ["Matrix Algebra", "Vectors", "System of Linear Equations"]
        }
        
        topic = st.selectbox(
            "Topic",
            topics_map[syllabus],
            key="practice_topic"
        )
        
        num_questions = st.slider("Number of Questions", 1, 10, 3)
        
        if st.button("🚀 Start Assessment", use_container_width=True):
            st.session_state.current_assessment = {
                "topic": topic,
                "syllabus": syllabus,
                "num_questions": num_questions,
                "started_at": datetime.now().isoformat()
            }
            st.success("Assessment started! Answer the questions below.")
    
    with col2:
        if "current_assessment" in st.session_state:
            assessment = st.session_state.current_assessment
            st.subheader(f"Assessment: {assessment['topic']} ({assessment['syllabus']})")
            st.info(f"{assessment['num_questions']} DSE-styled questions retrieved from RAG")
            
            # Display questions
            for i in range(1, assessment["num_questions"] + 1):
                with st.expander(f"Question {i}"):
                    st.write(f"[Sample question on {assessment['topic']}]")
                    answer = st.text_area(f"Your answer for Q{i}", key=f"answer_{i}")
                    
                    if st.button(f"Submit Q{i}", key=f"submit_{i}"):
                        st.success(f"✓ Submitted. Score: 7/10")
                        st.write("**Feedback:** Good attempt! Check your working...")
            
            if st.button("📊 View Full Report", use_container_width=True):
                st.switch_page("pages/progress.py")


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
