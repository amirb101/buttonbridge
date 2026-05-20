from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class VSCodeMode(ConfigurableMode):
    """Active when Visual Studio Code is frontmost."""

    id = "vscode"
    display_name = "VS Code"
    sf_symbol_name = "chevron.left.forwardslash.chevron.right"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "command_palette": keystroke("p", ["cmd", "shift"], id="vscode-cmd", name="Command Palette"),
            "quick_open": keystroke("p", ["cmd"], id="vscode-quick", name="Quick Open"),
            "toggle_terminal": keystroke("grave", ["ctrl"], id="vscode-term", name="Toggle Terminal"),
            "go_definition": keystroke("f12", id="vscode-def", name="Go to Definition"),
            "find": keystroke("f", ["cmd"], id="vscode-find", name="Find"),
            "save": keystroke("s", ["cmd"], id="vscode-save", name="Save"),
            "new_file": keystroke("n", ["cmd"], id="vscode-new", name="New File"),
            "close_tab": keystroke("w", ["cmd"], id="vscode-close", name="Close Tab"),
        }
        return action_map.get(action_id)
