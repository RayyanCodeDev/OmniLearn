import io
import re
import textwrap
import streamlit as st
from pypdf import PdfReader, PdfWriter
from backend.ai_pipeline import analyze_image, analyze_pdf, grade_answer, chat_with_notes

st.set_page_config(page_title="StudyStack", page_icon="📚", layout="wide")

MAX_PDF_MB = 20
MAX_PDF_PAGES = 30  # pages analyzed at once (keeps results good and free-tier usage low)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "file_key" not in st.session_state:
    st.session_state.file_key = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "name_asked" not in st.session_state:
    st.session_state.name_asked = False

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
.stTextArea textarea,.stTextInput input,.stNumberInput input{background:var(--glass2)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:14px!important;}
[data-testid="stFileUploaderDropzone"]{background:var(--glass2);border:1.5px dashed var(--border);border-radius:18px;}
[data-testid="stFileUploaderDropzone"] *{color:var(--text)!important;}
[data-testid="stAlert"]{background:var(--glass2);border:1px solid var(--border);border-radius:16px;backdrop-filter:blur(14px);}
.stButton>button,[data-testid="stFormSubmitButton"]>button{background:linear-gradient(135deg,#7c5cff,#00c8ff);color:#fff;border:0;border-radius:999px;padding:.55rem 1.6rem;font-weight:700;box-shadow:0 0 22px var(--glow);}
.stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover{filter:brightness(1.12);color:#fff;}

/* Chat form and message bubbles */
[data-testid="stForm"]{border:none!important;padding:0!important;background:transparent!important;}
[data-testid="stChatMessage"]{background:var(--glass);border:1px solid var(--border);border-radius:18px;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);}

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


def need_upload(tab_name):
    with card(f"empty_{tab_name}"):
        st.info("Upload a screenshot or PDF in the Capture tab first.")


def clean_name(raw):
    """Keep letters (any language), digits, spaces and a few name symbols; max 30 chars."""
    return re.sub(r"[^\w\s'’.-]", "", raw or "", flags=re.UNICODE).strip()[:30]


def get_context(res):
    """Everything the tutor can use: summary, notes and extracted text (capped for safety)."""
    notes = res.get("detailed_notes", "")
    if isinstance(notes, dict):
        notes = "\n".join(str(v) for v in notes.values())
    parts = [str(res.get("summary", "")), str(notes), str(res.get("raw_text", ""))]
    return "\n\n".join(p for p in parts if p.strip())[:20000]


# ---------- PDF HELPERS ----------
def pdf_page_count(data):
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            return None
        return len(reader.pages)
    except Exception:
        return None


def pdf_slice(data, start, end):
    """Return a new PDF containing pages start..end (1-based, inclusive)."""
    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted:
        reader.decrypt("")
    writer = PdfWriter()
    for i in range(start - 1, end):
        writer.add_page(reader.pages[i])
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def save_result(result, key):
    if "error" in result:
        st.error(f"Analysis failed: {result['error']}")
    else:
        st.session_state.analysis_result = result
        st.session_state.file_key = key
        st.session_state.chat_history = []  # new material = fresh chat (name is kept)


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
st.caption("Turn screenshots and PDFs into notes, flashcards, a concept map and a tutor.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📸 Capture", "🕸️ Knowledge Graph", "🧠 Smart Quiz", "💬 AI Tutor"])

with tab1:
    with card("home"):
        st.header("Welcome to StudyStack")
        st.write("Upload a screenshot or a PDF of a lecture, syllabus or chat. StudyStack extracts the text, writes notes, "
                 "makes flashcards, draws a concept map, grades your explanations and lets you chat with the material.")

with tab2:
    with card("upload"):
        st.header("📸 Capture")
        uploaded = st.file_uploader("Upload a screenshot (PNG, JPG) or a PDF", type=["png", "jpg", "jpeg", "pdf"])

        if uploaded is not None:
            is_pdf = uploaded.name.lower().endswith(".pdf")

            if not is_pdf:
                # Screenshots are analyzed automatically, once per new file
                st.image(uploaded, caption="Uploaded screenshot", width=400)
                key = ("img", uploaded.name, uploaded.size)
                if st.session_state.file_key != key:
                    with st.spinner("Extracting knowledge and generating study materials..."):
                        result = analyze_image(uploaded)
                    save_result(result, key)
                if st.session_state.file_key == key:
                    st.success("Analysis complete. Open the other tabs.")

            else:
                data = uploaded.getvalue()
                if uploaded.size > MAX_PDF_MB * 1024 * 1024:
                    st.error(f"This PDF is larger than {MAX_PDF_MB} MB. Try a smaller file or split it first.")
                else:
                    total = pdf_page_count(data)
                    if not total:
                        st.error("Couldn't read this PDF. It may be password-protected or damaged.")
                    else:
                        st.write(f"📄 **{uploaded.name}** · {total} page{'s' if total != 1 else ''}")
                        fid = f"{uploaded.name}_{uploaded.size}"
                        c1, c2, _ = st.columns([1, 1, 3])
                        start = int(c1.number_input("From page", min_value=1, max_value=total, value=1, step=1, key=f"from_{fid}"))
                        end = int(c2.number_input("To page", min_value=1, max_value=total,
                                                  value=min(total, MAX_PDF_PAGES), step=1, key=f"to_{fid}"))
                        count = end - start + 1
                        key = ("pdf", uploaded.name, uploaded.size, start, end)

                        if end < start:
                            st.error("'To page' must be the same as or after 'From page'.")
                        elif count > MAX_PDF_PAGES:
                            st.warning(f"Please pick at most {MAX_PDF_PAGES} pages at a time (you picked {count}). "
                                       "You can analyze the next chapter afterwards.")
                        else:
                            st.caption(f"{count} page{'s' if count != 1 else ''} selected.")
                            if st.button("Analyze pages"):
                                with st.spinner("Reading your PDF and generating study materials..."):
                                    result = analyze_pdf(pdf_slice(data, start, end))
                                save_result(result, key)
                            if st.session_state.file_key == key:
                                st.success("Analysis complete. Open the other tabs.")

with tab3:
    res = st.session_state.analysis_result
    if res is None:
        need_upload("graph")
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
                st.info("No key concepts were found in this material.")

        with card("flash"):
            st.header("Flashcards")
            for c in res.get("flashcards", []):
                with st.expander(f"❓ {c.get('front')}"):
                    st.write(f"**Answer:** {c.get('back')}")

with tab4:
    res = st.session_state.analysis_result
    if res is None:
        need_upload("quiz")
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
        need_upload("chat")
    else:
        context = get_context(res)
        name = st.session_state.user_name
        topic = res.get("topic", "your notes")

        with card("chat"):
            st.header("AI tutor")

            # Step 1: ask the student's name (once per visit)
            if not st.session_state.name_asked:
                with st.chat_message("assistant"):
                    st.markdown("Hi! I'm your StudyStack tutor 👋 What should I call you?")
                with st.form("name_form", clear_on_submit=True):
                    n = st.text_input("Your name", max_chars=30, placeholder="e.g. Ayesha")
                    c1, c2, _ = st.columns([1, 1, 4])
                    go = c1.form_submit_button("Continue")
                    skip = c2.form_submit_button("Skip")
                if go:
                    cleaned = clean_name(n)
                    if cleaned:
                        st.session_state.user_name = cleaned
                        st.session_state.name_asked = True
                        st.rerun()
                    else:
                        st.warning("Type a name, or press Skip.")
                if skip:
                    st.session_state.user_name = ""
                    st.session_state.name_asked = True
                    st.rerun()

            # Step 2: normal chat
            else:
                if not st.session_state.chat_history:
                    hello = f"Nice to meet you, {name}! " if name else "Hi there! "
                    with st.chat_message("assistant"):
                        st.markdown(f"{hello}Ask me anything about **{topic}**, or try: \"Explain this like I'm 5\".")
                for m in st.session_state.chat_history:
                    with st.chat_message(m["role"]):
                        st.markdown(m["content"])

                with st.form("chat_form", clear_on_submit=True):
                    q = st.text_input("Ask about the material", placeholder="Type your question and press Enter")
                    sent = st.form_submit_button("Ask")

                if sent:
                    if q.strip():
                        with st.spinner("Thinking..."):
                            reply = chat_with_notes(q, context, st.session_state.chat_history, name)
                        if reply.startswith("⚠️"):
                            st.warning(reply)  # errors are shown but not saved in the chat
                        else:
                            st.session_state.chat_history.append({"role": "user", "content": q})
                            st.session_state.chat_history.append({"role": "assistant", "content": reply})
                            st.rerun()
                    else:
                        st.warning("Type a question first.")

                b1, b2, _ = st.columns([1, 1, 4])
                if st.session_state.chat_history and b1.button("Clear chat"):
                    st.session_state.chat_history = []
                    st.rerun()
                if b2.button("Change name"):
                    st.session_state.name_asked = False
                    st.rerun()
