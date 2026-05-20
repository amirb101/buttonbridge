from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class CursorMode(ConfigurableMode):
    """Active when Cursor is frontmost (same shortcuts as VS Code by default)."""

    id = "cursor"
    display_name = "Cursor"
    sf_symbol_name = "cursorarrow.rays"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "command_palette": keystroke("p", ["cmd", "shift"], id="cursor-cmd", name="Command Palette"),
            "quick_open": keystroke("p", ["cmd"], id="cursor-quick", name="Quick Open"),
            "toggle_terminal": keystroke("grave", ["ctrl"], id="cursor-term", name="Toggle Terminal"),
            "go_definition": keystroke("f12", id="cursor-def", name="Go to Definition"),
            "find": keystroke("f", ["cmd"], id="cursor-find", name="Find"),
            "save": keystroke("s", ["cmd"], id="cursor-save", name="Save"),
            "new_file": keystroke("n", ["cmd"], id="cursor-new", name="New File"),
            "close_tab": keystroke("w", ["cmd"], id="cursor-close", name="Close Tab"),
        }
        return action_map.get(action_id)
