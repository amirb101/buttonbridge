"""
AppDetector — polls NSWorkspace to track the frontmost application and
notifies a callback whenever it changes.

Polling rather than NSWorkspace notifications keeps threading simple:
NSWorkspace notifications require an AppKit run loop, which is owned by
the rumps main thread.  Polling from a separate daemon thread avoids any
entanglement and is perfectly adequate at 0.5 s resolution.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Optional

from AppKit import NSWorkspace  # type: ignore[import]

from ..constants import Detection

logger = logging.getLogger(__name__)

# Callback type: receives the new bundle identifier (or None)
AppChangeCallback = Callable[[Optional[str]], None]


class AppDetector:
    """
    Polls the frontmost application and calls ``on_app_change`` whenever it
    differs from the last observed value.

    Usage::

        def on_change(bundle_id):
            router.update_mode(bundle_id)

        detector = AppDetector(on_app_change=on_change)
        detector.start()
    """

    def __init__(self, on_app_change: AppChangeCallback) -> None:
        self._on_app_change = on_app_change
        self._current_bundle_id: str | None = None
        self._workspace = NSWorkspace.sharedWorkspace()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def current_bundle_identifier(self) -> str | None:
        return self._current_bundle_id

    def start(self) -> None:
        """Start the background polling thread. Non-blocking."""
        thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="AppDetectorThread",
        )
        thread.start()
        logger.info("AppDetector: poll thread started")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _run(self) -> None:
        # Emit once immediately so the router knows the starting mode.
        self._check()
        while True:
            time.sleep(Detection.POLL_INTERVAL_SECONDS)
            self._check()

    def _check(self) -> None:
        app = self._workspace.frontmostApplication()
        bundle_id: str | None = app.bundleIdentifier() if app else None

        if bundle_id == self._current_bundle_id:
            return

        self._current_bundle_id = bundle_id
        logger.info("Frontmost app bundle id: %s", bundle_id)
        self._on_app_change(bundle_id)
