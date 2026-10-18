import streamlit as st
import os
import glob
from backend.ai_pipeline import analyze_image
from PIL import Image

st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

# --- STORAGE: PRESERVE DATA DURING TAB SWITCHING ---
if "courses" not in st.session_state:
    st.session_state.courses = []
if "notes" not in st.session_state:
    st.session_state.notes = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --- HIDE STREAMLIT BRANDING ---
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
.stAppToolbar {display: none;}
[data-testid="stStatusWidget"] {visibility: hidden;}
[data-testid="stDecoration"] {display: none;}
.viewerBadge_container__1QSob {display: none;}
.stActionButton {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🧠 OmniLearn")
st.subheader("Your AI-Powered Study Engine")

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Home",
    "📸 Capture Feed",
    "📝 Knowledge Graph",
    "⚙️ Gap Analysis & Quiz"
])

# --- TAB 1: HOME ---
with tab1:
    st.header("My Courses")
    new_course = st.text_input("Enter a course or subject", key="new_course_input")

    if st.button("Add Course"):
        if new_course.strip():
            st.session_state.courses.append(new_course.strip())
            st.rerun()

    if st.session_state.courses:
        for i, course in enumerate(st.session_state.courses):
            st.write(f"📚 {course}")
    else:
        st.info("Your subjects and courses will appear here.")

# --- TAB 2: CAPTURE FEED (AI INTEGRATION) ---
with tab2:
    st.header("📸 Capture Feed")
    st.write("Upload a screenshot of a lecture slide or WhatsApp message.")

    uploaded_file = st.file_uploader("Drag and drop a screenshot (PNG, JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        temp_path = "data/test_screenshots/temp_upload.png"
        os.makedirs("data/test_screenshots", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.image(uploaded_file, caption="Uploaded Screenshot", width=400)
        
        with st.spinner("🧠 Analyzing with AI..."):
            result = analyze_image(temp_path)
            
        if "error" in result:
            st.error("Could not analyze the image.")
        else:
            st.session_state.analysis_result = result
            st.success("Analysis Complete! Click on Tab 3 to see the Knowledge Graph.")

# --- TAB 3: KNOWLEDGE GRAPH ---
with tab3:
    st.header("📝 Your Knowledge Graph")
    if st.session_state.analysis_result is None:
        st.warning("Please upload a screenshot in Tab 2 first.")
    else:
        res = st.session_state.analysis_result
        st.success(f"**Subject:** {res.get('subject')} | **Topic:** {res.get('topic')}")
        st.write(f"**Summary:** {res.get('summary')}")
        
        st.write("### Key Concepts Detected")
        for concept in res.get("key_concepts", []):
            st.info(concept)
            

# --- TAB 4: GAP ANALYSIS & QUIZ ---
with tab4:
    st.header("⚙️ Gap Analysis & Quiz")
    if st.session_state.analysis_result is None:
        st.warning("Please upload a screenshot in Tab 2 first.")
    else:
        res = st.session_state.analysis_result
        st.write(f"Let's test your knowledge on **{res.get('topic')}**.")
        if st.button("Generate Quiz Question"):
            st.info(f"**Question:** Explain the concept of {res.get('key_concepts')[0]} in your own words.")
            st.text_area("Your Answer")
            st.button("Submit Answer")
