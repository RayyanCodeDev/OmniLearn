import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

SCREENSHOT_DIR = Path(__file__).parent.parent / "data" / "test_screenshots"

PROMPT = """You are an OCR + classification engine for a student's study app.
Read the screenshot and return ONLY valid JSON (no markdown fences, no prose)
with exactly these keys:
{
  "subject": "e.g. Physics, Chemistry, History",
  "topic": "short specific topic, e.g. Newton's Second Law",
  "summary": "2-3 sentence plain-English summary of what this image teaches",
  "key_concepts": ["concept 1", "concept 2", "concept 3"]
}
"""

def analyze_image(image_path):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not set in .env"}

    try:
        client = genai.Client(api_key=api_key)
        img = Image.open(image_path)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[PROMPT, img]
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            lines = text.splitlines()[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    files = sorted(SCREENSHOT_DIR.glob("shot_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not files:
        print("No screenshots found in data/test_screenshots. Run capture.py first.")
        sys.exit(1)
        
    latest_shot = files[0]
    print(f"📸 Processing latest screenshot: {latest_shot.name}")
    print("🧠 Analyzing with Gemini...")
    
    result = analyze_image(latest_shot)
    print(json.dumps(result, indent=2))
