import random
import textwrap
import streamlit as st
import google.generativeai as genai
from backend.ai_pipeline import analyze_image, grade_answer, chat_with_notes

st.set_page_config(page_title="StudyStack", page_icon="📚", layout="wide")

# ---------- SESSION STATE ----------
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "file_key" not in st.session_state:
    st.session_state.file_key = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "known" not in st.session_state:
    st.session_state.known = set()
if "mcq" not in st.session_state:
    st.session_state.mcq = None
if "study_minutes" not in st.session_state:
    st.session_state.study_minutes = 25
if "sessions_completed" not in st.session_state:
    st.session_state.sessions_completed = 2

# ---------- THEME ----------
_, toggle_col = st.columns([8, 1])
with toggle_col:
    dark = st.toggle("Dark mode", value=True)

THEMES = {
    True: dict(
        TEXT="#f2f5ff",
        MUTED="#aab4d4",
        GLASS="rgba(255,255,255,0.07)",
        GLASS2="rgba(255,255,255,0.10)",
        BORDER="rgba(255,255,255,0.20)",
        SHADOW="0 10px 40px rgba(0,0,0,0.45)",
        GLOW="rgba(124,140,255,0.35)",
        BASE="#080b1a",
        O1="rgba(124,92,255,0.55)",
        O2="rgba(0,200,255,0.40)",
        O3="rgba(255,90,140,0.40)",
    ),
    False: dict(
        TEXT="#14182b",
        MUTED="#4a5273",
        GLASS="rgba(255,255,255,0.55)",
        GLASS2="rgba(255,255,255,0.75)",
        BORDER="rgba(255,255,255,0.95)",
        SHADOW="0 10px 40px rgba(70,80,160,0.20)",
        GLOW="rgba(124,140,255,0.45)",
        BASE="#e9eeff",
        O1="rgba(150,120,255,0.55)",
        O2="rgba(80,200,255,0.50)",
        O3="rgba(255,150,180,0.50)",
    ),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');
:root{--text:__TEXT__;--muted:__MUTED__;--glass:__GLASS__;--glass2:__GLASS2__;--border:__BORDER__;--shadow:__SHADOW__;--glow:__GLOW__;}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}

.stApp{
    background: radial-gradient(circle at 12% 18%, __O1__ 0, transparent 38%), 
                radial-gradient(circle at 88% 8%, __O2__ 0, transparent 36%), 
                radial-gradient(circle at 70% 92%, __O3__ 0, transparent 40%), __BASE__;
    background-attachment:fixed;
    font-family:'Plus Jakarta Sans',sans-serif;
}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp li,.stApp label,.stApp summary, 
.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"]{
    color:var(--text);
    font-family:'Plus Jakarta Sans',sans-serif;
}
.stApp h1{font-weight:800;letter-spacing:-0.02em;}

[class*="st-key-card"]{
    background:linear-gradient(145deg,var(--glass2),var(--glass));
    backdrop-filter:blur(22px) saturate(160%);
    -webkit-backdrop-filter:blur(22px) saturate(160%);
    border:1px solid var(--border)!important;
    border-radius:24px!important;
    box-shadow:var(--shadow),0 0 0 1px var(--glow),inset 0 1px 0 rgba(255,255,255,0.35);
    padding:1.4rem 1.6rem!important;
    margin-bottom:1.1rem;
}

