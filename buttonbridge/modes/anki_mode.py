from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class AnkiMode(ConfigurableMode):
    """Active when Anki is frontmost."""

    id = "anki"
    display_name = "Anki"
    sf_symbol_name = "rectangle.stack.badge.play"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "show_answer": keystroke("space", id="anki-show-answer", name="Show Answer"),
            "again": keystroke("1", id="anki-again", name="Again"),
            "hard": keystroke("2", id="anki-hard", name="Hard"),
            "good": keystroke("3", id="anki-good", name="Good"),
            "easy": keystroke("4", id="anki-easy", name="Easy"),
            "undo": keystroke("z", ["cmd"], id="anki-undo", name="Undo"),
            "bury": keystroke("minus", id="anki-bury", name="Bury"),
            # Anki suspend uses "=" on macOS; "@" is not a valid key token in KeystrokeExecutor.
            "suspend": keystroke("equal", id="anki-suspend", name="Suspend"),
        }
        return action_map.get(action_id)
