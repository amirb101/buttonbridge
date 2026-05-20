from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class ClaudeDesktopMode(ConfigurableMode):
    """Active when the Anthropic Claude desktop app is frontmost."""

    id = "claude"
    display_name = "Claude"
    sf_symbol_name = "sparkles"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "new_chat":        keystroke("n", ["cmd"],          id="claude-new",     name="New Chat"),
            "send":            keystroke("return",              id="claude-send",    name="Send Message"),
            "new_line":        keystroke("return", ["shift"],   id="claude-newline", name="New Line"),
            "search_chats":    keystroke("k", ["cmd"],          id="claude-search",  name="Search Chats"),
            "settings":        keystroke("comma", ["cmd"],     id="claude-settings", name="Settings"),
            "stop":            keystroke("escape",              id="claude-stop",    name="Stop"),
            "close":           keystroke("w", ["cmd"],          id="claude-close",   name="Close Chat"),
        }
        return action_map.get(action_id)
