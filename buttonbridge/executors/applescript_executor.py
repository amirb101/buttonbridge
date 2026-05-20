"""
AppleScriptExecutor — runs AppleScript source strings via `osascript`.

Using subprocess + osascript is simpler and more maintainable than
PyObjC's NSAppleScript, and has identical results for everything we need.

All execution is dispatched to a background thread so the AppleScript's
blocking call (typically 200–800 ms) never stalls the main thread or the
controller poll loop.

The ``Spotify`` and ``System`` inner classes hold pre-built script strings
to keep the mode definitions readable — modes call e.g.
``AppleScriptExecutor.Spotify.PLAYPAUSE`` rather than writing inline scripts.
"""

from __future__ import annotations

import logging
import subprocess
import threading
from typing import Callable

logger = logging.getLogger(__name__)

# Serial worker thread — serial (not a pool) so that additive commands like
# volume adjustments don't pile up and overshoot.
_queue: list[str] = []
_lock  = threading.Lock()
_sem   = threading.Semaphore(0)


def _worker() -> None:
    """Background thread: drains the script queue one item at a time."""
    while True:
        _sem.acquire()
        with _lock:
            if not _queue:
                continue
            source = _queue.pop(0)
        try:
            result = subprocess.run(
                ["osascript", "-e", source],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                logger.error("AppleScript error: %s", result.stderr.strip())
        except subprocess.TimeoutExpired:
            logger.error("AppleScript timed out: %.80s…", source)
        except Exception as exc:  # noqa: BLE001
            logger.error("AppleScript unexpected error: %s", exc)


_worker_thread = threading.Thread(target=_worker, daemon=True, name="AppleScriptWorker")
_worker_thread.start()


class AppleScriptExecutor:
    """Static-method namespace for running AppleScript."""

    @staticmethod
    def run(source: str) -> None:
        """
        Queue an AppleScript source string for async execution.

        Returns immediately — execution happens on the background worker thread.
        """
        with _lock:
            _queue.append(source)
        _sem.release()

    # ------------------------------------------------------------------
    # Spotify
    # ------------------------------------------------------------------

    class Spotify:
        """Pre-built AppleScript strings for Spotify commands."""

        PLAYPAUSE        = 'tell application "Spotify" to playpause'
        NEXT_TRACK       = 'tell application "Spotify" to next track'
        PREVIOUS_TRACK   = 'tell application "Spotify" to previous track'
        TOGGLE_SHUFFLE   = 'tell application "Spotify" to set shuffling to not shuffling'
        TOGGLE_REPEAT    = 'tell application "Spotify" to set repeating to not repeating'

        @staticmethod
        def adjust_volume(delta: int) -> str:
            return (
                f'tell application "Spotify" to '
                f'set sound volume to (sound volume + {delta})'
            )

        @staticmethod
        def seek_relative(seconds: float) -> str:
            return (
                f'tell application "Spotify" to '
                f'set player position to (player position + {seconds})'
            )

    # ------------------------------------------------------------------
    # System
    # ------------------------------------------------------------------

    class System:
        """Pre-built AppleScript strings for system-level commands."""

        TOGGLE_MUTE = """
            set isMuted to output muted of (get volume settings)
            set volume output muted (not isMuted)
        """

        @staticmethod
        def adjust_volume(delta: int) -> str:
            return f"""
                set currentVolume to output volume of (get volume settings)
                set volume output volume (currentVolume + {delta})
            """
