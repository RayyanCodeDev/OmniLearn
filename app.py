import streamlit as st
import os
import glob
from backend.ai_pipeline import analyze_image, grade_answer, chat_with_notes
from PIL import Image
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# --- PROBLEM 4 FIX: GLASSMORPHISM & THEME TOGGLE ---
theme_choice = st.sidebar.toggle("Dark Mode", value=True)
if theme_choice:
    bg_color = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    text_color = "#ffffff"
    glass_bg = "rgba(255, 255, 255, 0.05)"
    glass_border = "1px solid rgba(255, 255, 255, 0.1)"
else:
    bg_color = "linear-gradient(135deg, #e0eafc, #cfdef3)"
    text_color = "#1a1a1a"
    glass_bg = "rgba(255, 255, 255, 0.4)"
    glass_border = "1px solid rgba(255, 255, 255, 0.6)"

glass_css = f"""
<style>
/* Hide Streamlit Branding */
#MainMenu {{visibility: hidden;}} header {{visibility: hidden;}} [data-testid="stToolbar"] {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* Background Gradient */
.stApp {{
    background: {bg_color};
    color: {text_color};
}}

/* Glassmorphism Panels */
[data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"] {{
    background: {glass_bg};
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    border: {glass_border};
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    margin-bottom: 20px;
}}

/* Make Expanders Glassy */
.streamlit-expanderHeader {{
    background: transparent !important;
    color: {text_color} !important;
}}

/* Text Colors */
h1, h2, h3, h4, p, span, div {{ color: {text_color} !important; }}
</style>
"""
st.markdown(glass_css, unsafe_allow_html=True)

st.title("🧠 OmniLearn")
st.subheader("Your AI-Powered Study Engine")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Home", "📸 Capture Feed", "📝 Knowledge Graph", "⚙️ Smart Quiz", "💬 AI Tutor"
])

with tab1:
    st.header("Welcome to OmniLearn")
    st.write("Upload a screenshot to instantly generate notes, flashcards, quizzes, and chat with your notes.")

with tab2:
    st.header("📸 Capture Feed")
    uploaded_file = st.file_uploader("Upload a screenshot (PNG, JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        temp_path = "data/test_screenshots/temp_upload.png"
        os.makedirs("data/test_screenshots", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.image(uploaded_file, caption="Uploaded Screenshot", width=400)
        
        with st.spinner("🧠 Extracting knowledge and generating study materials..."):
            result = analyze_image(temp_path)
            
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.session_state.analysis_result = result
            st.success("Analysis Complete! Check the other tabs.")

with tab3:
    st.header("📝 Knowledge Graph & Notes")
    if st.session_state.analysis_result is None:
        st.warning("Please upload a screenshot in Tab 2 first.")
    else:
        res = st.session_state.analysis_result
        st.success(f"**Subject:** {res.get('subject')} | **Topic:** {res.get('topic')}")
        
        # PROBLEM 1 FIX: Clean Detailed Notes
        notes = res.get('detailed_notes', 'No notes generated.')
        if isinstance(notes, dict): # If AI returns a dict of indices, fix it
            notes = "\n".join([f"- {v}" for k, v in notes.items()])
        
        with st.expander("📖 View Detailed Study Notes", expanded=True):
            st.markdown(notes)
            
        # PROBLEM 2 & 3 FIX: Bigger Graph, White Text
        st.write("### 🕸️ Concept Map")
        topic = res.get('topic', 'Main Topic')
        concepts = res.get("key_concepts", [])
        
        nodes = []
        edges = []
        
        nodes.append(Node(id=topic, label=topic, size=30, color="#FF6B6B", font={"color": "#ffffff", "size": 16, "face": "arial"}))
        
        for i, concept in enumerate(concepts):
            concept_id = f"{concept}_{i}"
            nodes.append(Node(id=concept_id, label=concept, size=20, color="#4ECDC4", font={"color": "#ffffff", "size": 14, "face": "arial"}))
            edges.append(Edge(source=topic, target=concept_id, type="CURVE_SMOOTH", color="#ffffff"))
            
        config = Config(width=1000, 
                        height=500, 
                        directed=True, 
                        physics=True, 
                        hierarchical=False,
                        nodeHighlightBehavior=True, 
                        highlightColor="#F7A7A6",
                        collapsible=False)
                        
        agraph(nodes=nodes, edges=edges, config=config)
        
        st.write("### 🗂️ Auto-Generated Flashcards")
        cards = res.get("flashcards", [])
        for card in cards:
            with st.expander(f"❓ {card.get('front')}"):
                st.write(f"**Answer:** {card.get('back')}")

with tab4:
    st.header("⚙️ Feynman Technique Quiz")
    if st.session_state.analysis_result is None:
        st.warning("Please upload a screenshot in Tab 2 first.")
    else:
        res = st.session_state.analysis_result
        topic = res.get('topic', 'the topic')
        st.write(f"Explain **{topic}** in your own words. The AI will grade your understanding.")
        
        user_answer = st.text_area("Your Explanation:")
        if st.button("Grade My Answer"):
            if user_answer.strip():
                with st.spinner("Grading..."):
                    feedback = grade_answer(topic, user_answer)
                    st.success("Feedback:")
                    st.write(feedback)
            else:
                st.warning("Please type an answer first.")

with tab5:
    st.header("💬 AI Tutor (Chat with your Notes)")
    if st.session_state.analysis_result is None:
        st.warning("Please upload a screenshot in Tab 2 first.")
    else:
        res = st.session_state.analysis_result
        context = res.get("raw_text", res.get("summary", ""))
        
        st.write("Ask a question about the material, or ask the AI to explain it further:")
        user_question = st.text_input("Your Question:")
        
        if st.button("Ask AI"):
            if user_question.strip():
                with st.spinner("Thinking..."):
                    answer = chat_with_notes(user_question, context)
                    st.success("Answer:")
                    st.write(answer)
            else:
                st.warning("Please type a question first.")