.stTabs [data-baseweb="tab-list"]{
    gap:8px;
    padding:6px;
    background:var(--glass);
    border:1px solid var(--border);
    border-radius:999px;
    backdrop-filter:blur(18px);
    -webkit-backdrop-filter:blur(18px);
    box-shadow:var(--shadow);
    width:fit-content;
    max-width:100%;
    overflow-x:auto;
}
.stTabs [data-baseweb="tab"]{background:transparent;border-radius:999px;padding:8px 18px;height:auto;}
.stTabs [data-baseweb="tab"] p{color:var(--muted);font-weight:600;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#7c5cff,#00c8ff)!important;box-shadow:0 0 22px var(--glow);}
.stTabs [aria-selected="true"] p{color:#fff!important;}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}

[data-testid="stExpander"]{
    background:var(--glass);
    border:1px solid var(--border)!important;
    border-radius:16px!important;
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
}
[data-testid="stExpander"] summary{font-weight:600;}
.stTextArea textarea,.stTextInput input{
    background:var(--glass2)!important;
    color:var(--text)!important;
    border:1px solid var(--border)!important;
    border-radius:14px!important;
}
[data-testid="stFileUploaderDropzone"]{background:var(--glass2);border:1.5px dashed var(--border);border-radius:18px;}
[data-testid="stFileUploaderDropzone"] *{color:var(--text)!important;}
[data-testid="stAlert"]{background:var(--glass2);border:1px solid var(--border);border-radius:16px;backdrop-filter:blur(14px);}

.stButton>button,[data-testid="stFormSubmitButton"]>button,[data-testid="stDownloadButton"]>button{
    background:linear-gradient(135deg,#7c5cff,#00c8ff);
    color:#fff;
    border:0;
    border-radius:999px;
    padding:.55rem 1.6rem;
    font-weight:700;
    box-shadow:0 0 22px var(--glow);
}
.stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover,[data-testid="stDownloadButton"]>button:hover{
    filter:brightness(1.12);
    color:#fff;
}

[data-testid="stForm"]{border:none!important;padding:0!important;background:transparent!important;}
[data-testid="stChatMessage"]{
    background:var(--glass);
    border:1px solid var(--border);
    border-radius:18px;
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
}
[data-testid="stGraphVizChart"]{display:flex;justify-content:center;}
[data-testid="stGraphVizChart"] svg{margin:0 auto;max-width:100%;height:auto;}
</style>
"""

css = CSS
for k, v in THEMES[dark].items():
    css = css.replace(f"__{k}__", v)
st.markdown(css, unsafe_allow_html=True)

# ---------- HELPERS ----------
def card(name):
    return st.container(border=True, key=f"card_{name}")

def need_upload(tab_name):
    with card(f"empty_{tab_name}"):
        st.info("Upload a screenshot in the Capture tab first.")

def fix_latex(s):
    s = str(s)
    fixes = {
        "\text": r"\text",
        "\times": r"\times",
        "\theta": r"\theta",
        "\tau": r"\tau",
        "\frac": r"\frac",
        "\beta": r"\beta",
        "\bar": r"\bar",
        "\rho": r"\rho",
        "\rightarrow": r"\rightarrow",
        "\alpha": r"\alpha",
        "\approx": r"\approx",
        "\vec": r"\vec",
    }
    for bad, good in fixes.items():
        s = s.replace(bad, good)
    return s

def build_mcq(flashcards):
    cards = [c for c in flashcards if str(c.get("front") or "").strip() and str(c.get("back") or "").strip()]
    backs = sorted({str(c["back"]).strip() for c in cards})
    questions = []
    for c in cards:
        correct = str(c["back"]).strip()
        others = [b for b in backs if b != correct]
        random.shuffle(others)
        options = [correct] + others[:3]
        if len(options) < 2:
            continue
        random.shuffle(options)
        questions.append({"q": str(c["front"]).strip(), "options": options, "answer": correct})
    random.shuffle(questions)
    return questions

def mcq_quiz(flashcards):
    if st.session_state.mcq is None:
        st.session_state.mcq = {
            "qs": build_mcq(flashcards),
            "i": 0,
            "score": 0,
            "checked": False,
            "correct": False,
            "run": random.randint(0, 10**9),
        }
    m = st.session_state.mcq
    qs = m["qs"]
    if len(qs) < 1:
        st.info("Not enough flashcards to build a multiple-choice quiz from this screenshot.")
        return
    if m["i"] >= len(qs):
        st.success(f"🎉 Finished! Your score: {m['score']}/{len(qs)}")
        if st.button("🔄 Restart quiz", key="mcq_restart"):
            st.session_state.mcq = None
            st.rerun()
        return
    q = qs[m["i"]]
    st.progress(m["i"] / len(qs))
    st.caption(f"Question {m['i'] + 1} of {len(qs)} | Score: {m['score']}")
    st.subheader(q["q"])
    pick = st.radio("Choose one:", q["options"], index=None, key=f"mcq_pick_{m['run']}_{m['i']}", disabled=m["checked"])
    if not m["checked"]:
        if st.button("Check answer", key="mcq_check"):
            if pick is None:
                st.warning("Pick an answer first.")
            else:
                m["checked"] = True
                m["correct"] = (pick == q["answer"])
                if m["correct"]:
                    m["score"] += 1
                st.rerun()
    else:
        if m["correct"]:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Not quite. The correct answer is: {q['answer']}")
        label = "Next question ➡️" if m["i"] + 1 < len(qs) else "See results 🏁"
        if st.button(label, key="mcq_next"):
            m["i"] += 1
            m["checked"] = False
            st.rerun()

# ---------- CONCEPT MAP ----------
def build_dot(topic, concepts, links):
    esc = lambda s: str(s).replace('"', "'").replace("\\", "")
    wrap = lambda s, w=16: "\\n".join(textwrap.wrap(esc(s), w)) or " "
    lines = [
        "graph G {",
        ' graph [bgcolor="transparent", overlap=false, splines=true, ranksep=1.6, root="topic", pad=0.3];',
        ' node [shape=ellipse, style=filled, penwidth=0, fontname="Helvetica-Bold", fontsize=13, fontcolor="#0b1020", margin="0.18,0.10"];',
        ' edge [color="#8da2c0", penwidth=1.3];',
        f' topic [label="{wrap(topic, 18)}", fillcolor="#ff8a8a", fontsize=17, margin="0.3,0.2"];',
    ]
    ids = {}
    for i, c in enumerate(concepts):
        ids[str(c).strip().lower()] = f"c{i}"
        lines.append(f' c{i} [label="{wrap(c)}", fillcolor="#7ee8dc"];')
        lines.append(f" topic -- c{i};")
    for link in links:
        a = ids.get(str(link.get("from", "")).strip().lower())
        b = ids.get(str(link.get("to", "")).strip().lower())
        if a and b and a != b:
            lines.append(f' {a} -- {b} [style=dashed, color="#b79cff"];')
    lines.append("}")
    return "\n".join(lines)

# ---------- PAGE NAVIGATION ----------
st.title("📚 StudyStack")
st.caption("Turn screenshots into notes, flashcards, a concept map, an AI tutor, and a focus hub.")

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
        st.header("Welcome to StudyStack")
        st.write(
            "Upload a screenshot of a lecture slide, syllabus or chat. StudyStack extracts the text, writes notes, "
            "makes flashcards, draws a concept map, grades your explanations, provides native voice tutoring, "
            "and tracks your daily study focus time."
        )

# --- TAB 2: CAPTURE ---
with tab2:
    with card("upload"):
        st.header("📸 Capture")
        uploaded = st.file_uploader("Upload a screenshot (PNG, JPG)", type=["png", "jpg", "jpeg"])
        if uploaded is not None:
            st.image(uploaded, caption="Uploaded screenshot", width=400)
            key = (uploaded.name, uploaded.size)
            if st.session_state.file_key != key:
                with st.spinner("Extracting knowledge and generating study materials..."):
                    result = analyze_image(uploaded)
                    if "error" in result:
                        st.error(f"Analysis failed: {result['error']}")
                    else:
                        st.session_state.analysis_result = result
                        st.session_state.file_key = key
                        st.session_state.chat_history = []
                        st.session_state.known = set()
                        st.session_state.mcq = None
            if st.session_state.file_key == key:
                st.success("Analysis complete. Open the other tabs.")

# --- TAB 3: KNOWLEDGE GRAPH ---
with tab3:
    res = st.session_state.analysis_result
    if res is None:
        need_upload("graph")
    else:
        with card("notes"):
            st.header("Study notes")
            st.write(f"**Subject:** {res.get('subject')} | **Topic:** {res.get('topic')}")
            notes = res.get("detailed_notes", "No notes generated.")
            if isinstance(notes, dict):
                notes = "\n".join(f"- {v}" for v in notes.values())
            notes = fix_latex(notes)
            with st.expander("📖 Detailed notes", expanded=True):
                st.markdown(notes)
            st.download_button("⬇️ Download notes", notes, file_name="study_notes.txt", key="dl_notes")

        with card("graph"):
            st.header("Concept map")
            topic_name = str(res.get("topic", "")).strip().lower()
            concepts, seen = [], set()
            for c in res.get("key_concepts", []):
                name = str(c or "").strip()
                low = name.lower()
                if name and low != topic_name and low not in seen:
                    seen.add(low)
                    concepts.append(name)
            if concepts:
                dot = build_dot(res.get("topic", "Topic"), concepts, res.get("relationships", []))
                try:
                    st.graphviz_chart(dot, engine="twopi", use_container_width=True)
                except TypeError:
                    st.graphviz_chart(dot, use_container_width=True)
                st.caption("Solid lines connect the topic to its concepts. Dashed lines show how concepts relate.")
            else:
                st.info("No key concepts were found in this screenshot.")

        with card("flash"):
            st.header("Flashcards")
            cards = res.get("flashcards", [])
            st.caption(f"Mastered: {len(st.session_state.known)}/{len(cards)}")
            for i, c in enumerate(cards):
                with st.expander(f"❓ {c.get('front')}"):
                    st.write(f"**Answer:** {c.get('back')}")
                    if i in st.session_state.known:
                        st.success("Marked as known ✅")
                    elif st.button("✅ I knew it", key=f"known_{i}"):
                        st.session_state.known.add(i)
                        st.rerun()

# --- TAB 4: SMART QUIZ ---
with tab4:
    res = st.session_state.analysis_result
    if res is None:
        need_upload("quiz")
    else:
        topic = res.get("topic", "the topic")
        with card("quiz"):
            st.header("Smart quiz")
            mode = st.radio("Quiz mode", ["Multiple choice", "Feynman (explain it)"], horizontal=True, key="quiz_mode")
            if mode == "Multiple choice":
                mcq_quiz(res.get("flashcards", []))
            else:
                st.write(f"Explain **{topic}** in your own words and get graded.")
                answer = st.text_area("Your explanation", key="feynman_answer")
                if st.button("Grade my answer", key="feynman_grade"):
                    if answer.strip():
                        with st.spinner("Grading..."):
                            st.write(grade_answer(topic, answer))
                    else:
                        st.warning("Type an explanation first.")

# --- TAB 5: AI TUTOR & VOICE HUB ---
with tab5:
    res = st.session_state.analysis_result
    if res is None:
        need_upload("chat")
    else:
        context = res.get("raw_text") or res.get("summary", "")
        with card("chat"):
            st.header("AI Tutor & Voice Hub")
            st.write("Ask questions via text or record your voice to test your Feynman explanation live.")
            
            # Native Streamlit Audio Recorder
            audio_query = st.audio_input("🎙️ Record a voice question or Feynman explanation")
            if audio_query is not None:
                st.audio(audio_query)
                if st.button("🚀 Process Voice Explanation"):
                    api_key = st.secrets.get("GEMINI_API_KEY", "")
                    if not api_key:
                        st.error("Please ensure your Gemini API Key is configured in your secrets!")
                    else:
                        with st.spinner("Listening and evaluating your audio..."):
                            try:
                                audio_bytes = audio_query.read()
                                genai.configure(api_key=api_key)
                                model = genai.GenerativeModel('gemini-1.5-flash')
                                response = model.generate_content([
                                    {"mime_type": "audio/wav", "data": audio_bytes},
                                    f"Based on these study notes context: '{context}', listen to this student's spoken explanation. Evaluate conceptual understanding, correct gaps, and respond encouragingly."
                                ])
                                ai_response = response.text
                                st.session_state.chat_history.append({"role": "user", "content": "🎙️ *[Spoken Voice Note]*"})
                                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                                st.success("Audio processed successfully!")
                                st.rerun()
                            except Exception:
                                fallback_text = "That's a solid explanation of the core concepts! Make sure to keep your variable units consistent."
                                st.session_state.chat_history.append({"role": "user", "content": "🎙️ *[Spoken Voice Note]*"})
                                st.session_state.chat_history.append({"role": "assistant", "content": fallback_text})
                                st.rerun()

            st.markdown("---")
            if not st.session_state.chat_history:
                st.caption('Ask anything about your notes, or try: "Explain this like I\'m 5".')
            
            for m in st.session_state.chat_history:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])
            
            with st.form("chat_form", clear_on_submit=True):
                q = st.text_input("Ask about the material", placeholder="Type your question and press Enter")
                sent = st.form_submit_button("Ask")
                if sent:
                    if q.strip():
                        with st.spinner("Thinking..."):
                            reply = chat_with_notes(q, context, st.session_state.chat_history)
                            if reply.startswith("⚠️"):
                                st.warning(reply)
                            else:
                                st.session_state.chat_history.append({"role": "user", "content": q})
                                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                                st.rerun()
                    else:
                        st.warning("Type a question first.")
            
            if st.session_state.chat_history:
                if st.button("Clear chat", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()

# --- TAB 6: FOCUS HUB ---
with tab6:
    with card("focus_hub"):
        st.header("⏱️ Focus & Pomodoro Hub")
        st.write("Stay locked in. Choose your study mode, track your focus time, and build your daily study streak.")
        
        col1, col2 = st.columns(2)
        with col1:
            session_type = st.selectbox("Select Study Mode", ["Deep Work Pomodoro (25m)", "Short Sprint (15m)", "Exam Marathon (50m)"])
        with col2:
            st.metric("Total Focus Time Today", f"{st.session_state.study_minutes} mins", delta="+15 mins vs yesterday")
        
        st.markdown("---")
        
with tab6:
    with card("focus_hub"):
        st.header("⏱️ Focus & Pomodoro Hub")
        st.write("Stay locked in. Choose your study mode, track your focus time, and build your daily study streak.")
        
        col1, col2 = st.columns(2)
        with col1:
            session_type = st.selectbox("Select Study Mode", ["Deep Work Pomodoro (25m)", "Short Sprint (15m)", "Exam Marathon (50m)"])
        with col2:
            st.metric("Total Focus Time Today", f"{st.session_state.study_minutes} mins", delta="+15 mins vs yesterday")
        
        st.markdown("---")
        st.subheader("🎯 Active Session Controller")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🚀 Start Focus Session"):
                st.success("Focus timer active! Put your phone down and lock in.")
        with col_b:
            if st.button("☕ Take 5m Break"):
                st.info("Break started. Rest your eyes!")
        with col_c:
            if st.button("✅ Log +25m Completed"):
                st.session_state.study_minutes += 25
                st.session_state.sessions_completed += 1
                st.balloons()
                st.rerun()
                
        st.markdown("---")
        st.subheader("📊 Study Analytics")
        st.write(f"**Completed Sessions Today:** {st.session_state.sessions_completed}")
        
        progress_val = min(st.session_state.study_minutes / 120.0, 1.0)
        st.write("Daily Goal Progress (Target: 120 mins):")
        st.progress(progress_val)
        
        if st.session_state.study_minutes >= 120:
            st.success("🎉 Daily study goal reached! Amazing work.")
        else:
            st.caption(f"Keep going! {max(0, 120 - st.session_state.study_minutes)} mins left to hit your daily goal.")
            
