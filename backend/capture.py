import pyautogui
import keyboard
import time
import os
from backend.ai_pipeline import analyze_image

SAVE_DIR = "data/test_screenshots"
os.makedirs(SAVE_DIR, exist_ok=True)

def capture_and_analyze():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filepath = f"{SAVE_DIR}/screenshot_{timestamp}.png"
    
    print("\n📸 Taking screenshot...")
    pyautogui.screenshot(filepath)
    
    print("🧠 Analyzing with AI...")
    result = analyze_image(filepath)
    
    print("✅ AI Result:", result)
    print("\nPress Ctrl+Shift+O to take another screenshot.")

keyboard.add_hotkey('ctrl+shift+o', capture_and_analyze)

print("OmniLearn Capture Running. Press Ctrl+Shift+O to capture. Press ESC in this terminal to quit.")
keyboard.wait('esc')

  