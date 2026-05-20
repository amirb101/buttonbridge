"""AppMode abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .action import Action
from .button_combo import ButtonCombo
from .gamepad_button import GamepadButton


class AppMode(ABC):
    """
    A named controller profile that maps buttons to actions.

    Subclass this to add support for a new application.  Only
    ``id``, ``display_name``, ``sf_symbol_name``, and ``button_map``
    are required — ``combo_map`` defaults to empty.

    Example::

        class WordMode(AppMode):
            id           = "word"
            display_name = "Word"
            sf_symbol_name = "doc.text"   # used by the Swift overlay if ported back

            @property
            def button_map(self):
                return {
                    GamepadButton.A: keystroke("s", ["cmd"], id="word-save", name="Save"),
                    ...
                }
    """

    # Stable kebab-case identifier — used for persisting preferences to disk.
    @property
    @abstractmethod
    def id(self) -> str: ...

    # Name shown in the status bar and logs.
    @property
    @abstractmethod
    def display_name(self) -> str: ...

    # SF Symbol name (kept for future parity with any Swift UI layer).
    @property
    @abstractmethod
    def sf_symbol_name(self) -> str: ...

    # Maps individual button presses to actions.
    @property
    @abstractmethod
    def button_map(self) -> dict[GamepadButton, Action]: ...

    # Maps multi-button combos to actions.  Empty by default.
    @property
    def combo_map(self) -> dict[ButtonCombo, Action]:
        return {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id!r}>"
