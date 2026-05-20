"""Optional per-machine SDL button index → :class:`GamepadButton` overrides."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..constants import Controller
from ..core.gamepad_button import GamepadButton

logger = logging.getLogger(__name__)

_OVERRIDE_PATH = Path.home() / ".buttonbridge" / "pygame_button_map.json"

# Generic SDL / Xbox-style fallback.
_DEFAULT_MAP: dict[int, GamepadButton] = {
    Controller.ButtonIndex.A: GamepadButton.A,
    Controller.ButtonIndex.B: GamepadButton.B,
    Controller.ButtonIndex.X: GamepadButton.X,
    Controller.ButtonIndex.Y: GamepadButton.Y,
    Controller.ButtonIndex.L1: GamepadButton.LEFT_SHOULDER,
    Controller.ButtonIndex.R1: GamepadButton.RIGHT_SHOULDER,
    Controller.ButtonIndex.L2: GamepadButton.LEFT_TRIGGER,
    Controller.ButtonIndex.R2: GamepadButton.RIGHT_TRIGGER,
    Controller.ButtonIndex.SELECT: GamepadButton.SELECT,
    Controller.ButtonIndex.START: GamepadButton.START,
}

# 8BitDo Micro on macOS/SDL (from pygame logs): A=0, B=1, Y=4, X often 5, L1=6.
EIGHTBITDO_MICRO_MAP: dict[int, GamepadButton] = {
    0: GamepadButton.A,
    1: GamepadButton.B,
    4: GamepadButton.Y,
    5: GamepadButton.X,
    6: GamepadButton.LEFT_SHOULDER,
    7: GamepadButton.RIGHT_SHOULDER,
    8: GamepadButton.LEFT_TRIGGER,
    9: GamepadButton.RIGHT_TRIGGER,
    10: GamepadButton.SELECT,
    11: GamepadButton.START,
}


def map_for_controller_name(name: str | None) -> dict[int, GamepadButton]:
    """Pick a button map from the SDL device name."""
    if name and "8bitdo" in name.lower() and "micro" in name.lower():
        logger.info("Using 8BitDo Micro button map (A=0 B=1 X=5 Y=4 L1=6 …)")
        return dict(EIGHTBITDO_MICRO_MAP)
    return dict(_DEFAULT_MAP)


def load_button_index_map(controller_name: str | None = None) -> dict[int, GamepadButton]:
    """
    Return pygame ``JOYBUTTON*`` index → logical button.

    Create ``~/.buttonbridge/pygame_button_map.json`` after running
    ``python -m buttonbridge.tools.button_logger``::

        {"0": "A", "1": "B", "2": "X", "3": "Y"}
    """
    if not _OVERRIDE_PATH.exists():
        return map_for_controller_name(controller_name)

    try:
        with open(_OVERRIDE_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        out: dict[int, GamepadButton] = {}
        for key, name in raw.items():
            idx = int(key)
            if not isinstance(name, str) or name not in GamepadButton.__members__:
                raise ValueError(f"unknown GamepadButton {name!r}")
            btn = GamepadButton[name]
            out[idx] = btn
        logger.info("Loaded custom pygame button map from %s (%d entries)", _OVERRIDE_PATH, len(out))
        return out
    except Exception as e:
        logger.warning("Could not load %s (%s); using built-in map", _OVERRIDE_PATH, e)
        return map_for_controller_name(controller_name)
