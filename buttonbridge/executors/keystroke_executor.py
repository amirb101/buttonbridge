"""
KeystrokeExecutor — sends keyboard shortcuts via the macOS Core Graphics
event system (the same low-level channel as physical key presses).

Requires the Accessibility permission granted at first launch.
"""

from __future__ import annotations

import logging
from typing import Sequence

from Quartz import (  # type: ignore[import]
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetFlags,
    CGEventSourceCreate,
    kCGEventFlagMaskAlternate,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
    kCGHIDEventTap,
    kCGEventSourceStateHIDSystemState,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Modifier flag lookup
# ---------------------------------------------------------------------------

_MODIFIER_FLAGS: dict[str, int] = {
    "cmd":   kCGEventFlagMaskCommand,
    "shift": kCGEventFlagMaskShift,
    "opt":   kCGEventFlagMaskAlternate,
    "ctrl":  kCGEventFlagMaskControl,
}

# ---------------------------------------------------------------------------
# Key code lookup  (kVK_* values from Carbon HIToolbox/Events.h)
# ---------------------------------------------------------------------------

_KEY_CODES: dict[str, int] = {
    # Letters
    "a": 0,  "b": 11, "c": 8,  "d": 2,  "e": 14, "f": 3,
    "g": 5,  "h": 4,  "i": 34, "j": 38, "k": 40, "l": 37,
    "m": 46, "n": 45, "o": 31, "p": 35, "q": 12, "r": 15,
    "s": 1,  "t": 17, "u": 32, "v": 9,  "w": 13, "x": 7,
    "y": 16, "z": 6,

    # Numbers
    "0": 29, "1": 18, "2": 19, "3": 20, "4": 21,
    "5": 23, "6": 22, "7": 26, "8": 28, "9": 25,

    # Punctuation
    "left_bracket":  33,   # [
    "right_bracket": 30,   # ]
    "backslash":     42,   # \
    "semicolon":     41,
    "apostrophe":    39,
    "comma":         43,
    "period":        47,
    "slash":         44,
    "grave":         50,   # `
    "minus":         27,
    "equal":         24,

    # Navigation
    "left_arrow":  123,
    "right_arrow": 124,
    "down_arrow":  125,
    "up_arrow":    126,
    "page_up":     116,
    "page_down":   121,
    "home":        115,
    "end":         119,

    # Special
    "delete":         51,
    "forward_delete": 117,
    "escape":         53,
    "return":         36,
    "space":          49,
    "tab":            48,

    # Function keys
    "f1": 122, "f2": 120, "f3": 99,  "f4": 118,
    "f5": 96,  "f6": 97,  "f7": 98,  "f8": 100,
    "f9": 101, "f10": 109,"f11": 103,"f12": 111,
}


class KeystrokeExecutor:
    """
    Static-method namespace for sending keyboard shortcuts.

    All public methods are class-level and require no instantiation.
    """

    @classmethod
    def send(cls, key: str, modifiers: Sequence[str] = ()) -> None:
        """
        Post a key-down + key-up event pair for the given key and modifiers.

        Args:
            key:       Key name matching a key in ``_KEY_CODES``
                       (e.g. ``"t"``, ``"left_bracket"``).
            modifiers: Modifier names from ``_MODIFIER_FLAGS``
                       (``"cmd"``, ``"shift"``, ``"opt"``, ``"ctrl"``).
        """
        key_code = _KEY_CODES.get(key)
        if key_code is None:
            logger.error("KeystrokeExecutor: unknown key %r", key)
            return

        flags = 0
        for mod in modifiers:
            flag = _MODIFIER_FLAGS.get(mod)
            if flag is None:
                logger.warning("KeystrokeExecutor: unknown modifier %r", mod)
                continue
            flags |= flag

        source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

        key_down = CGEventCreateKeyboardEvent(source, key_code, True)
        key_up   = CGEventCreateKeyboardEvent(source, key_code, False)

        if flags:
            CGEventSetFlags(key_down, flags)
            CGEventSetFlags(key_up,   flags)

        CGEventPost(kCGHIDEventTap, key_down)
        CGEventPost(kCGHIDEventTap, key_up)

        logger.debug("Keystroke: %r modifiers=%r", key, list(modifiers))
