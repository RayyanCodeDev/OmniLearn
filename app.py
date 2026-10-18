import streamlit as st
import os
import glob
from backend.ai_pipeline import analyze_image
from PIL import Image

st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

# Hide default Streamlit branding
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stToolbar"] {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🧠 OmniLearn")
st.subheader("Your AI-Powered Study Engine")

# The folder where capture.py saves images
SAVE_DIR = "data/test_screenshots"

if st.button("🔄 Refresh Knowledge Graph"):
    st.rerun()

# Find all images in the folder
images = glob.glob(os.path.join(SAVE_DIR, "*.png"))
# Sort by newest first
images.sort(key=os.path.getmtime, reverse=True)

st.write(f"**Total Concepts Captured:** {len(images)}")

if len(images) == 0:
    st.info("No screenshots captured yet. Run `python backend/capture.py` and press Ctrl+Shift+O to capture your first slide!")
else:
    # Show the most recent capture
    latest_image = images[0]
    st.write("### Latest Capture")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(latest_image, caption="Captured Screenshot", use_container_width=True)
        
    with col2:
        with st.spinner("🧠 AI is analyzing the latest screenshot..."):
            result = analyze_image(latest_image)
            
        if "error" not in result:
            st.success("Analysis Complete!")
            st.write(f"**Subject:** {result.get('subject', 'Unknown')}")
            st.write(f"**Topic:** {result.get('topic', 'Unknown')}")
            st.write(f"**Summary:** {result.get('summary', '')}")
            
            st.write("**Key Concepts:**")
            for concept in result.get("key_concepts", []):
                st.info(concept)