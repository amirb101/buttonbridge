from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class NotesMode(ConfigurableMode):
    """Active when Apple Notes is frontmost."""

    id = "notes"
    display_name = "Notes"
    sf_symbol_name = "note.text"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "new_note":        keystroke("n", ["cmd"],          id="notes-new",      name="New Note"),
            "new_folder":      keystroke("n", ["cmd", "shift"], id="notes-folder",   name="New Folder"),
            "search":          keystroke("f", ["cmd"],          id="notes-search",   name="Search"),
            "delete":          keystroke("delete", ["cmd"],     id="notes-delete",   name="Delete Note"),
            "bold":            keystroke("b", ["cmd"],          id="notes-bold",     name="Bold"),
            "italic":          keystroke("i", ["cmd"],          id="notes-italic",   name="Italic"),
            "checklist":       keystroke("l", ["cmd", "shift"], id="notes-check",    name="Toggle Checklist"),
            "back":            keystroke("[", ["cmd"],          id="notes-back",     name="Navigate Back"),
        }
        return action_map.get(action_id)
