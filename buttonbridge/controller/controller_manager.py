"""
ControllerManager — reads gamepad input from the 8BitDo Micro via pygame
and translates raw hardware events into typed ``GamepadButton`` presses.

Design goals:
- All pygame I/O runs on a single dedicated daemon thread.
- The rest of the app never touches pygame directly.
- Button-to-enum mapping is fully contained here; changing hardware or
  firmware requires only editing this file.

Threading:
    The polling loop runs on ``_PollThread``.  When a button changes state,
    it calls ``on_button_change(button, is_pressed)`` on whichever thread
    the callback runs on — callers should dispatch to their own thread if
    needed.  ``ActionRouter`` handles this via its own thread-safe queue.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Callable

from ..constants import Controller
from ..core.gamepad_button import GamepadButton
from ..sdl_bootstrap import bootstrap_pygame_for_menu_bar_app, configure_sdl_env
from .raw_button_map import load_button_index_map

logger = logging.getLogger(__name__)

# Callback type: (button, is_pressed)
ButtonChangeCallback = Callable[[GamepadButton, bool], None]
ConnectionChangeCallback = Callable[[bool], None]


class ControllerManager:
    """
    Manages controller discovery and input translation.

    Usage::

        def on_button(button, is_pressed):
            if is_pressed:
                router.button_pressed(button)
            else:
                router.button_released(button)

        mgr = ControllerManager(on_button_change=on_button)
        mgr.start()   # non-blocking; starts background poll thread
    """

    def __init__(
        self,
        on_button_change: ButtonChangeCallback,
        on_connection_changed: ConnectionChangeCallback | None = None,
    ) -> None:
        self._on_button_change = on_button_change
        self._on_connection_changed = on_connection_changed
        self._connected = False
        self._poll_thread: threading.Thread | None = None
        self._last_no_joystick_log = 0.0
        self._button_index_map: dict[int, GamepadButton] = {}
        self._last_down_monotonic: dict[int, float] = {}
        burst_ms = os.environ.get("BUTTONBRIDGE_BURST_MS", "40")
        try:
            self._burst_seconds = max(0.0, float(burst_ms) / 1000.0)
        except ValueError:
            self._burst_seconds = 0.04
        self._last_burst_down = 0.0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        return self._connected

    def start(self) -> None:
        """Start the background polling thread. Non-blocking."""
        # Main thread (rumps). Never use pygame.display here — SDL Cocoa + rumps aborts on macOS 26+.
        bootstrap_pygame_for_menu_bar_app()
        self._poll_thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="ControllerPollThread",
        )
        self._poll_thread.start()
        logger.info("ControllerManager: poll thread started")

    # ------------------------------------------------------------------
    # Private: poll loop
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """
        Entry point for the poll thread.

        Main thread already ran :func:`bootstrap_pygame_for_menu_bar_app` (dummy SDL video with rumps).
        """
        configure_sdl_env(embedded_with_rumps=True)
        import pygame

        if not pygame.get_init():
            pygame.init()
        pygame.joystick.init()

        joystick: pygame.joystick.JoystickType | None = None

        logger.info(
            "ControllerManager: poll loop ready (joystick count=%d)",
            pygame.joystick.get_count(),
        )

        while True:
            # -- Controller connect / disconnect ---------------------------
            count = pygame.joystick.get_count()
            if count > 0 and joystick is None:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                self._connected = True
                name = joystick.get_name()
                self._button_index_map = load_button_index_map(name)
                # macOS often shows "Wireless Controller" / "DUALSHOCK 4" / "8BitDo …" — all are fine here.
                logger.info("Controller connected (pygame/SDL): %s", name)
                if self._on_connection_changed:
                    self._on_connection_changed(True)

            elif count == 0 and joystick is None:
                # pygame only sees what SDL enumerates; Bluetooth + dummy video can be finicky on macOS.
                now = time.monotonic()
                if now - self._last_no_joystick_log >= 12.0:
                    self._last_no_joystick_log = now
                    logger.warning(
                        "Pygame still sees 0 joysticks. Try: quit Steam; enable Input Monitoring for "
                        "Terminal/Python; re-pair the controller; SDL_JOYSTICK_HIDAPI=0 or =1. "
                        "Diagnostic: python -m buttonbridge.tools.button_logger"
                    )

            elif count == 0 and joystick is not None:
                joystick = None
                self._connected = False
                logger.info("Controller disconnected")
                if self._on_connection_changed:
                    self._on_connection_changed(False)

            # -- Event processing -----------------------------------------
            for event in pygame.event.get():
                if joystick is None:
                    continue

                if event.type == pygame.JOYBUTTONDOWN:
                    if self._accept_button_down(event.button):
                        button = _button_from_index(event.button, self._button_index_map)
                        if button:
                            logger.info(
                                "JOY raw index=%d → %s (down)",
                                event.button,
                                button.display_name,
                            )
                            self._on_button_change(button, True)

                elif event.type == pygame.JOYBUTTONUP:
                    button = _button_from_index(
                        event.button, self._button_index_map, log_if_missing=False
                    )
                    if button:
                        self._on_button_change(button, False)

                elif event.type == pygame.JOYHATMOTION:
                    self._handle_hat_motion(event.value)

                elif event.type == pygame.JOYAXISMOTION:
                    # Some firmware versions expose L2/R2 as axes (−1 to +1).
                    button = _trigger_from_axis(event.axis, event.value)
                    if button:
                        is_pressed = event.value >= Controller.TRIGGER_PRESS_THRESHOLD
                        self._on_button_change(button, is_pressed)

            time.sleep(Controller.POLL_INTERVAL_SECONDS)

    def _accept_button_down(self, raw_index: int) -> bool:
        """Drop duplicate / ghost presses (common on 8BitDo D-input via SDL)."""
        now = time.monotonic()
        last = self._last_down_monotonic.get(raw_index)
        if last is not None and (now - last) < 0.08:
            return False
        self._last_down_monotonic[raw_index] = now

        if self._burst_seconds > 0 and (now - self._last_burst_down) < self._burst_seconds:
            logger.debug(
                "Ignoring raw button %d (%.0fms after previous down; burst window)",
                raw_index,
                (now - self._last_burst_down) * 1000,
            )
            return False
        self._last_burst_down = now
        return True

    def _handle_hat_motion(self, value: tuple[int, int]) -> None:
        """D-pad hat: release all directions on centre; one direction on tilt."""
        if value == (0, 0):
            for btn in (
                GamepadButton.DPAD_UP,
                GamepadButton.DPAD_DOWN,
                GamepadButton.DPAD_LEFT,
                GamepadButton.DPAD_RIGHT,
            ):
                self._on_button_change(btn, False)
            return
        button = _button_from_hat(value, self._swap_dpad_left_right())
        if button:
            self._on_button_change(button, True)

    @staticmethod
    def _swap_dpad_left_right() -> bool:
        return os.environ.get("BUTTONBRIDGE_SWAP_DPAD_LR", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )


# ---------------------------------------------------------------------------
# Hardware mapping helpers
#
# These translate raw pygame indices/values → typed GamepadButton enums.
# If your controller feels wrong, run:
#   python -m buttonbridge.tools.button_logger
# and update the indices here.
# ---------------------------------------------------------------------------

_HAT_DIRECTION_MAP: dict[tuple[int, int], GamepadButton] = {
    Controller.HatDirection.UP:    GamepadButton.DPAD_UP,
    Controller.HatDirection.DOWN:  GamepadButton.DPAD_DOWN,
    Controller.HatDirection.LEFT:  GamepadButton.DPAD_LEFT,
    Controller.HatDirection.RIGHT: GamepadButton.DPAD_RIGHT,
}

_TRIGGER_AXIS_MAP: dict[int, GamepadButton] = {
    Controller.AxisIndex.LEFT_TRIGGER:  GamepadButton.LEFT_TRIGGER,
    Controller.AxisIndex.RIGHT_TRIGGER: GamepadButton.RIGHT_TRIGGER,
}


def _button_from_index(
    index: int,
    index_map: dict[int, GamepadButton],
    *,
    log_if_missing: bool = True,
) -> GamepadButton | None:
    result = index_map.get(index)
    if result is None and log_if_missing:
        logger.info(
            "Unmapped pygame button index %d — run: python -m buttonbridge.tools.button_logger "
            "then add to ~/.buttonbridge/pygame_button_map.json",
            index,
        )
    return result


def _button_from_hat(
    value: tuple[int, int],
    swap_left_right: bool = False,
) -> GamepadButton | None:
    if value == (0, 0):
        return None
    if swap_left_right and value in (
        Controller.HatDirection.LEFT,
        Controller.HatDirection.RIGHT,
    ):
        value = (
            Controller.HatDirection.RIGHT
            if value == Controller.HatDirection.LEFT
            else Controller.HatDirection.LEFT
        )
    return _HAT_DIRECTION_MAP.get(value)


def _trigger_from_axis(axis: int, value: float) -> GamepadButton | None:
    return _TRIGGER_AXIS_MAP.get(axis)
