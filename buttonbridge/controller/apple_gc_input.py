"""
Gamepad input via Apple's GameController framework (macOS).

This does **not** use pygame/SDL for discovery, so it works alongside rumps
without opening an SDL Cocoa window (which aborts when NSApplication already
exists — see ``sdl_bootstrap``).

Polls on the **main run loop** via ``NSTimer`` in **NSRunLoopCommonModes** so
ticks still fire while the status-item menu is tracking the mouse (default
mode timers often do not).

Uses ``extendedGamepad`` / ``gamepad`` / ``microGamepad`` when present; many
Bluetooth pads (DualSense, some 8BitDo modes) only expose **physicalInputProfile**
— we map aliases from ``allButtons`` / ``allAxes`` / ``allDpads`` to
``GamepadButton``.

``shouldMonitorBackgroundEvents`` keeps input flowing when other apps are key.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Callable

from Foundation import NSRunLoop, NSRunLoopCommonModes, NSTimer

from ..constants import Controller
from ..core.gamepad_button import GamepadButton
from .calibration import get_store, CalibrationWizard

logger = logging.getLogger(__name__)

ButtonChangeCallback = Callable[[GamepadButton, bool], None]
ConnectionChangeCallback = Callable[[bool], None]

_TH = Controller.TRIGGER_PRESS_THRESHOLD


def _objc_prop(obj, name: str):
    if obj is None:
        return None
    a = getattr(obj, name, None)
    if a is None:
        return None
    return a() if callable(a) else a


def _btn_press(inp) -> bool:
    if inp is None:
        return False
    try:
        return bool(inp.isPressed())
    except Exception:
        return False


def _axis(inp) -> float:
    if inp is None:
        return 0.0
    try:
        v = inp.value()
        return float(v) if v is not None else 0.0
    except Exception:
        pass
    try:
        return float(inp.value)
    except Exception:
        return 0.0


def _norm_alias(s: str) -> str:
    return "".join(c.lower() for c in s if c.isalnum())


def _iter_objc_collection(coll):
    """
    Iterate Objective-C collections returned by PyObjC.

    Handles NSArray-like (count/objectAtIndex_) and NSSet-like (objectEnumerator)
    objects used by GameController physicalInputProfile.
    """
    if coll is None:
        return
    # NSArray / NSIndexSet-style
    if hasattr(coll, "count") and hasattr(coll, "objectAtIndex_"):
        try:
            for i in range(coll.count()):
                yield coll.objectAtIndex_(i)
            return
        except Exception:
            pass
    # NSSet / NSEnumerator-style
    if hasattr(coll, "objectEnumerator"):
        try:
            it = coll.objectEnumerator()
            while True:
                obj = it.nextObject()
                if obj is None:
                    break
                yield obj
            return
        except Exception:
            pass
    # Python iterable fallback
    try:
        for obj in coll:
            yield obj
    except Exception:
        return


def _physical_alias_to_face_or_menu(n: str) -> GamepadButton | None:
    """Map GCPhysicalInputProfile button primaryAlias / localizedName → enum."""
    # D-pad (often separate digital elements)
    if "dpadup" in n or n == "up" and "dpad" in n:
        return GamepadButton.DPAD_UP
    if "dpaddown" in n or (n == "down" and "dpad" in n):
        return GamepadButton.DPAD_DOWN
    if "dpadleft" in n:
        return GamepadButton.DPAD_LEFT
    if "dpadright" in n:
        return GamepadButton.DPAD_RIGHT
    # Shoulders (before generic "left"/"right")
    if "leftshoulder" in n or "l1" == n or n.endswith("l1button"):
        return GamepadButton.LEFT_SHOULDER
    if "rightshoulder" in n or "r1" == n or n.endswith("r1button"):
        return GamepadButton.RIGHT_SHOULDER
    # Face — Xbox names
    if "buttona" in n or n == "a" or "buttoncross" in n or "cross" == n or "crossbutton" in n:
        return GamepadButton.A
    if "buttonb" in n or n == "b" or "buttoncircle" in n or "circle" == n or "circlebutton" in n:
        return GamepadButton.B
    if "buttonx" in n or n == "x" or "buttonsquare" in n or "square" == n or "squarebutton" in n:
        return GamepadButton.X
    if "buttony" in n or n == "y" or "buttontriangle" in n or "triangle" == n or "trianglebutton" in n:
        return GamepadButton.Y
    # Menu cluster
    if "buttonmenu" in n or "menu" in n or "start" in n or "home" in n or "logo" in n:
        return GamepadButton.START
    if "buttonoptions" in n or "options" in n or "select" in n or "share" in n or "view" in n or "back" in n:
        return GamepadButton.SELECT
    # Some pads expose L2/R2 as digital "button" elements
    if "lefttrigger" in n or "l2" in n or "lt" == n or "leftz" in n:
        return GamepadButton.LEFT_TRIGGER
    if "righttrigger" in n or "r2" in n or "rt" == n or "rightz" in n:
        return GamepadButton.RIGHT_TRIGGER
    return None


def _physical_alias_axis_to_trigger(n: str) -> GamepadButton | None:
    if "lefttrigger" in n or "l2" in n or n in ("lt", "ltaxis", "leftz"):
        return GamepadButton.LEFT_TRIGGER
    if "righttrigger" in n or "r2" in n or n in ("rt", "rtaxis", "rightz"):
        return GamepadButton.RIGHT_TRIGGER
    if "z" in n and "left" in n and "right" not in n:
        return GamepadButton.LEFT_TRIGGER
    if "z" in n and "right" in n:
        return GamepadButton.RIGHT_TRIGGER
    return None


def _physical_profile_has_inputs(pip) -> bool:
    if pip is None:
        return False
    try:
        b = pip.allButtons()
        if b is not None and b.count() > 0:
            return True
    except Exception:
        pass
    try:
        e = pip.allElements()
        if e is not None and e.count() > 0:
            return True
    except Exception:
        pass
    return False


def _schedule_timer_common_modes(interval: float, repeats: bool, block) -> NSTimer:
    """Like scheduledTimer… but runs during event tracking (status bar menus, drags)."""
    t = NSTimer.timerWithTimeInterval_repeats_block_(interval, repeats, block)
    NSRunLoop.currentRunLoop().addTimer_forMode_(t, NSRunLoopCommonModes)
    return t


class AppleGCControllerInput:
    """
    Same responsibilities as ``ControllerManager`` (pygame), different backend.
    """

    def __init__(
        self,
        on_button_change: ButtonChangeCallback,
        on_connection_changed: ConnectionChangeCallback | None = None,
    ) -> None:
        self._cb = on_button_change
        self._on_connection_changed = on_connection_changed
        self._connected = False
        self._last: dict[GamepadButton, bool] = {}
        self._logged_name = False
        self._timer: NSTimer | None = None
        self._last_empty_log = 0.0
        self._last_rediscover = 0.0
        self._logged_profile_gap = False
        self._current_controller_name: str | None = None
        self._calibration_wizard: Any = None
        self._on_calibration_complete: Callable[[], None] | None = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    def start(self) -> None:
        """Schedule polling on the main run loop (call from AppKit main thread)."""
        logger.info("AppleGCControllerInput.start() entered")
        logger.info(
            "GameController profile preference: %s (set BUTTONBRIDGE_GC_PROFILE=extended|physical|micro|auto)",
            os.environ.get("BUTTONBRIDGE_GC_PROFILE", "auto"),
        )
        from GameController import GCController

        try:
            GCController.setShouldMonitorBackgroundEvents_(True)
        except Exception as e:
            logger.debug("setShouldMonitorBackgroundEvents: %s", e)

        try:
            # PyObjC binding expects a no-arg completion block.
            GCController.startWirelessControllerDiscoveryWithCompletionHandler_(
                lambda: None
            )
        except Exception as e:
            logger.debug("startWirelessControllerDiscovery: %s", e)

        def stop_discovery(_timer) -> None:
            try:
                GCController.stopWirelessControllerDiscovery()
            except Exception as e:
                logger.debug("stopWirelessControllerDiscovery: %s", e)

        try:
            _schedule_timer_common_modes(8.0, False, stop_discovery)
        except Exception as e:
            logger.debug("schedule stopWirelessControllerDiscovery: %s", e)

        self._GCController = GCController
        try:
            self._poll(GCController)
        except Exception as e:
            logger.warning("GameController initial poll failed: %s", e)

        def tick(_timer) -> None:
            try:
                self._poll(GCController)
            except Exception as e:
                logger.warning("GameController poll failed: %s", e)

        self._timer = _schedule_timer_common_modes(
            Controller.POLL_INTERVAL_SECONDS,
            True,
            tick,
        )
        logger.info(
            "AppleGCControllerInput: timer on common run-loop modes (~%.0f Hz); "
            "physicalInputProfile fallback enabled",
            1.0 / Controller.POLL_INTERVAL_SECONDS,
        )

    def _pick_controller(self, GCController):
        prefer = os.environ.get("BUTTONBRIDGE_GC_PROFILE", "auto").strip().lower()
        for c in GCController.controllers():
            pip = _objc_prop(c, "physicalInputProfile")
            ext = _objc_prop(c, "extendedGamepad") or _objc_prop(c, "gamepad")
            micro = _objc_prop(c, "microGamepad")
            physical = pip if _physical_profile_has_inputs(pip) else None

            if prefer in ("physical", "pip"):
                if physical is not None:
                    return c, physical, "physical"
                if ext is not None:
                    return c, ext, "extended"
                if micro is not None:
                    return c, micro, "micro"
                continue

            if prefer in ("extended", "ext"):
                if ext is not None:
                    return c, ext, "extended"
                if physical is not None:
                    return c, physical, "physical"
                if micro is not None:
                    return c, micro, "micro"
                continue

            if prefer == "micro":
                if micro is not None:
                    return c, micro, "micro"
                if physical is not None:
                    return c, physical, "physical"
                if ext is not None:
                    return c, ext, "extended"
                continue

            # auto: extended -> physical -> micro
            if ext is not None:
                return c, ext, "extended"
            if physical is not None:
                return c, physical, "physical"
            if micro is not None:
                return c, micro, "micro"
        return None, None, None

    def _poll(self, GCController) -> None:
        # Check if paused for configuration
        if getattr(self, "_paused_for_config", False):
            return  # Skip processing while GUI is configuring

        ctrls = GCController.controllers()
        n = len(ctrls)
        ctrl, pad, kind = self._pick_controller(GCController)

        now = time.monotonic()
        if n == 0:
            if now - self._last_empty_log >= 30.0:
                self._last_empty_log = now
                logger.warning(
                    "GameController: 0 devices. Open **System Settings → Game Controllers** — if the "
                    "pad is not listed, macOS does not expose it to GameController (try **X** or **S** "
                    "mode on 8BitDo, or disconnect/reconnect). This app cannot see pure D-input HID "
                    "pads through Apple’s API."
                )
            if now - self._last_rediscover >= 45.0:
                self._last_rediscover = now
                try:
                    GCController.startWirelessControllerDiscoveryWithCompletionHandler_(
                        lambda err: None,
                    )
                except Exception:
                    pass

        if n > 0 and pad is None and not self._logged_profile_gap:
            self._logged_profile_gap = True
            for c in ctrls:
                vn = _objc_prop(c, "vendorName")
                logger.warning(
                    "GameController sees a device (%r) but no extended/gamepad/micro profile and "
                    "no physicalInputProfile buttons — macOS may not support this device for GC.",
                    vn,
                )

        was_connected = self._connected
        self._connected = pad is not None

        if not self._connected:
            if was_connected:
                logger.info("GameController disconnected")
                if self._on_connection_changed:
                    self._on_connection_changed(False)
            for b, prev in list(self._last.items()):
                if prev:
                    self._cb(b, False)
            self._last.clear()
            self._logged_name = False
            if n == 0:
                self._logged_profile_gap = False
            return

        if not self._logged_name:
            self._logged_name = True
            name = _objc_prop(ctrl, "vendorName") or "controller"
            self._current_controller_name = name
            logger.info("GameController connected: %s (profile=%s)", name, kind)
            if self._on_connection_changed:
                self._on_connection_changed(True)

            # Check if calibration needed
            store = get_store()
            if store.needs_calibration(name):
                logger.info("Controller '%s' needs calibration - use 'Calibrate Controller' from menu", name)

        # Check if we're in button capture mode (for keybinding GUI)
        from ..ipc_button_capture import is_listening, capture_button
        if is_listening() and pad is not None:
            captured = self._check_for_capture(pad, kind)
            if captured:
                capture_button(captured)
                return  # Don't process as normal input

        if kind == "micro":
            self._poll_micro(pad)
        elif kind == "physical":
            self._poll_physical(pad)
        else:
            self._poll_extended(pad)

    def _check_for_capture(self, pad, kind: str) -> str | None:
        """Check if any button is pressed for capture mode. Returns button name if pressed."""
        buttons_to_check = [
            ("buttonA", GamepadButton.A),
            ("buttonB", GamepadButton.B),
            ("buttonX", GamepadButton.X),
            ("buttonY", GamepadButton.Y),
            ("leftShoulder", GamepadButton.LEFT_SHOULDER),
            ("rightShoulder", GamepadButton.RIGHT_SHOULDER),
            ("leftTrigger", GamepadButton.LEFT_TRIGGER),
            ("rightTrigger", GamepadButton.RIGHT_TRIGGER),
        ]
        
        for btn_prop, btn_enum in buttons_to_check:
            val = _objc_prop(pad, btn_prop)
            if val is not None and _btn_press(val):
                return btn_enum.name
        
        # Check D-pad
        dpad = _objc_prop(pad, "dpad")
        if dpad:
            if _btn_press(_objc_prop(dpad, "up")):
                return GamepadButton.DPAD_UP.name
            if _btn_press(_objc_prop(dpad, "down")):
                return GamepadButton.DPAD_DOWN.name
            if _btn_press(_objc_prop(dpad, "left")):
                return GamepadButton.DPAD_LEFT.name
            if _btn_press(_objc_prop(dpad, "right")):
                return GamepadButton.DPAD_RIGHT.name
        
        # Check menu buttons
        menu = _objc_prop(pad, "buttonMenu")
        if menu and _btn_press(menu):
            return GamepadButton.START.name
        
        options = _objc_prop(pad, "buttonOptions")
        if options and _btn_press(options):
            return GamepadButton.SELECT.name
        
        return None

    def _poll_micro(self, pad) -> None:
        dpad = _objc_prop(pad, "dpad")
        state: dict[GamepadButton, bool] = {
            GamepadButton.A: _btn_press(_objc_prop(pad, "buttonA")),
            GamepadButton.B: False,
            GamepadButton.X: _btn_press(_objc_prop(pad, "buttonX")),
            GamepadButton.Y: False,
            GamepadButton.LEFT_SHOULDER: False,
            GamepadButton.RIGHT_SHOULDER: False,
            GamepadButton.LEFT_TRIGGER: False,
            GamepadButton.RIGHT_TRIGGER: False,
            GamepadButton.DPAD_UP: _btn_press(_objc_prop(dpad, "up")),
            GamepadButton.DPAD_DOWN: _btn_press(_objc_prop(dpad, "down")),
            GamepadButton.DPAD_LEFT: _btn_press(_objc_prop(dpad, "left")),
            GamepadButton.DPAD_RIGHT: _btn_press(_objc_prop(dpad, "right")),
            GamepadButton.START: _btn_press(_objc_prop(pad, "buttonMenu")),
            GamepadButton.SELECT: False,
        }
        self._emit_changes(state)

    def _poll_extended(self, pad) -> None:
        dpad = _objc_prop(pad, "dpad")
        state: dict[GamepadButton, bool] = {
            GamepadButton.A: _btn_press(_objc_prop(pad, "buttonA")),
            GamepadButton.B: _btn_press(_objc_prop(pad, "buttonB")),
            GamepadButton.X: _btn_press(_objc_prop(pad, "buttonX")),
            GamepadButton.Y: _btn_press(_objc_prop(pad, "buttonY")),
            GamepadButton.LEFT_SHOULDER: _btn_press(_objc_prop(pad, "leftShoulder")),
            GamepadButton.RIGHT_SHOULDER: _btn_press(_objc_prop(pad, "rightShoulder")),
            GamepadButton.LEFT_TRIGGER: _axis(_objc_prop(pad, "leftTrigger")) >= _TH,
            GamepadButton.RIGHT_TRIGGER: _axis(_objc_prop(pad, "rightTrigger")) >= _TH,
            GamepadButton.DPAD_UP: _btn_press(_objc_prop(dpad, "up")),
            GamepadButton.DPAD_DOWN: _btn_press(_objc_prop(dpad, "down")),
            GamepadButton.DPAD_LEFT: _btn_press(_objc_prop(dpad, "left")),
            GamepadButton.DPAD_RIGHT: _btn_press(_objc_prop(dpad, "right")),
            GamepadButton.START: _btn_press(_objc_prop(pad, "buttonMenu")),
            GamepadButton.SELECT: _btn_press(_objc_prop(pad, "buttonOptions")),
        }
        self._emit_changes(state)

    def _poll_physical(self, pip) -> None:
        state: dict[GamepadButton, bool] = {b: False for b in GamepadButton}
        # Track which physical alias produced each logical button (for calibration)
        physical_aliases: dict[GamepadButton, str] = {}

        try:
            buttons = pip.allButtons()
            if buttons is not None:
                for el in _iter_objc_collection(buttons):
                    alias = str(
                        _objc_prop(el, "primaryAlias")
                        or _objc_prop(el, "localizedName")
                        or _objc_prop(el, "unmappedLocalizedName")
                        or "",
                    )
                    n = _norm_alias(alias)
                    gpb = _physical_alias_to_face_or_menu(n)
                    if gpb is None:
                        continue
                    if gpb in (GamepadButton.LEFT_TRIGGER, GamepadButton.RIGHT_TRIGGER):
                        if _btn_press(el) or _axis(el) >= _TH:
                            state[gpb] = True
                            physical_aliases[gpb] = alias
                    elif _btn_press(el):
                        state[gpb] = True
                        physical_aliases[gpb] = alias
        except Exception as e:
            logger.debug("physical allButtons: %s", e)

        try:
            axes = pip.allAxes()
            if axes is not None:
                for el in _iter_objc_collection(axes):
                    alias = str(
                        _objc_prop(el, "primaryAlias")
                        or _objc_prop(el, "localizedName")
                        or "",
                    )
                    gpb = _physical_alias_axis_to_trigger(_norm_alias(alias))
                    if gpb is not None and _axis(el) >= _TH:
                        state[gpb] = True
                        physical_aliases[gpb] = alias
        except Exception as e:
            logger.debug("physical allAxes: %s", e)

        try:
            dpads = pip.allDpads()
            if dpads is not None:
                for dpad in _iter_objc_collection(dpads):
                    if _btn_press(_objc_prop(dpad, "up")):
                        state[GamepadButton.DPAD_UP] = True
                        physical_aliases[GamepadButton.DPAD_UP] = "dpadup"
                    if _btn_press(_objc_prop(dpad, "down")):
                        state[GamepadButton.DPAD_DOWN] = True
                        physical_aliases[GamepadButton.DPAD_DOWN] = "dpaddown"
                    if _btn_press(_objc_prop(dpad, "left")):
                        state[GamepadButton.DPAD_LEFT] = True
                        physical_aliases[GamepadButton.DPAD_LEFT] = "dpadleft"
                    if _btn_press(_objc_prop(dpad, "right")):
                        state[GamepadButton.DPAD_RIGHT] = True
                        physical_aliases[GamepadButton.DPAD_RIGHT] = "dpadright"
        except Exception as e:
            logger.debug("physical allDpads: %s", e)

        self._emit_changes(state, physical_aliases if physical_aliases else None)

    def _emit_changes(self, state: dict[GamepadButton, bool], physical_aliases: dict[GamepadButton, str] | None = None) -> None:
        """
        Emit button changes, applying calibration if available.

        If physical_aliases is provided, we'll use calibration mapping to translate
        physical button names to logical buttons.
        """
        # Get calibration mapping if available
        store = get_store()
        mapping = None
        if self._current_controller_name:
            mapping = store.get_mapping(self._current_controller_name)

        # If we have a mapping and physical aliases, translate
        if mapping and mapping.is_complete and physical_aliases:
            translated_state: dict[GamepadButton, bool] = {b: False for b in GamepadButton}
            for logical_btn, pressed in state.items():
                if not pressed:
                    continue
                # Find physical alias for this logical button
                alias = physical_aliases.get(logical_btn)
                if alias:
                    # Get mapped logical button from calibration
                    mapped_btn = mapping.get_button(alias)
                    if mapped_btn:
                        translated_state[mapped_btn] = True
                    else:
                        # No mapping for this alias, pass through
                        translated_state[logical_btn] = True
                else:
                    translated_state[logical_btn] = True
            state = translated_state

        for btn, pressed in state.items():
            prev = self._last.get(btn, False)
            if pressed != prev:
                self._cb(btn, pressed)
        self._last = dict(state)

    def start_calibration(self, on_complete: Callable[[], None] | None = None) -> bool:
        """
        Start calibration wizard for current controller.
        Returns True if calibration started, False if no controller connected.
        """
        if not self._current_controller_name:
            logger.warning("Cannot calibrate: no controller connected")
            return False

        self._on_calibration_complete = on_complete

        def on_complete_mapping(mapping):
            logger.info("Calibration complete for '%s'", mapping.controller_name)
            if self._on_calibration_complete:
                self._on_calibration_complete()
            self._calibration_wizard = None

        def on_cancel():
            logger.info("Calibration cancelled")
            self._calibration_wizard = None

        self._calibration_wizard = CalibrationWizard(
            self._current_controller_name,
            on_complete_mapping,
            on_cancel,
        )
        self._calibration_wizard.start()
        return True

    def on_button_event_for_calibration(self, alias: str, is_pressed: bool) -> bool:
        """
        Pass button events to calibration wizard if active.
        Returns True if event was consumed by calibration.
        """
        if self._calibration_wizard and self._calibration_wizard._active:
            return self._calibration_wizard.on_button_event(alias, is_pressed)
        return False

    def clear_calibration(self) -> bool:
        """Clear calibration for current controller."""
        if not self._current_controller_name:
            return False
        get_store().clear_mapping(self._current_controller_name)
        logger.info("Cleared calibration for '%s'", self._current_controller_name)
        return True
