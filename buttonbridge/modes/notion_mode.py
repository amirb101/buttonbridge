from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class NotionMode(ConfigurableMode):
    """Active when Notion is frontmost."""

    id = "notion"
    display_name = "Notion"
    sf_symbol_name = "square.grid.2x2"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "quick_find": keystroke("k", ["cmd"], id="notion-quick-find", name="Quick Find"),
            "new_page": keystroke("n", ["cmd"], id="notion-new-page", name="New Page"),
            "toggle_todo": keystroke("return", ["cmd"], id="notion-todo", name="Toggle Todo"),
            "slash_command": keystroke("slash", id="notion-slash", name="Slash Command"),
            "back": keystroke("left_bracket", ["cmd"], id="notion-back", name="Go Back"),
            "forward": keystroke("right_bracket", ["cmd"], id="notion-forward", name="Go Forward"),
            "command_palette": keystroke("p", ["cmd", "shift"], id="notion-cmd", name="Command Palette"),
            "duplicate": keystroke("d", ["cmd"], id="notion-duplicate", name="Duplicate"),
        }
        return action_map.get(action_id)
