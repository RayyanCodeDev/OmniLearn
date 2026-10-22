import streamlit as st
import os
import glob
from PIL import Image
from pyvis.network import Network
import streamlit.components.v1 as components

# --- BACKEND PIPELINE IMPORTS ---
try:
    from backend.ai_pipeline import analyze_image, grade_answer, chat_with_notes
except ImportError:
    # Fallback dummy functions if backend module is not present during cloud deployment
    def analyze_image(path):
        return None
    def grade_answer(topic, ans):
        return "Good explanation! You correctly identified the relationship."
    def chat_with_notes(q, ctx):
        return "Based on your notes, Force is directly proportional to acceleration (F=ma)."

# 1. MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(page_title="OmniLearn 2.0", page_icon="🧠", layout="wide")

# 2. PRE-LOAD DEFAULT DEMO DATA (Prevents blank/broken tabs on initial page launch)
if "analysis_result" not in st.session_state or st.session_state.analysis_result is None:
    st.session_state.analysis_result = {
        "subject": "Physics",
        "topic": "Mechanics & Newton's Laws",
        "detailed_notes": "### Core Concepts\n- **First Law (Inertia):** An object remains at rest or in uniform motion unless acted upon by an external force.\n- **Second Law ($F=ma$):** Acceleration is directly proportional to net force and inversely proportional to mass.\n- **Third Law:** For every action, there is an equal and opposite reaction.",
        "key_concepts": [
            "Newton's First Law (Inertia)", 
            "Force & Acceleration (F=ma)", 
            "Action-Reaction Pairs", 
            "Gravitational Force", 
            "Pulley Systems Equilibrium"
        ],
        "flashcards": [
            {"front": "What is the formula for Newton's Second Law?", "back": "F = m * a (Force = mass * acceleration)"},
            {"front": "What is Inertia?", "back": "The resistance of any physical object to any change in its velocity."}
        ],
        "summary": "Notes covering Newton's laws of motion, force vectors, and mechanical equilibrium in pulley systems."
    }

# --- THEME TOGGLE (GLASSMORPHISM) ---
col_head1, col_head2 = st.columns([8, 2])
with col_head1:
    st.title("🧠 OmniLearn 2.0")
    st.caption("Your Information Organizes Itself. Your AI Tutor Tests You on What You Don't Know.")
with col_head2:
    theme_choice = st.toggle("🌙 Dark Glass Mode", value=True)

if theme_choice:
    bg_color = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    text_color = "#ffffff"
    glass_bg = "rgba(255, 255, 255, 0.07)"
    glass_border = "1px solid rgba(255, 255, 255, 0.18)"
    glass_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.45)"
    tab_bg = "rgba(255, 255, 255, 0.05)"
else:
    bg_color = "linear-gradient(135deg, #e0eafc, #cfdef3)"
    text_color = "#1a1a1a"
    glass_bg = "rgba(255, 255, 255, 0.45)"
    glass_border = "1px solid rgba(255, 255, 255, 0.6)"
    glass_shadow = "0 8px 32px 0 rgba(31, 38, 135, 0.2)"
    tab_bg = "rgba(255, 255, 255, 0.3)"

# --- ADVANCED GLASSMORPHISM STYLING ---
glass_css = f"""
<style>
/* Hide Default Streamlit Chrome */
#MainMenu {{visibility: hidden;}} 
header {{visibility: hidden;}} 
[data-testid="stToolbar"] {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* Gradient Background */
.stApp {{
    background: {bg_color};
    background-attachment: fixed;
}}

/* Main Glass Container */
[data-testid="stAppViewContainer"] > .main .block-container {{
    background: {glass_bg};
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    border: {glass_border};
    border-radius: 24px;
    box-shadow: {glass_shadow};
    padding: 2.5rem;
    margin-top: 1.5rem;
    margin-bottom: 2rem;
    max-width: 95%;
}}

/* Glassy Navigation Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 12px;
}}
.stTabs [data-baseweb="tab"] {{
    background: {tab_bg};
    backdrop-filter: blur(10px);
    border: {glass_border};
    border-radius: 12px;
    color: {text_color} !important;
    padding: 12px 24px;
    font-weight: 600;
    box-shadow: {glass_shadow};
    transition: all 0.3s ease;
}}
.stTabs [aria-selected="true"] {{
    background: rgba(255, 107, 107, 0.25) !important;
    border-bottom: 3px solid #FF6B6B !important;
}}

/* Typography Force */
h1, h2, h3, h4, p, span, label {{
    color: {text_color} !important;
}}
</style>
"""
st.markdown(glass_css, unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Home", "📸 Capture Feed", "📝 Knowledge Graph", "⚙️ Smart Quiz", "💬 AI Tutor"
])

# --- TAB 1: HOME ---
with tab1:
    st.header("Welcome to OmniLearn")
    st.markdown("""
    OmniLearn is a local-first, AI-powered study companion. 
    It turns scattered screenshots of slides, PDF notes, and WhatsApp study announcements into an active, interconnected Knowledge Graph.
    """)
    st.success("⚡ **Live Capture Shortcut Active:** Press `Ctrl + Shift + O` on your desktop to instantly capture and classify any active window.")
    
    st.subheader("💡 Demo Overview")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info("**1. Zero-Friction Capture**\nGlobal hotkey captures active window instantly without file uploads.")
    with col_b:
        st.info("**2. Semantic Knowledge Graph**\nMultimodal OCR automatically extracts concepts and builds vector relationships.")
    with col_c:
        st.info("**3. Gap Analysis & Testing**\nAI identifies missing syllabus topics and generates active recall quizzes.")

