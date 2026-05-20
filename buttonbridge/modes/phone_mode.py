from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class PhoneMode(ConfigurableMode):
    """Active when Phone app is frontmost (for Continuity calls)."""

    id = "phone"
    display_name = "Phone"
    sf_symbol_name = "phone.fill"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "answer_call": keystroke("return", id="phone-answer", name="Answer Call"),
            "decline_call": keystroke("d", id="phone-decline", name="Decline Call"),
            "end_call": keystroke("escape", id="phone-end", name="End Call"),
            "mute_toggle": keystroke("m", id="phone-mute", name="Toggle Mute"),
            "keypad": keystroke("k", id="phone-keypad", name="Show Keypad"),
            "contacts": keystroke("l", id="phone-contacts", name="Show Contacts"),
            "recents": keystroke("r", id="phone-recents", name="Show Recents"),
            "voicemail": keystroke("v", id="phone-voicemail", name="Show Voicemail"),
        }
        return action_map.get(action_id)
