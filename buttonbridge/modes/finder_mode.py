from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class FinderMode(ConfigurableMode):
    """Active when Finder is frontmost."""

    id = "finder"
    display_name = "Finder"
    sf_symbol_name = "folder"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "new_folder": keystroke("n", ["cmd", "shift"], id="finder-new-folder", name="New Folder"),
            "quick_look": keystroke("y", id="finder-quick-look", name="Quick Look"),
            "get_info": keystroke("i", ["cmd"], id="finder-info", name="Get Info"),
            "search": keystroke("f", ["cmd"], id="finder-search", name="Search"),
            "go_back": keystroke("[", ["cmd"], id="finder-back", name="Go Back"),
            "go_forward": keystroke("]", ["cmd"], id="finder-forward", name="Go Forward"),
            "trash": keystroke("delete", ["cmd"], id="finder-trash", name="Move to Trash"),
            "show_hidden": keystroke("period", ["cmd", "shift"], id="finder-hidden", name="Show Hidden Files"),
        }
        return action_map.get(action_id)
