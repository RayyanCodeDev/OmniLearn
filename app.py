import streamlit as st
import os
import glob
from backend.ai_pipeline import analyze_image, grade_answer, chat_with_notes
from PIL import Image

st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

hide_st_style = """
<style>
#MainMenu {visibility: hidden;} header {visibility: hidden;} [data-testid="stToolbar"] {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🧠 OmniLearn")
st.subheader("Your AI-Powered Study Engine")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Home", "📸 Capture Feed", "📝 Knowledge Graph", "⚙️ Smart Quiz", "💬 AI Tutor"
])

with tab1:
    st.header("Welcome to OmniLearn")
    st.write("Upload a screenshot to instantly generate notes, flashcards, and quizzes.")

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
        
        # FEATURE 5: Detailed Notes
        with st.expander("📖 View Detailed Study Notes", expanded=True):
            st.write(res.get('detailed_notes', 'No detailed notes generated.'))
            
        # FEATURE 4: Visual Graph Placeholder (Huzaifa will upgrade this)
        st.write("### 🕸️ Concept Map")
        concepts = res.get("key_concepts", [])
        st.info(f"**Core Topic:** {res.get('topic')} \n\n **Linked Concepts:** {', '.join(concepts)}")
        st.caption("*(Huzaifa: Replace this with a visual `streamlit-agraph` map)*")
        
        # FEATURE 3: Flashcards
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
        
        st.write("Ask a question about the material you just uploaded:")
        user_question = st.text_input("Your Question:")
        
        if st.button("Ask AI"):
            if user_question.strip():
                with st.spinner("Thinking..."):
                    answer = chat_with_notes(user_question, context)
                    st.success("Answer:")
                    st.write(answer)
            else:
                st.warning("Please type a question first.")
