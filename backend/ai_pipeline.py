import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from PIL import Image

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
KEY_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY")
_client = None


def _find_key():
    """Look for the API key in environment variables first, then in Streamlit Secrets."""
    for name in KEY_NAMES:
        if os.getenv(name):
            return os.getenv(name)
    try:
        import streamlit as st
        for name in KEY_NAMES:
            if name in st.secrets:
                return st.secrets[name]
    except Exception:
        pass
    return None


def get_client():
    """Create the client lazily so a missing key shows a normal error instead of crashing on import."""
    global _client
    if _client is None:
        key = _find_key()
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it in Streamlit Cloud > Manage app > Settings > Secrets.")
        _client = genai.Client(api_key=key)
    return _client


def friendly_error(e):
    """Turn an API exception into a short message a student can read."""
    if isinstance(e, errors.ClientError):
        code = getattr(e, "code", None)
        if code == 429:
            return ("⚠️ Gemini's free-tier limit was reached. Wait about a minute and try again. "
                    "If it keeps happening, you've probably used today's free quota.")
        if code == 404:
            return f"⚠️ The model '{MODEL}' was not found. Set GEMINI_MODEL in Secrets to a model your key can use."
        if code in (401, 403):
            return "⚠️ Gemini rejected the API key. Check GEMINI_API_KEY in Secrets."
        return f"⚠️ Gemini returned an error ({code}): {getattr(e, 'message', e)}"
    return f"⚠️ Something went wrong: {e}"


PROMPT = """You are an OCR + classification engine for a student's study app.
Read the screenshot and return ONLY valid JSON with exactly these keys:
{
  "subject": "e.g. Physics, Chemistry, History",
  "topic": "short specific topic",
  "summary": "2-3 sentence plain-English summary",
  "detailed_notes": "A single markdown string of detailed, bulleted study notes.",
  "key_concepts": ["5 to 8 short concept names, max 4 words each"],
  "relationships": [{"from": "concept A", "to": "concept B"}],
  "raw_text": "The exact text extracted from the image",
  "flashcards": [{"front": "Question", "back": "Answer"}]
}
Rules for "relationships": use ONLY names copied exactly from key_concepts, and give 3 to 8 links
showing how the concepts relate to each other (not to the topic).
"""


def analyze_image(image_file):
    try:
        img = Image.open(image_file)
        response = get_client().models.generate_content(
            model=MODEL,
            contents=[PROMPT, img],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        text = response.text.strip()
        if text.startswith("```"):
            lines = text.splitlines()[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)
    except Exception as e:
        return {"error": friendly_error(e)}


def _ask(prompt):
    try:
        return get_client().models.generate_content(model=MODEL, contents=prompt).text
    except Exception as e:
        return friendly_error(e)


def grade_answer(topic, user_answer):
    return _ask(f"""You are a helpful tutor. The student is studying {topic}.
The student wrote this explanation: "{user_answer}"

Evaluate it using the Feynman Technique. If it is correct, praise them.
If it is wrong or incomplete, gently correct them and explain the right answer in 2 sentences.
Return ONLY plain text.""")


def chat_with_notes(question, context_text):
    return _ask(f"""You are StudyStack, an expert AI tutor.
The student's extracted study material is below as "Context".

Context:
{context_text}

Question: {question}

1. If the question relates to the Context, answer specifically from it.
2. If it is a general request ("explain like I'm 5", "give an example"), use your own knowledge but tie it back to the Context when you can.
3. Be helpful, conversational and encouraging.""")
