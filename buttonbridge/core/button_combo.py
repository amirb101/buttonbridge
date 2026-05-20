"""Multi-button combo type."""

from __future__ import annotations
from dataclasses import dataclass

from .gamepad_button import GamepadButton


@dataclass(frozen=True)
class ButtonCombo:
    """
    A set of buttons that must all be held simultaneously to trigger a
    composite action.

    Combos are checked before single-button actions: when a button press
    completes a registered combo, only the combo fires — the individual
    button actions do not.

    Example::

        # A alone → new tab.  A + B together → bookmark.
        combo = ButtonCombo(GamepadButton.A, GamepadButton.B)
    """

    buttons: frozenset[GamepadButton]

    def __init__(self, *buttons: GamepadButton) -> None:
        if len(buttons) < 2:
            raise ValueError("A combo requires at least two buttons.")
        object.__setattr__(self, "buttons", frozenset(buttons))

    def matches(self, held: set[GamepadButton]) -> bool:
        """Return True if every button in this combo is currently held."""
        return self.buttons.issubset(held)
