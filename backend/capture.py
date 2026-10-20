"""
capture.py — OmniLearn global hotkey screenshot capture.
Press Ctrl+Shift+O anywhere to grab a screenshot and save it.
"""
import os
import sys
import time
import datetime
from pathlib import Path

import keyboard
import pyautogui
from PIL import Image

# --- Config -----------------------------------------------------------------
# Changed this line so it saves to the folder our website reads from!
SCREENSHOT_DIR = Path(__file__).parent.parent / "data" / "test_screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_HOTKEY = "ctrl+shift+o"
FALLBACK_HOTKEY = "ctrl+shift+p"

_last_capture_time = 0.0
DEBOUNCE_SECONDS = 1.0

# --- Core capture -----------------------------------------------------------
def take_screenshot() -> Path | None:
    global _last_capture_time
    now = time.time()
    if now - _last_capture_time < DEBOUNCE_SECONDS:
        return None
    _last_capture_time = now

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = SCREENSHOT_DIR / f"shot_{timestamp}.png"

    try:
        time.sleep(0.15)
        img = pyautogui.screenshot()
        img.save(filename)
        print(f"[OK] Captured -> {filename}")
        return filename
    except Exception as e:
        print(f"[ERROR] Screenshot failed: {e}")
        return None

def on_hotkey(hotkey_name: str):
    def _handler():
        path = take_screenshot()
        if path:
            print(f"[HOTKEY:{hotkey_name}] saved {path.name}")
    return _handler

# --- Registration with suppression + fallback -------------------------------
def register_hotkeys():
    registered = []
    try:
        keyboard.add_hotkey(PRIMARY_HOTKEY, on_hotkey(PRIMARY_HOTKEY), suppress=True, trigger_on_release=False)
        registered.append(PRIMARY_HOTKEY)
    except Exception as e:
        print(f"[WARN] Could not register {PRIMARY_HOTKEY}: {e}")

    try:
        keyboard.add_hotkey(FALLBACK_HOTKEY, on_hotkey(FALLBACK_HOTKEY), suppress=True, trigger_on_release=False)
        registered.append(FALLBACK_HOTKEY)
    except Exception as e:
        print(f"[WARN] Could not register {FALLBACK_HOTKEY}: {e}")
    return registered

def main():
    if sys.platform == "win32" and not _is_admin():
        print("[WARN] Not running as admin. Hotkey suppression may not work.")

    hotkeys = register_hotkeys()
    if not hotkeys:
        print("[FATAL] No hotkeys could be registered. Exiting.")
        sys.exit(1)

    print("=" * 60)
    print(" OmniLearn Capture — running")
    print(f" Hotkeys active: {', '.join(hotkeys)}")
    print(f" Saving to:      {SCREENSHOT_DIR}")
    print(" Press Esc or Ctrl+C to quit.")
    print("=" * 60)

    try:
        keyboard.wait("esc")
    except KeyboardInterrupt:
        pass
    finally:
        keyboard.unhook_all()
        print("\n[STOPPED] Hotkeys released.")

def _is_admin() -> bool:
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return True

if __name__ == "__main__":
    main()
