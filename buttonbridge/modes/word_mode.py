from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class WordMode(ConfigurableMode):
    """Active when Microsoft Word is frontmost."""

    id = "word"
    display_name = "Word"
    sf_symbol_name = "doc.text"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "save":            keystroke("s", ["cmd"],          id="word-save",      name="Save"),
            "find":            keystroke("f", ["cmd"],          id="word-find",      name="Find"),
            "bold":            keystroke("b", ["cmd"],          id="word-bold",      name="Bold"),
            "italic":          keystroke("i", ["cmd"],          id="word-italic",    name="Italic"),
            "undo":            keystroke("z", ["cmd"],          id="word-undo",      name="Undo"),
            "redo":            keystroke("z", ["cmd", "shift"], id="word-redo",      name="Redo"),
            "page_up":         keystroke("pageup",              id="word-pgup",      name="Page Up"),
            "page_down":       keystroke("pagedown",            id="word-pgdn",      name="Page Down"),
            "zoom_in":         keystroke("=", ["cmd"],          id="word-zoomin",    name="Zoom In"),
            "zoom_out":        keystroke("-", ["cmd"],          id="word-zoomout",   name="Zoom Out"),
            "word_count":      keystroke("g", ["cmd", "shift"], id="word-wc",        name="Word Count"),
            "new_document":    keystroke("n", ["cmd"],          id="word-new",       name="New Document"),
        }
        return action_map.get(action_id)
