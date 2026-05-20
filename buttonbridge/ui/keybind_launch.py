"""Launch the keybind / hotkey GUI in a subprocess (separate Tk main loop)."""

from __future__ import annotations

import subprocess
import sys


def launch_keybinding_gui(readonly: bool = False) -> bool:
    """Run ``keybind_gui`` in a child process. Returns True if exit code was 0."""
    frozen = getattr(sys, "frozen", False)
    if frozen:
        cmd = [sys.executable, "--buttonbridge-keybind-gui"]
    else:
        cmd = [sys.executable, "-m", "buttonbridge", "--buttonbridge-keybind-gui"]
    if readonly:
        cmd.append("--readonly")
    result = subprocess.run(cmd, check=False)
    return result.returncode == 0
