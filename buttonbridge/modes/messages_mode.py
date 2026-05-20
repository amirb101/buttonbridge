from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class MessagesMode(ConfigurableMode):
    """Active when Messages is frontmost."""

    id = "messages"
    display_name = "Messages"
    sf_symbol_name = "message.fill"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "new_message": keystroke("n", ["cmd"], id="msg-new", name="New Message"),
            "send_message": keystroke("return", id="msg-send", name="Send"),
            "next_conversation": keystroke("right_bracket", ["cmd"], id="msg-next", name="Next Chat"),
            "prev_conversation": keystroke("left_bracket", ["cmd"], id="msg-prev", name="Previous Chat"),
            "search": keystroke("f", ["cmd"], id="msg-search", name="Search"),
            "details": keystroke("i", ["cmd"], id="msg-details", name="Chat Info"),
        }
        return action_map.get(action_id)
