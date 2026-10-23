import textwrap
import streamlit as st
from backend.ai_pipeline import analyze_image, grade_answer, chat_with_notes

st.set_page_config(page_title="StudyStack", page_icon="📚", layout="wide")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "file_key" not in st.session_state:
    st.session_state.file_key = None

# ---------- THEME ----------
_, toggle_col = st.columns([8, 1])
with toggle_col:
    dark = st.toggle("Dark mode", value=True)

THEMES = {
    True: dict(
        TEXT="#f2f5ff", MUTED="#aab4d4", GLASS="rgba(255,255,255,0.07)", GLASS2="rgba(255,255,255,0.10)",
        BORDER="rgba(255,255,255,0.20)", SHADOW="0 10px 40px rgba(0,0,0,0.45)", GLOW="rgba(124,140,255,0.35)",
        BASE="#080b1a", O1="rgba(124,92,255,0.55)", O2="rgba(0,200,255,0.40)", O3="rgba(255,90,140,0.40)",
    ),
    False: dict(
        TEXT="#14182b", MUTED="#4a5273", GLASS="rgba(255,255,255,0.55)", GLASS2="rgba(255,255,255,0.75)",
        BORDER="rgba(255,255,255,0.95)", SHADOW="0 10px 40px rgba(70,80,160,0.20)", GLOW="rgba(124,140,255,0.45)",
        BASE="#e9eeff", O1="rgba(150,120,255,0.55)", O2="rgba(80,200,255,0.50)", O3="rgba(255,150,180,0.50)",
    ),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');
:root{--text:__TEXT__;--muted:__MUTED__;--glass:__GLASS__;--glass2:__GLASS2__;--border:__BORDER__;--shadow:__SHADOW__;--glow:__GLOW__;}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}

/* Backdrop: colored light orbs give the glass something to blur */
.stApp{
  background:
    radial-gradient(circle at 12% 18%, __O1__ 0, transparent 38%),
    radial-gradient(circle at 88% 8%,  __O2__ 0, transparent 36%),
    radial-gradient(circle at 70% 92%, __O3__ 0, transparent 40%),
    __BASE__;
  background-attachment:fixed;
  font-family:'Plus Jakarta Sans',sans-serif;
}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp li,.stApp label,.stApp summary,
.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"]{color:var(--text);font-family:'Plus Jakarta Sans',sans-serif;}
.stApp h1{font-weight:800;letter-spacing:-0.02em;}

/* Frosted glass cards (containers created with key="card_*") */
[class*="st-key-card"]{
  background:linear-gradient(145deg,var(--glass2),var(--glass));
  backdrop-filter:blur(22px) saturate(160%);-webkit-backdrop-filter:blur(22px) saturate(160%);
  border:1px solid var(--border)!important;border-radius:24px!important;
  box-shadow:var(--shadow),0 0 0 1px var(--glow),inset 0 1px 0 rgba(255,255,255,0.35);
  padding:1.4rem 1.6rem!important;margin-bottom:1.1rem;
}

/* Pill tabs */
.stTabs [data-baseweb="tab-list"]{gap:8px;padding:6px;background:var(--glass);border:1px solid var(--border);
  border-radius:999px;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);box-shadow:var(--shadow);width:fit-content;max-width:100%;overflow-x:auto;}
