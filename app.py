import streamlit as st

# 1. Page config MUST be the first Streamlit command
st.set_page_config(page_title="OmniLearn", page_icon="🧠", layout="wide")

# 2. Hide the default Streamlit branding (Fork button, menu, footer)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. Your actual app content
st.title("🧠 OmniLearn")
st.subheader("Your AI-Powered Study Engine")

st.success("Live Deployment Pipeline Test Successful! GitHub is linked to Streamlit.")

st.write("---")
st.write("**(This placeholder text will be replaced by Member 2's UI and Member 3's AI pipeline soon.)**")
