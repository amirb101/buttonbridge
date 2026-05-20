from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class ChatGPTMode(ConfigurableMode):
    """Active when the ChatGPT desktop app is frontmost."""

    id = "chatgpt"
    display_name = "ChatGPT"
    sf_symbol_name = "bubble.left.and.bubble.right"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "new_chat":        keystroke("n", ["cmd"],          id="gpt-new",      name="New Chat"),
            "send":            keystroke("return",              id="gpt-send",     name="Send Message"),
            "new_line":        keystroke("return", ["shift"],   id="gpt-newline",  name="New Line"),
            "search_chats":    keystroke("k", ["cmd"],          id="gpt-search",   name="Search Chats"),
            "copy_last":       keystroke("c", ["cmd", "shift"], id="gpt-copy",     name="Copy Last Response"),
            "stop":            keystroke(".", ["cmd"],          id="gpt-stop",     name="Stop Generating"),
            "close":           keystroke("w", ["cmd"],          id="gpt-close",    name="Close Chat"),
        }
        return action_map.get(action_id)
