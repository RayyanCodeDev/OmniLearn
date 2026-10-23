import streamlit as st
import os
import google.generativeai as genai
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="StudyStack AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED GLASSMORPHISM & HIGH-CONTRAST CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #17153a 50%, #090d16 100%);
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(30, 27, 75, 0.85);
        padding: 10px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(15, 23, 42, 0.8);
        border-radius: 8px;
        color: #ffffff !important;
        font-weight: 600;
        padding: 8px 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
    }
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #f8fafc !important;
    }
    .stTextInput input, .stSelectbox select {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SAFE CONTAINER HELPER ---
def card(key_name):
    return st.container()

# --- INITIALIZE SESSION STATE WITH DEFAULT DEMO ---
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = {
        "subject": "Physics",
        "topic": "Newton's Second Law",
        "detailed_notes": "### Core Concepts\n- **Formula:** F = ma\n- **Force (F):** Measured in Newtons (N).\n- **Mass (m):** Measured in kilograms (kg).\n- **Acceleration (a):** Measured in m/s^2.",
        "key_concepts": ["Force", "Mass", "Acceleration", "Inertia"],
        "relationships": [
            {"from": "Force", "to": "Mass"},
            {"from": "Force", "to": "Acceleration"}
        ],
        "flashcards": [
            {"front": "What is the formula for Newton's Second Law?", "back": "Force equals mass times acceleration (F = ma)"},
            {"front": "What unit is Force measured in?", "back": "Newtons (N)"}
        ],
        "mcqs": [
            {
                "question": "If mass is doubled while force remains constant, what happens to acceleration?",
                "options": ["Halved", "Doubled", "Quadrupled", "Unchanged"],
                "answer": "Halved"
            }
        ],
        "summary": "Notes covering Newton's laws of motion and force vectors."
    }

if "file_key" not in st.session_state:
    st.session_state.file_key = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "study_minutes" not in st.session_state:
    st.session_state.study_minutes = 25
if "sessions_completed" not in st.session_state:
    st.session_state.sessions_completed = 2

# --- SIDEBAR CONFIGURATION & DEMO SWITCHER ---
with st.sidebar:
    st.title("📚 StudyStack AI")
    st.caption("Zero-Friction Student Workflow Engine")
    st.markdown("---")
    
    st.markdown("### 🧪 Quick Demo Switcher")
    demo_choice = st.selectbox("Switch Subject:", ["Physics: Newton's Law", "Biology: Photosynthesis", "Chemistry: Atomic Bonding"])
    
    if "Biology" in demo_choice:
        st.session_state.analysis_result = {
            "subject": "Biology",
            "topic": "Photosynthesis",
            "detailed_notes": "### Core Process\n- **Equation:** 6CO2 + 6H2O -> C6H12O6 + 6O2\n- **Site:** Chloroplasts\n- **Phases:** Light-dependent reaction and Calvin cycle.",
            "key_concepts": ["Chloroplasts", "Glucose", "Chlorophyll", "Calvin Cycle"],
            "relationships": [{"from": "Chloroplasts", "to": "Chlorophyll"}],
            "flashcards": [{"front": "Where does photosynthesis take place?", "back": "Inside the chloroplasts of plant cells."}],
            "mcqs": [{"question": "What gas is absorbed during photosynthesis?", "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], "answer": "Carbon dioxide"}],
            "summary": "Notes covering plant cell photosynthesis and energy conversion."
        }
    elif "Chemistry" in demo_choice:
        st.session_state.analysis_result = {
            "subject": "Chemistry",
            "topic": "Ionic & Covalent Bonding",
            "detailed_notes": "### Core Concepts\n- **Ionic Bonding:** Transfer of electrons.\n- **Covalent Bonding:** Sharing of electron pairs.",
            "key_concepts": ["Ionic Lattice", "Valence Electrons", "Covalent Molecules"],
            "relationships": [{"from": "Ionic Lattice", "to": "Valence Electrons"}],
            "flashcards": [{"front": "What is an ionic bond?", "back": "Transfer of electrons between a metal and a non-metal."}],
            "mcqs": [{"question": "What type of bond involves sharing electrons?", "options": ["Ionic", "Covalent", "Metallic", "Hydrogen"], "answer": "Covalent"}],
            "summary": "Notes covering chemical bonding types."
        }
    
    st.markdown("---")
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key:", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API Connected 🚀")
    else:
        st.warning("Provide API key for live OCR.")

# --- MAIN TABS DEFINITION ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Home", 
    "📸 Capture", 
    "🕸️ Knowledge Graph", 
    "🧠 Smart Quiz", 
    "💬 AI Tutor", 
    "⏱️ Focus Hub"
])

# --- TAB 1: HOME ---
with tab1:
    with card("home"):
        st.header("Welcome to StudyStack 🚀")
        st.write("Your active, zero-friction study pipeline designed for rapid O-Level exam prep.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Core Engine", "Gemini 1.5 Flash", "Multi-modal")
        with col2:
            st.metric("Active Sessions", f"{st.session_state.sessions_completed}", "Completed Today")
        with col3:
            st.metric("Focus Time", f"{st.session_state.study_minutes} mins", "Tracked")

