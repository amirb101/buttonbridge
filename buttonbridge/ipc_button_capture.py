"""
IPC mechanism for capturing controller button presses in the GUI.

The main app listens for button events and writes them to a shared file.
The GUI reads from this file to know which button was pressed.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

IPC_DIR = Path.home() / ".config" / "pocket-study-remote"
CAPTURE_FILE = IPC_DIR / "button_capture.json"
LISTENING_FILE = IPC_DIR / "listening_for_button"


def start_listening(mode_id: str, action_id: str) -> None:
    """Tell the main app we want to capture a button for this action."""
    IPC_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write listening flag
    data = {
        "mode_id": mode_id,
        "action_id": action_id,
        "timestamp": time.time(),
        "captured": None,
    }
    
    with open(LISTENING_FILE, "w") as f:
        json.dump(data, f)


def stop_listening() -> None:
    """Stop listening for button presses."""
    if LISTENING_FILE.exists():
        LISTENING_FILE.unlink()


def is_listening() -> bool:
    """Check if we should be capturing button presses."""
    return LISTENING_FILE.exists()


def get_capture_request() -> dict | None:
    """Get the current capture request (called by main app)."""
    if not LISTENING_FILE.exists():
        return None
    
    try:
        with open(LISTENING_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def capture_button(button_name: str, is_combo: bool = False, combo_buttons: list[str] | None = None) -> None:
    """Write a captured button to the capture file (called by main app)."""
    data = {
        "button": button_name,
        "is_combo": is_combo,
        "combo_buttons": combo_buttons or [],
        "timestamp": time.time(),
    }
    
    with open(CAPTURE_FILE, "w") as f:
        json.dump(data, f)


def get_captured_button(timeout: float = 30.0) -> dict | None:
    """Poll for a captured button (called by GUI)."""
    start = time.time()
    
    while time.time() - start < timeout:
        if CAPTURE_FILE.exists():
            try:
                with open(CAPTURE_FILE, "r") as f:
                    data = json.load(f)
                # Clear the file after reading
                CAPTURE_FILE.unlink()
                return data
            except Exception:
                pass
        
        time.sleep(0.05)
    
    return None


def clear_capture_file() -> None:
    """Clear any stale capture file."""
    if CAPTURE_FILE.exists():
        CAPTURE_FILE.unlink()
