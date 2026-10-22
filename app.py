import streamlit as st
import os
import glob
from backend.ai_pipeline import analyze_image, grade_answer, chat_with_notes
from PIL import Image
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --- THEME TOGGLE ---
col1, col2 = st.columns([8, 1])
with col2:
    theme_choice = st.toggle("Dark Mode", value=True)

if theme_choice:
    bg_color = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    text_color = "#ffffff"
    glass_bg = "rgba(255, 255, 255, 0.05)"
    glass_border = "1px solid rgba(255, 255, 255, 0.15)"
    glass_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
else:
    bg_color = "linear-gradient(135deg, #e0eafc, #cfdef3)"
    text_color = "#1a1a1a"
    glass_bg = "rgba(255, 255, 255, 0.4)"
    glass_border = "1px solid rgba(255, 255, 255, 0.6)"
    glass_shadow = "0 8px 32px 0 rgba(31, 38, 135, 0.37)"

# --- AGGRESSIVE GLASSMORPHISM CSS ---
glass_css = f"""
<style>
/* Hide Streamlit Branding */
#MainMenu {{visibility: hidden;}} header {{visibility: hidden;}} [data-testid="stToolbar"] {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* The Background */
.stApp {{
    background: {bg_color};
    background-attachment: fixed;
}}

/* The Glassmorphism Card */
[data-testid="stAppViewContainer"] > .main .block-container {{
    background: {glass_bg};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: {glass_border};
    border-radius: 24px;
    box-shadow: {glass_shadow};
    padding: 3rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
    max-width: 95%;
}}

/* Glassy Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
.stTabs [data-baseweb="tab"] {{
    background: {glass_bg};
    border: {glass_border};
    border-radius: 12px;
    color: {text_color};
    padding: 10px 20px;
    box-shadow: {glass_shadow};
}}
.stTabs [aria-selected="true"] {{
    background: rgba(255, 255, 255, 0.15) !important;
    border-bottom: 2px solid #FF6B6B !important;
}}

/* Force Text Color */
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
    st.write("Upload a screenshot or use your global hotkey to instantly generate notes, flashcards, quizzes, and chat with your notes.")
    st.info("💡 **Demo Tip:** Use the Capture Feed tab to test the OCR and AI knowledge extraction pipeline live.")

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
            
        if isinstance(result, dict) and "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.session_state.analysis_result = result
            st.success("Analysis Complete! Check the Knowledge Graph and Quiz tabs.")

with tab3:
    st.header("📝 Knowledge Graph & Notes")
    if st.session_state.analysis_result is None:
        st.warning("Please upload a screenshot in the **Capture Feed** tab first.")
    else:
        res = st.session_state.analysis_result
        st.success(f"**Subject:** {res.get('subject')} | **Topic:** {res.get('topic')}")
        
        notes = res.get('detailed_notes', 'No notes generated.')
        if isinstance(notes, dict):
            notes = "\n".join([f"- {v}" for k, v in notes.items()])
        
        with st.expander("📖 View Detailed Study Notes", expanded=True):
            st.markdown(notes)
            
        st.write("### 🕸️ Concept Map")
        topic = res.get('topic', 'Main Topic')
        concepts = res.get("key_concepts", [])
        
        # --- PYVIS GRAPH CONFIG ---
        pyvis_bg = "#0e1117" if theme_choice else "#ffffff"
        pyvis_font = "#ffffff" if theme_choice else "#000000"

        net = Network(height="500px", width="100%", bgcolor=pyvis_bg, font_color=pyvis_font, directed=True)
        
        net.add_node(topic, label=topic, color="#FF6B6B", size=35, font={"size": 18, "color": pyvis_font, "face": "arial"})
        for i, concept in enumerate(concepts):
            concept_id = f"c_{i}"
            net.add_node(concept_id, label=concept, color="#4ECDC4", size=25, font={"size": 16, "color": pyvis_font, "face": "arial"})
            net.add_edge(topic, concept_id)
        
        net.repulsion(node_distance=150, central_gravity=0.2, spring_length=200, spring_strength=0.05, damping=0.09)
        
        try:
            path = "temp_graph.html"
            net.save_graph(path)
            with open(path, 'r', encoding='utf-8') as f:
                html_data = f.read()
            components.html(html_data, height=520)
        except Exception as e:
            st.error(f"Could not generate graph: {e}")
        
        st.write("### 🗂️ Auto-Generated Flashcards")
        cards = res.get("flashcards", [])
        for card in cards:
            with st.expander(f"❓ {card.get('front')}"):
                st.write(f"**Answer:** {card.get('back')}")

with tab4:
    st.header("⚙️ Feynman Technique Quiz")
    if st.session_state.analysis_result is None:
        st.warning("Please upload a screenshot in the **Capture Feed** tab first.")
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
        st.warning("Please upload a screenshot in the **Capture Feed** tab first.")
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
                
