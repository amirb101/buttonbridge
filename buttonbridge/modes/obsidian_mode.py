from __future__ import annotations

from ..core.action import Action, keystroke, open_app
from ..core.configurable_mode import ConfigurableMode
from ..constants import BundleID


class ObsidianMode(ConfigurableMode):
    """
    Active when Obsidian is the frontmost application.

    Fires custom hotkeys that you configure in Obsidian's Settings → Hotkeys.
    The README contains the exact setup table.

    Buttons are configurable via Edit Keybindings.
    """

    id             = "obsidian"
    display_name   = "Obsidian"
    sf_symbol_name = "note.text"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        """Create action from ID."""
        action_map = {
            "command_palette": keystroke(
                "p", ["cmd"],
                id="obsidian-command-palette",
                name="Command Palette",
            ),
            "quick_switcher": keystroke(
                "o", ["cmd"],
                id="obsidian-quick-switcher",
                name="Quick Switcher",
            ),
            "daily_note": keystroke(
                "d", ["ctrl", "shift"],
                id="obsidian-daily-note",
                name="Today's Daily Note",
            ),
            "toggle_checklist": keystroke(
                "c", ["ctrl", "shift"],
                id="obsidian-toggle-checklist",
                name="Toggle Checklist",
            ),
            "navigate_back": keystroke(
                "left_arrow", ["cmd", "opt"],
                id="obsidian-navigate-back",
                name="Navigate Back",
            ),
            "navigate_forward": keystroke(
                "right_arrow", ["cmd", "opt"],
                id="obsidian-navigate-forward",
                name="Navigate Forward",
            ),
            "toggle_sidebar": keystroke(
                "backslash", ["cmd"],
                id="obsidian-toggle-sidebar",
                name="Toggle Left Sidebar",
            ),
            "search_all": keystroke(
                "f", ["cmd", "shift"],
                id="obsidian-search-all",
                name="Search All Files",
            ),
            "insert_template": keystroke(
                "t", ["ctrl", "shift"],
                id="obsidian-insert-template",
                name="Insert Template",
            ),
            "graph_view": keystroke(
                "g", ["ctrl", "shift"],
                id="obsidian-graph-view",
                name="Graph View",
            ),
            "new_note": keystroke(
                "n", ["cmd"],
                id="obsidian-new-note",
                name="New Note",
            ),
            "search": keystroke(
                "f", ["cmd"],
                id="obsidian-search",
                name="Search Current File",
            ),
            "toggle_preview": keystroke(
                "e", ["cmd"],
                id="obsidian-toggle-preview",
                name="Toggle Preview",
            ),
            "insert_link": keystroke(
                "k", ["cmd"],
                id="obsidian-insert-link",
                name="Insert Link",
            ),
        }
        return action_map.get(action_id)
