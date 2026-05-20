from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class OutlookMode(ConfigurableMode):
    """Active when Microsoft Outlook is frontmost."""

    id = "outlook"
    display_name = "Outlook"
    sf_symbol_name = "envelope"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "new_email":       keystroke("n", ["cmd"],          id="outlook-new",    name="New Email"),
            "reply":           keystroke("r", ["cmd"],          id="outlook-reply",  name="Reply"),
            "reply_all":       keystroke("r", ["cmd", "shift"], id="outlook-replyall", name="Reply All"),
            "forward":         keystroke("j", ["cmd"],          id="outlook-fwd",    name="Forward"),
            "send":            keystroke("return", ["cmd"],     id="outlook-send",   name="Send"),
            "delete":          keystroke("delete",              id="outlook-del",    name="Delete"),
            "search":          keystroke("e", ["cmd"],          id="outlook-search", name="Search"),
            "next_message":    keystroke("]", ["cmd"],          id="outlook-next",   name="Next Message"),
            "prev_message":    keystroke("[", ["cmd"],          id="outlook-prev",   name="Previous Message"),
            "mark_read":       keystroke("t", ["cmd"],          id="outlook-read",   name="Mark as Read"),
        }
        return action_map.get(action_id)
