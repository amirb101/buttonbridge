"""
Controller calibration - maps physical button aliases to logical GamepadButtons.

Stores per-controller mappings so Nintendo/Xbox/generic layouts all work correctly.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..core.gamepad_button import GamepadButton

logger = logging.getLogger(__name__)

# Buttons to calibrate in order (logical names)
CALIBRATION_ORDER = [
    GamepadButton.DPAD_UP,
    GamepadButton.DPAD_DOWN,
    GamepadButton.DPAD_LEFT,
    GamepadButton.DPAD_RIGHT,
    GamepadButton.A,
    GamepadButton.B,
    GamepadButton.X,
    GamepadButton.Y,
    GamepadButton.LEFT_SHOULDER,
    GamepadButton.RIGHT_SHOULDER,
    GamepadButton.LEFT_TRIGGER,
    GamepadButton.RIGHT_TRIGGER,
    GamepadButton.START,
    GamepadButton.SELECT,
]


@dataclass
class ControllerMapping:
    """Maps physical button aliases to logical GamepadButtons."""

    controller_name: str
    # Map: physical alias (lowercase normalized) -> logical GamepadButton
    alias_to_button: dict[str, GamepadButton] = field(default_factory=dict)
    is_complete: bool = False

    def get_button(self, alias: str) -> GamepadButton | None:
        """Get logical button for a physical alias (case-insensitive)."""
        normalized = "".join(c.lower() for c in alias if c.isalnum())
        return self.alias_to_button.get(normalized)


class CalibrationStore:
    """Persistent storage for controller mappings."""

    def __init__(self) -> None:
        self._path = Path.home() / ".config" / "pocket-study-remote" / "controller_mappings.json"
        self._cache: dict[str, ControllerMapping] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        """Load mappings from disk."""
        if not self._path.exists():
            return
        try:
            with open(self._path, "r") as f:
                data = json.load(f)
            for name, mapping_data in data.items():
                alias_map = {
                    k: GamepadButton[v] for k, v in mapping_data.get("aliases", {}).items()
                }
                self._cache[name] = ControllerMapping(
                    controller_name=name,
                    alias_to_button=alias_map,
                    is_complete=mapping_data.get("is_complete", False),
                )
            logger.info("Loaded %d controller mappings from %s", len(self._cache), self._path)
        except Exception as e:
            logger.warning("Failed to load controller mappings: %s", e)

    def _save(self) -> None:
        """Save mappings to disk."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                name: {
                    "aliases": {k: v.name for k, v in mapping.alias_to_button.items()},
                    "is_complete": mapping.is_complete,
                }
                for name, mapping in self._cache.items()
            }
            with open(self._path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save controller mappings: %s", e)

    def get_mapping(self, controller_name: str) -> ControllerMapping | None:
        """Get stored mapping for a controller, or None if not calibrated."""
        with self._lock:
            return self._cache.get(controller_name)

    def needs_calibration(self, controller_name: str) -> bool:
        """Check if controller needs calibration (new or incomplete)."""
        with self._lock:
            mapping = self._cache.get(controller_name)
            return mapping is None or not mapping.is_complete

    def save_mapping(self, mapping: ControllerMapping) -> None:
        """Save a completed mapping."""
        with self._lock:
            self._cache[mapping.controller_name] = mapping
            self._save()

    def clear_mapping(self, controller_name: str) -> None:
        """Clear mapping for a controller (force recalibration)."""
        with self._lock:
            if controller_name in self._cache:
                del self._cache[controller_name]
                self._save()

    def get_all_controller_names(self) -> list[str]:
        """Get list of all calibrated controller names."""
        with self._lock:
            return list(self._cache.keys())


# Global store instance
_store: CalibrationStore | None = None


def get_store() -> CalibrationStore:
    """Get the global calibration store."""
    global _store
    if _store is None:
        _store = CalibrationStore()
    return _store


class CalibrationWizard:
    """
    Interactive calibration using rumps notifications (non-blocking).

    Guides user through pressing each button in sequence.
    Uses notifications instead of blocking alerts so controller events still flow.
    """

    def __init__(
        self,
        controller_name: str,
        on_complete: Callable[[ControllerMapping], None],
        on_cancel: Callable[[], None],
    ) -> None:
        self.controller_name = controller_name
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.mapping = ControllerMapping(controller_name=controller_name)
        self.current_index = 0
        self.detected_aliases: set[str] = set()
        self._active = False
        self._last_press_time = 0.0
        self._timer = None
        self._waiting_for_press = False

    def start(self) -> None:
        """Start the calibration wizard."""
        import rumps

        # Reset state for fresh calibration
        self._active = True
        self._waiting_for_press = True
        self._last_press_time = time.time()
        self.current_index = 0
        self.detected_aliases.clear()
        self.mapping.alias_to_button.clear()
        self.mapping.is_complete = False

        self._show_current_prompt()

        # Auto-cancel after 2 minutes of inactivity
        def timeout_check():
            if not self._active:
                return
            # Check if it's been too long since last press
            now = time.time()
            if now - self._last_press_time > 120:  # 2 minutes
                logger.warning("[Calibration] Timeout - no button pressed for 2 minutes")
                self.cancel()

        def schedule_timeout(_timer):
            timeout_check()

        self._timeout_timer = rumps.Timer(schedule_timeout, 30.0)  # Check every 30s
        self._timeout_timer.start()

    def _show_current_prompt(self) -> None:
        """Show calibration prompt in menu bar title and notification."""
        import rumps
        from ..main import app as main_app

        if not self._active or self.current_index >= len(CALIBRATION_ORDER):
            return

        btn = CALIBRATION_ORDER[self.current_index]
        progress = f"{self.current_index + 1}/{len(CALIBRATION_ORDER)}"

        # Show in menu bar title (always visible)
        if main_app and hasattr(main_app, "show_calibration_prompt"):
            main_app.show_calibration_prompt(btn.display_name)

        # Also try notification (might not show if DND is on)
        try:
            rumps.notification(
                title=f"Calibration {progress}",
                subtitle=f"Press: {btn.display_name}",
                message=f"Step {progress} - Press this button on controller",
                sound=False,
            )
        except Exception:
            pass  # Notifications might fail

        logger.info("[Calibration] Waiting for: %s (%s)", btn.name, btn.display_name)

    def _advance(self) -> None:
        """Move to next button or finish."""
        import rumps

        self.current_index += 1
        self._waiting_for_press = True

        if self.current_index >= len(CALIBRATION_ORDER):
            self._finish()
        else:
            self._show_current_prompt()

    def on_button_event(self, alias: str, is_pressed: bool) -> bool:
        """
        Called when a button is pressed during calibration.
        Returns True if this button was consumed (should not propagate).
        """
        if not self._active or not is_pressed or not self._waiting_for_press:
            return False
        if self.current_index >= len(CALIBRATION_ORDER):
            return False

        # Debounce
        now = time.time()
        if now - self._last_press_time < 0.3:
            return True  # Consume but don't process
        self._last_press_time = now

        normalized = "".join(c.lower() for c in alias if c.isalnum())
        if normalized in self.detected_aliases:
            return True  # Already mapped, consume but don't re-add

        # Map this physical alias to the current logical button
        logical_button = CALIBRATION_ORDER[self.current_index]
        self.mapping.alias_to_button[normalized] = logical_button
        self.detected_aliases.add(normalized)

        logger.info("[Calibration] Mapped %s -> %s", alias, logical_button.name)

        # Advance to next
        self._waiting_for_press = False
        self._advance()
        return True

    def _finish(self) -> None:
        """Complete calibration."""
        import rumps
        from ..main import app as main_app

        self._active = False
        for t in (self._timer, getattr(self, '_timeout_timer', None)):
            if t:
                try:
                    t.stop()
                except Exception:
                    pass
        self._timer = None
        self._timeout_timer = None

        # Clear menu bar prompt
        if main_app and hasattr(main_app, "clear_calibration_prompt"):
            main_app.clear_calibration_prompt()

        self.mapping.is_complete = True
        get_store().save_mapping(self.mapping)

        rumps.notification(
            title="Calibration Complete!",
            subtitle=self.controller_name,
            message=f"Mapped {len(self.mapping.alias_to_button)} buttons",
            sound=True,
        )
        logger.info("[Calibration] Complete! Mapped %d buttons", len(self.mapping.alias_to_button))
        self.on_complete(self.mapping)

    def cancel(self) -> None:
        """Cancel calibration."""
        from ..main import app as main_app

        self._active = False
        self._waiting_for_press = False
        for t in (self._timer, getattr(self, '_timeout_timer', None)):
            if t:
                try:
                    t.stop()
                except Exception:
                    pass
        self._timer = None
        self._timeout_timer = None

        # Clear menu bar prompt
        if main_app and hasattr(main_app, "clear_calibration_prompt"):
            main_app.clear_calibration_prompt()

        self.on_cancel()
