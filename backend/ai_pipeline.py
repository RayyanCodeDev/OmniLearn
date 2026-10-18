import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import PIL.Image

# Load the secret key from the .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def analyze_image(image_path):
    img = PIL.Image.open(image_path)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """
    Analyze this screenshot of a student's study material. 
    Extract the following information and return ONLY a valid JSON object:
    {
      "subject": "e.g., Physics, Math, History",
      "topic": "e.g., Newton's Laws, Calculus",
      "summary": "A 1-sentence summary of the content",
      "key_concepts": ["concept 1", "concept 2"]
    }
    """
    
    response = model.generate_content([prompt, img])
    text = response.text.strip().replace('```json', '').replace('```', '')
    try:
        return json.loads(text)
    except:
        return {"error": "Could not parse JSON"}
 