.stTabs [data-baseweb="tab"]{background:transparent;border-radius:999px;padding:8px 18px;height:auto;}
.stTabs [data-baseweb="tab"] p{color:var(--muted);font-weight:600;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#7c5cff,#00c8ff)!important;box-shadow:0 0 22px var(--glow);}
.stTabs [aria-selected="true"] p{color:#fff!important;}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}

/* Expanders, inputs, alerts, uploader */
[data-testid="stExpander"]{background:var(--glass);border:1px solid var(--border)!important;border-radius:16px!important;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);}
[data-testid="stExpander"] summary{font-weight:600;}
.stTextArea textarea,.stTextInput input{background:var(--glass2)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:14px!important;}
[data-testid="stFileUploaderDropzone"]{background:var(--glass2);border:1.5px dashed var(--border);border-radius:18px;}
[data-testid="stFileUploaderDropzone"] *{color:var(--text)!important;}
[data-testid="stAlert"]{background:var(--glass2);border:1px solid var(--border);border-radius:16px;backdrop-filter:blur(14px);}
.stButton>button{background:linear-gradient(135deg,#7c5cff,#00c8ff);color:#fff;border:0;border-radius:999px;padding:.55rem 1.6rem;font-weight:700;box-shadow:0 0 22px var(--glow);}
.stButton>button:hover{filter:brightness(1.12);color:#fff;}

/* Center the concept map */
[data-testid="stGraphVizChart"]{display:flex;justify-content:center;}
[data-testid="stGraphVizChart"] svg{margin:0 auto;max-width:100%;height:auto;}
</style>
"""
css = CSS
for k, v in THEMES[dark].items():
    css = css.replace(f"__{k}__", v)
st.markdown(css, unsafe_allow_html=True)


def card(name):
    return st.container(border=True, key=f"card_{name}")


# ---------- CONCEPT MAP ----------
def build_dot(topic, concepts, links):
    esc = lambda s: str(s).replace('"', "'").replace("\\", "")
    wrap = lambda s, w=16: "\\n".join(textwrap.wrap(esc(s), w)) or " "

    lines = [
        "graph G {",
        '  graph [bgcolor="transparent", overlap=false, splines=true, ranksep=1.6, root="topic", pad=0.3];',
        '  node  [shape=ellipse, style=filled, penwidth=0, fontname="Helvetica-Bold", fontsize=13, fontcolor="#0b1020", margin="0.18,0.10"];',
        '  edge  [color="#8da2c0", penwidth=1.3];',
        f'  topic [label="{wrap(topic, 18)}", fillcolor="#ff8a8a", fontsize=17, margin="0.3,0.2"];',
    ]
    ids = {}
    for i, c in enumerate(concepts):
        ids[str(c).strip().lower()] = f"c{i}"
        lines.append(f'  c{i} [label="{wrap(c)}", fillcolor="#7ee8dc"];')
        lines.append(f"  topic -- c{i};")
    for link in links:
        a = ids.get(str(link.get("from", "")).strip().lower())
        b = ids.get(str(link.get("to", "")).strip().lower())
        if a and b and a != b:
            lines.append(f'  {a} -- {b} [style=dashed, color="#b79cff"];')
    lines.append("}")
    return "\n".join(lines)


# ---------- PAGE ----------
st.title("📚 StudyStack")
st.caption("Turn screenshots into notes, flashcards, a concept map and a tutor.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📸 Capture", "🕸️ Knowledge Graph", "🧠 Smart Quiz", "💬 AI Tutor"])

with tab1:
    with card("home"):
        st.header("Welcome to StudyStack")
        st.write("Upload a screenshot of a lecture slide, syllabus or chat. StudyStack extracts the text, writes notes, "
                 "makes flashcards, draws a concept map, grades your explanations and lets you chat with the material.")

with tab2:
    with card("upload"):
        st.header("📸 Capture")
        uploaded = st.file_uploader("Upload a screenshot (PNG, JPG)", type=["png", "jpg", "jpeg"])
        if uploaded is not None:
            st.image(uploaded, caption="Uploaded screenshot", width=400)
            key = (uploaded.name, uploaded.size)
            if st.session_state.file_key != key:  # only call Gemini once per new file
                with st.spinner("Extracting knowledge and generating study materials..."):
                    result = analyze_image(uploaded)
                if "error" in result:
                    st.error(f"Analysis failed: {result['error']}")
                else:
                    st.session_state.analysis_result = result
                    st.session_state.file_key = key
            if st.session_state.file_key == key:
                st.success("Analysis complete. Open the other tabs.")

def need_upload():
    with card("empty"):
        st.info("Upload a screenshot in the Capture tab first.")

with tab3:
    res = st.session_state.analysis_result
    if res is None:
        need_upload()
    else:
        with card("notes"):
            st.header("Study notes")
            st.write(f"**Subject:** {res.get('subject')}  |  **Topic:** {res.get('topic')}")
            notes = res.get("detailed_notes", "No notes generated.")
            if isinstance(notes, dict):
                notes = "\n".join(f"- {v}" for v in notes.values())
            with st.expander("📖 Detailed notes", expanded=True):
                st.markdown(notes)

        with card("graph"):
            st.header("Concept map")
            concepts = [c for c in res.get("key_concepts", []) if str(c).strip()]
            if concepts:
                dot = build_dot(res.get("topic", "Topic"), concepts, res.get("relationships", []))
                try:
                    st.graphviz_chart(dot, engine="twopi", use_container_width=True)
                except TypeError:  # older Streamlit without the engine argument
                    st.graphviz_chart(dot, use_container_width=True)
                st.caption("Solid lines connect the topic to its concepts. Dashed lines show how concepts relate.")
            else:
                st.info("No key concepts were found in this screenshot.")

        with card("flash"):
            st.header("Flashcards")
            for c in res.get("flashcards", []):
                with st.expander(f"❓ {c.get('front')}"):
                    st.write(f"**Answer:** {c.get('back')}")

with tab4:
    res = st.session_state.analysis_result
    if res is None:
        need_upload()
    else:
        topic = res.get("topic", "the topic")
        with card("quiz"):
            st.header("Feynman quiz")
            st.write(f"Explain **{topic}** in your own words and get graded.")
            answer = st.text_area("Your explanation")
            if st.button("Grade my answer"):
                if answer.strip():
                    with st.spinner("Grading..."):
                        st.write(grade_answer(topic, answer))
                else:
                    st.warning("Type an explanation first.")

with tab5:
    res = st.session_state.analysis_result
    if res is None:
        need_upload()
    else:
        context = res.get("raw_text") or res.get("summary", "")
        with card("chat"):
            st.header("AI tutor")
            q = st.text_input("Ask about the material")
            if st.button("Ask"):
                if q.strip():
                    with st.spinner("Thinking..."):
                        st.write(chat_with_notes(q, context))
                else:
                    st.warning("Type a question first.")
