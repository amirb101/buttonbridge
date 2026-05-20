"""
ActionRouter — the central coordinator between controller input and actions.

Responsibilities:
1. Tracks the active mode (updated by AppDetector via ``update_mode``).
2. Tracks which buttons are currently held (for combo detection).
3. Resolves button presses: checks combos first, falls through to
   single-button actions.
4. Fires the resolved action.

Threading:
    Button events arrive from the ControllerManager poll thread.
    App-change events arrive from the AppDetector poll thread.
    Both call into ActionRouter on their respective threads.

    ActionRouter uses a threading.Lock to protect ``_current_mode`` and
    ``_held_buttons``.  Action dispatch (``action.perform()``) is called
    while NOT holding the lock, so long-running actions (AppleScript) never
    block controller input.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable

from ..core.app_mode import AppMode
from ..core.button_combo import ButtonCombo
from ..core.gamepad_button import GamepadButton
from ..core.mode_registry import ModeRegistry

logger = logging.getLogger(__name__)


class ActionRouter:
    """
    Routes button presses to actions based on the active mode.

    Args:
        registry:        Populated ``ModeRegistry``.
        on_mode_changed: Optional callback fired (with the new mode) whenever
                         the active mode changes.  Use this to update the
                         status bar label and trigger the overlay.
    """

    def __init__(
        self,
        registry: ModeRegistry,
        on_mode_changed: Callable[[AppMode], None] | None = None,
    ) -> None:
        self._registry        = registry
        self._on_mode_changed = on_mode_changed
        self._lock            = threading.Lock()
        self._current_mode: AppMode           = registry.fallback
        self._held_buttons:  set[GamepadButton] = set()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_mode(self) -> AppMode:
        with self._lock:
            return self._current_mode

    # ------------------------------------------------------------------
    # Called by AppDetector
    # ------------------------------------------------------------------

    def update_mode(self, bundle_identifier: str | None) -> None:
        """Switch to the mode registered for ``bundle_identifier``."""
        new_mode = self._registry.mode_for(bundle_identifier)

        with self._lock:
            if new_mode.id == self._current_mode.id:
                return
            self._current_mode = new_mode
            self._held_buttons.clear()   # stale held state is meaningless after a mode switch

        logger.info("Mode changed → %s", new_mode.display_name)

        if self._on_mode_changed:
            self._on_mode_changed(new_mode)

    # ------------------------------------------------------------------
    # Called by ControllerManager
    # ------------------------------------------------------------------

    def button_changed(self, button: GamepadButton, is_pressed: bool) -> None:
        """Process a button press or release."""
        action = None
        mode_label = ""

        with self._lock:
            if is_pressed:
                self._held_buttons.add(button)
                action = self._resolve(button)
                mode_label = self._current_mode.display_name
            else:
                self._held_buttons.discard(button)

        # Fire outside the lock so AppleScript/keystroke calls don't block input.
        if is_pressed:
            if action is not None:
                logger.info(
                    "INPUT button=%s  keys=%s  in_mode=%s  effect=%s  action_id=%s",
                    button.display_name,
                    action.shortcut_repr or "—",
                    mode_label,
                    action.display_name,
                    action.id,
                )
                action()
            else:
                logger.info(
                    "INPUT button=%s  keys=—  in_mode=%s  effect=(no binding)  action_id=—",
                    button.display_name,
                    mode_label,
                )

    # ------------------------------------------------------------------
    # Private: dispatch logic
    # ------------------------------------------------------------------

    def _resolve(self, pressed: GamepadButton):
        """
        Return the action to fire for the newly pressed button.

        Combos are checked first.  A combo fires only when the pressed
        button completes its full button set — all other members must
        already be held.  If no combo matches, return the single-button
        action (or None if unassigned).
        """
        mode = self._current_mode
        held = self._held_buttons   # already includes ``pressed``

        # 1. Check combos
        for combo, action in mode.combo_map.items():
            if pressed in combo.buttons and combo.matches(held):
                logger.debug("Combo fired: %s → %s", combo.buttons, action.id)
                return action

        # 2. Single-button action
        action = mode.button_map.get(pressed)
        if action:
            logger.debug("Button fired: %s → %s", pressed.display_name, action.id)
        return action
