import os
import json
from typing import List, Dict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()

# Centralized model choice
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_client = None

# --- Pydantic Schemas for Strict JSON Formatting ---
class Relationship(BaseModel):
    # Use Field alias to support the reserved Python word 'from'
    from_concept: str = Field(alias="from", description="Source concept name")
    to_concept: str = Field(alias="to", description="Target concept name")

    class Config:
        populate_by_name = True

class Flashcard(BaseModel):
    front: str
    back: str

class StudyMaterial(BaseModel):
    subject: str = Field(description="e.g., Physics, Biology, Chemistry, Mathematics")
    topic: str = Field(description="The specific topic name")
    detailed_notes: str = Field(description="Comprehensive markdown notes covering the core concepts")
    key_concepts: List[str] = Field(description="Important keywords or concepts")
    relationships: List[Relationship]
    flashcards: List[Flashcard]
    summary: str = Field(description="A short summary of the text")

# --- Client Setup & Configuration ---
def _find_key():
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        if os.getenv(name):
            return os.getenv(name)
    try:
        import streamlit as st
        for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            if name in st.secrets:
                return st.secrets[name]
    except Exception:
        pass
    return None

def get_client() -> genai.Client:
    """Lazily initializes and updates the new SDK client."""
    global _client
    if _client is None:
        key = _find_key()
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set. Please add it to your environment variables or Streamlit secrets.")
        _client = genai.Client(api_key=key)
    return _client

# --- Core AI Operations ---
def analyze_image(uploaded_file):
    try:
        client = get_client()
        img = Image.open(uploaded_file)
        
        prompt = "Analyze this study material image and organize its information into the requested schema structure."
        
        # Using native schemas forces Gemini to output valid JSON matching our model
        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StudyMaterial,
            ),
        )
        # Simply parse the guaranteed clean JSON string directly
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

def grade_answer(topic, answer):
    try:
        client = get_client()
        prompt = f"Evaluate this student's explanation of the topic '{topic}':\n\n{answer}\n\nProvide constructive feedback, grade them gently, and point out any missing conceptual details."
        
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        return f"Error grading answer: {e}"

def chat_with_notes(query, context, history=None):
    """
    history can be a list of dicts: [{'role': 'user', 'content': '...'}, {'role': 'model', 'content': '...'}]
    It formats past messages into the prompt context seamlessly.
    """
    try:
        client = get_client()
        
        # Build conversational string context from the history list
        convo_history = ""
        if history:
            for message in history[-6:]: # Keep the last 3 exchanges for speed/token economy
                role = "Student" if message['role'] == 'user' else "AI Tutor"
                convo_history += f"{role}: {message['content']}\n"
                
        prompt = (
            f"Context notes:\n{context}\n\n"
            f"Conversation History:\n{convo_history or '(No history yet)'}\n"
            f"Student Question: {query}\n\n"
            f"Provide a helpful answer tying directly back to the context notes if relevant."
        )
        
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error in AI tutor: {e}"
        
