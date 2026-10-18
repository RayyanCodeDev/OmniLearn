import streamlit as st

st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

# --- AGGRESSIVE CSS TO HIDE ALL STREAMLIT BRANDING ---
hide_st_style = """
            <style>
            /* Hide the top header and main menu */
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Hide the top-right toolbar (Fork, GitHub icon, etc.) */
            [data-testid="stToolbar"] {visibility: hidden;}
            .stAppToolbar {display: none;}
            
            /* Hide the bottom-right "Hosted with Streamlit" badge and status widget */
            [data-testid="stStatusWidget"] {visibility: hidden;}
            [data-testid="stDecoration"] {display: none;}
            .viewerBadge_container__1QSob {display: none;}
            .stActionButton {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# -----------------------------------------------------

st.title("🧠 OmniLearn")
st.subheader("Your AI-Powered Study Engine")
st.success("Live Deployment Pipeline Test Successful! GitHub is linked to Streamlit.")