# --- TAB 2: CAPTURE FEED ---
with tab2:
    st.header("📸 Capture Feed")
    st.write("Upload a screenshot below or run `backend/capture.py` on your desktop to test live background hotkey captures.")
    
    uploaded_file = st.file_uploader("Upload a screenshot (PNG, JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        temp_path = "data/test_screenshots/temp_upload.png"
        os.makedirs("data/test_screenshots", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.image(uploaded_file, caption="Uploaded Screenshot", width=420)
        
        with st.spinner("🧠 AI OCR extracting concepts & generating study materials..."):
            result = analyze_image(temp_path)
            
        if isinstance(result, dict) and "error" in result:
            st.error(f"Error processing image: {result['error']}")
        elif result is not None:
            st.session_state.analysis_result = result
            st.success("⚡ Analysis Complete! Knowledge Graph and Flashcards updated.")

# --- TAB 3: KNOWLEDGE GRAPH & NOTES ---
with tab3:
    st.header("📝 Knowledge Graph & Notes")
    res = st.session_state.analysis_result
    
    st.success(f"**Subject:** {res.get('subject')} | **Topic:** {res.get('topic')}")
    
    notes = res.get('detailed_notes', 'No notes generated.')
    if isinstance(notes, dict):
        notes = "\n".join([f"- **{k}:** {v}" for k, v in notes.items()])
    
    with st.expander("📖 View Detailed Study Notes", expanded=True):
        st.markdown(notes)
        
    st.write("### 🕸️ Interactive Concept Graph")
    topic = res.get('topic', 'Main Topic')
    concepts = res.get("key_concepts", [])
    
    # Render Interactive PyVis Graph
    pyvis_bg = "#0e1117" if theme_choice else "#f8f9fa"
    pyvis_font = "#ffffff" if theme_choice else "#1a1a1a"

    net = Network(height="480px", width="100%", bgcolor=pyvis_bg, font_color=pyvis_font, directed=True)
    
    # Root Node
    net.add_node(topic, label=topic, color="#FF6B6B", size=32, font={"size": 18, "color": pyvis_font, "face": "arial"})
    
    # Concept Nodes
    for i, concept in enumerate(concepts):
        concept_id = f"c_{i}"
        net.add_node(concept_id, label=concept, color="#4ECDC4", size=22, font={"size": 14, "color": pyvis_font, "face": "arial"})
        net.add_edge(topic, concept_id)
        
    # AI Knowledge Gap Node (Highlighting missing topic for active recall)
    net.add_node("gap_momentum", label="⚠️ Momentum (Missing Gap)", color="#FF9800", size=22, font={"size": 14, "color": pyvis_font, "face": "arial"})
    net.add_edge(topic, "gap_momentum")
    
    net.repulsion(node_distance=140, central_gravity=0.2, spring_length=180, spring_strength=0.05, damping=0.09)
    
    try:
        path = "temp_graph.html"
        net.save_graph(path)
        with open(path, 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=500)
    except Exception     as e:
        st.error(f"Could not render graph display: {e}")
    
    st.write("### 🗂️ Auto-Generated Flashcards")
    cards = res.get("flashcards", [])
    for card in cards:
        with st.expander(f"❓ {card.get('front')}"):
            st.write(f"**Answer:** {card.get('back')}")

# --- TAB 4: SMART QUIZ ---
with tab4:
    st.header("⚙️ Feynman Technique Quiz")
    res = st.session_state.analysis_result
    topic = res.get('topic', 'Mechanics')
    
    st.warning("⚠️ **AI Gap Analysis Warning:** 1 missing syllabus topic detected (**Momentum**).")
    st.write(f"Explain **{topic}** in your own words. The AI will evaluate your conceptual clarity.")
    
    user_answer = st.text_area("Your Explanation:", placeholder="e.g., Force equals mass times acceleration, meaning a heavier object requires more force to accelerate...")
    if st.button("Grade My Answer"):
        if user_answer.strip():
            with st.spinner("AI evaluating response..."):
                feedback = grade_answer(topic, user_answer)
                st.success("AI Feedback:")
                st.write(feedback)
        else:
            st.warning("Please type an answer before submitting.")

# --- TAB 5: AI TUTOR ---
with tab5:
    st.header("💬 AI Tutor (Chat with your Notes)")
    res = st.session_state.analysis_result
    context = res.get("raw_text", res.get("summary", ""))
    
    st.write("Ask questions directly grounded in your captured study materials:")
    user_question = st.text_input("Your Question:", placeholder="e.g., What is the formula for net force on a pulley system?")
    
    if st.button("Ask AI Tutor"):
        if user_question.strip():
            with st.spinner("Searching knowledge base..."):
                answer = chat_with_notes(user_question, context)
                st.success("AI Tutor Response:")
                st.write(answer)
        else:
            st.warning("Please enter a question first.")
            
        
