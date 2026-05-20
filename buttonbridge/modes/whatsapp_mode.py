from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class WhatsAppMode(ConfigurableMode):
    """Active when WhatsApp is frontmost."""

    id = "whatsapp"
    display_name = "WhatsApp"
    sf_symbol_name = "bubble.left.fill"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "new_chat": keystroke("n", ["cmd"], id="wa-new", name="New Chat"),
            "send": keystroke("return", id="wa-send", name="Send"),
            "search": keystroke("f", ["cmd"], id="wa-search", name="Search"),
            "search_in_chat": keystroke("f", ["cmd", "shift"], id="wa-search-chat", name="Search in Chat"),
            "archive_chat": keystroke("e", ["cmd", "shift"], id="wa-archive", name="Archive Chat"),
            "mute_chat": keystroke("m", ["cmd", "shift"], id="wa-mute", name="Mute Chat"),
        }
        return action_map.get(action_id)
