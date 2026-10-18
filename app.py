import streamlit as st
import os
import glob
from backend.ai_pipeline import analyze_image
from PIL import Image

st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

# --- HIDE STREAMLIT BRANDING ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stToolbar"] {visibility: hidden;}
            [data-testid="stStatusWidget"] {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🧠 OmniLearn")
st.subheader("Your AI-Powered Study Engine")

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Home",
    "📚 Capture Feed",
    "📝 Knowledge Graph",
    "⚙️ Gap Analysis & Quiz"
])

with tab1:
    st.header("Welcome to OmniLearn")
    st.write("OmniLearn passively captures your study materials, organizes them using AI, and tests you on what you don't know.")
    st.info("Go to the **Capture Feed** tab to upload a screenshot and see the magic!")

with tab2:
    st.header("📸 Capture Feed")
    st.write("Upload a screenshot of a lecture slide or WhatsApp message, and our AI will extract the concepts.")
    
    uploaded_file = st.file_uploader("Drag and drop a screenshot here (PNG, JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Save the uploaded file temporarily
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
            st.success("Analysis Complete!")
            st.write(f"**Subject:** {result.get('subject', 'Unknown')}")
            st.write(f"**Topic:** {result.get('topic', 'Unknown')}")
            st.write(f"**Summary:** {result.get('summary', '')}")
            st.write("**Key Concepts:**")
            for concept in result.get("key_concepts", []):
                st.info(concept)

with tab3:
    st.header("📝 Your Knowledge Graph")
    st.write("This is where the visual map of your learning will go.")
    
    # Quick check of local folder (for the hotkey script)
    SAVE_DIR = "data/test_screenshots"
    images = glob.glob(os.path.join(SAVE_DIR, "*.png"))
    st.write(f"**Total Screenshots in local database:** {len(images)}")
    st.info("Visual graph integration coming soon!")

with tab4:
    st.header("⚙️ Gap Analysis & Quiz")
    st.write("The AI will compare your notes to the syllabus and find what you are missing.")
    if st.button("Generate Quiz"):
        st.success("Quiz generation logic coming soon!")
