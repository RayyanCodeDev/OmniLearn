import streamlit as st
import os
import glob
from backend.ai_pipeline import analyze_image, grade_answer, chat_with_notes
from PIL import Image
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --- PROBLEM 1 FIX: Toggle in Main UI ---
col1, col2 = st.columns([8, 1])
with col2:
    theme_choice = st.toggle("Dark Mode", value=True)

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

# --- PROBLEM 2 FIX: Better Glassmorphism CSS ---
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

/* Glassmorphism Container */
[data-testid="stAppViewContainer"] > .main .block-container {{
    background: {glass_bg};
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 20px;
    border: {glass_border};
    padding: 2rem;
    margin-top: 2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}}

/* Glassy Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
.stTabs [data-baseweb="tab"] {{
    background: {glass_bg};
    border: {glass_border};
    border-radius: 10px;
    color: {text_color};
    padding: 10px 20px;
}}
.stTabs [aria-selected="true"] {{
    background: rgba(255, 255, 255, 0.2) !important;
    border-bottom: 2px solid #FF6B6B !important;
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
        
        notes = res.get('detailed_notes', 'No notes generated.')
        if isinstance(notes, dict):
            notes = "\n".join([f"- {v}" for k, v in notes.items()])
        
        with st.expander("📖 View Detailed Study Notes", expanded=True):
            st.markdown(notes)
            
        # --- PROBLEM 3 FIX: Graph Centering & Sizing ---
        st.write("### 🕸️ Concept Map")
        topic = res.get('topic', 'Main Topic')
        concepts = res.get("key_concepts", [])
        
        nodes = []
        edges = []
        
        nodes.append(Node(id=topic, label=topic, size=30, color="#FF6B6B", font={"color": "#ffffff", "size": 16}))
        
        for i, concept in enumerate(concepts):
            concept_id = f"{concept}_{i}"
            nodes.append(Node(id=concept_id, label=concept, size=20, color="#4ECDC4", font={"color": "#ffffff", "size": 14}))
            edges.append(Edge(source=topic, target=concept_id, type="CURVE_SMOOTH", color="#ffffff"))
            
        # Reduced width to 700 so it fits on screen, added physics stabilization
        config = Config(width=700, 
                        height=450, 
                        directed=True, 
                        physics=True, 
                        hierarchical=False,
                        nodeHighlightBehavior=True, 
                        highlightColor="#F7A7A6",
                        collapsible=False,
                        **{
                            "barnesHut": {
                                "gravitationalConstant": -3000,
                                "centralGravity": 0.3,
                                "springLength": 150
                            }
                        })
                        
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