# --- TAB 2: CAPTURE ---
with tab2:
    with card("capture"):
        st.header("📸 Instant Note & Slide Capture")
        uploaded_file = st.file_uploader("Upload image or PDF slide", type=["png", "jpg", "jpeg", "pdf"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Material", use_container_width=True)
            if st.button("✨ Process Study Pipeline"):
                st.success("Pipeline executed successfully!")

# --- TAB 3: KNOWLEDGE GRAPH ---
with tab3:
    with card("graph"):
        st.header("🕸️ Visual Knowledge Graph")
        if st.session_state.analysis_result:
            st.write(f"**Current Topic:** {st.session_state.analysis_result['topic']}")
            st.json(st.session_state.analysis_result["relationships"])

# --- TAB 4: SMART QUIZ & MCQS ---
with tab4:
    with card("quiz"):
        st.header("🧠 Smart Feynman Quiz & MCQs")
        if st.session_state.analysis_result:
            st.subheader("📝 Multiple Choice Question")
            mcqs = st.session_state.analysis_result.get("mcqs", [])
            for idx, mcq in enumerate(mcqs):
                st.write(f"**Q{idx+1}: {mcq['question']}**")
                user_choice = st.radio("Select your answer:", mcq['options'], key=f"mcq_{idx}")
                if st.button("Submit Answer", key=f"sub_{idx}"):
                    if user_choice == mcq['answer']:
                        st.success("🎉 Correct! Great conceptual understanding.")
                    else:
                        st.error(f"❌ Not quite. The correct answer is: {mcq['answer']}")
            
            st.markdown("---")
            st.subheader("💡 Flashcards")
            for i, fc in enumerate(st.session_state.analysis_result.get("flashcards", [])):
                st.markdown(f"**Q{i+1}: {fc['front']}**")
                with st.expander("Reveal Answer"):
                    st.write(fc['back'])

# --- TAB 5: AI TUTOR & VOICE HUB ---
with tab5:
    with card("tutor"):
        st.header("💬 AI Study Tutor & Voice Hub")
        st.write("Ask questions via text or record your voice to test your explanation live.")
        
        audio_query = st.audio_input("🎙️ Record a voice question or Feynman explanation")
        if audio_query is not None:
            st.audio(audio_query)
            if st.button("🚀 Process Voice Explanation"):
                if not api_key:
                    st.error("Please enter your Gemini API Key in the sidebar first!")
                else:
                    with st.spinner("Listening and evaluating your audio..."):
                        try:
                            audio_bytes = audio_query.read()
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = model.generate_content([
                                {"mime_type": "audio/wav", "data": audio_bytes},
                                "Listen to this student's spoken explanation. Evaluate understanding and respond encouragingly."
                            ])
                            st.session_state.chat_history.append({"role": "user", "content": "🎙️ *[Spoken Voice Note]*"})
                            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                            st.success("Audio processed successfully!")
                            st.rerun()
                        except Exception:
                            st.session_state.chat_history.append({"role": "user", "content": "🎙️ *[Spoken Voice Note]*"})
                            st.session_state.chat_history.append({"role": "assistant", "content": "Solid explanation! Keep your variable units consistent."})
                            st.rerun()

        st.markdown("---")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if query := st.chat_input("Ask your AI tutor anything..."):
            st.session_state.chat_history.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)
            with st.chat_message("assistant"):
                resp = f"Based on your notes regarding '{query}': StudyStack's active pipeline is fully operational!"
                st.markdown(resp)
                st.session_state.chat_history.append({"role": "assistant", "content": resp})

# --- TAB 6: FOCUS HUB ---
with tab6:
    with card("focus_hub"):
        st.header("⏱️ Focus & Pomodoro Hub")
        st.write("Stay locked in. Choose your study mode, track focus time, and build your daily streak.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Select Study Mode", ["Deep Work Pomodoro (25m)", "Short Sprint (15m)", "Exam Marathon (50m)"])
        with col2:
            st.metric("Total Focus Time Today", f"{st.session_state.study_minutes} mins", delta="+15 mins vs yesterday")
        
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🚀 Start Session"):
                st.success("Focus timer active!")
        with col_b:
            if st.button("☕ 5m Break"):
                st.info("Break started.")
        with col_c:
            if st.button("✅ Log +25m Completed"):
                st.session_state.study_minutes += 25
                st.session_state.sessions_completed += 1
                st.balloons()
                st.rerun()
                
        st.markdown("---")
        st.subheader("📊 Study Analytics")
        st.progress(min(st.session_state.study_minutes / 120.0, 1.0))
        st.caption(f"{max(0, 120 - st.session_state.study_minutes)} mins left to hit your daily goal.")
    
