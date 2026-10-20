import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# Load the secret key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"

PROMPT = """You are an OCR + classification engine for a student's study app.
Read the screenshot and return ONLY valid JSON (no markdown fences, no prose)
with exactly these keys:

{
  "subject":      "e.g. Physics, Chemistry, History",
  "topic":        "short specific topic, e.g. Newton's Second Law",
  "summary":      "2-3 sentence plain-English summary of what this image teaches",
  "key_concepts": ["concept 1", "concept 2", "concept 3"]
}

If the image has no academic content, still return JSON but set
subject and topic to "Unknown" and explain in summary why.
"""

def _strip_fences(text: str) -> str:
    """Strip markdown fences if Gemini adds them."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text

# THIS IS THE FUNCTION YOUR APP.PY IS LOOKING FOR
def analyze_image(image_path):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        img = Image.open(image_path)
        response = model.generate_content([PROMPT, img])
        cleaned = _strip_fences(response.text)
        
        data = json.loads(cleaned)
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
