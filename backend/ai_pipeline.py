import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = """You are an OCR + classification engine for a student's study app.
Read the screenshot and return ONLY valid JSON (no markdown fences, no prose)
with exactly these keys:
{
  "subject": "e.g. Physics, Chemistry, History",
  "topic": "short specific topic",
  "summary": "2-3 sentence plain-English summary",
  "detailed_notes": "Detailed, bulleted study notes explaining the concepts in the image.",
  "key_concepts": ["concept 1", "concept 2", "concept 3"],
  "raw_text": "The exact text extracted from the image",
  "flashcards": [{"front": "Question", "back": "Answer"}]
}
"""

def analyze_image(image_path):
    try:
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

# --- NEW FEATURE: Smart Quiz Grader ---
def grade_answer(topic, user_answer):
    prompt = f"""
    You are a helpful tutor. The student is studying {topic}.
    The student wrote this explanation: "{user_answer}"
    
    Evaluate their answer using the Feynman Technique. If it is correct, praise them. 
    If it is wrong or incomplete, gently correct them and explain the right answer in 2 sentences.
    Return ONLY plain text.
    """
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return response.text

# --- NEW FEATURE: Chat with Notes ---
def chat_with_notes(question, context_text):
    prompt = f"""
    You are an AI Tutor. Answer the student's question using ONLY the context below.
    If the answer is not in the context, say "I couldn't find that in your notes."
    
    Context: {context_text}
    Question: {question}
    """
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return response.text

if __name__ == "__main__":
    # (Keep your testing code here for the terminal)
    pass
