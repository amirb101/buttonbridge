from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class FaceTimeMode(ConfigurableMode):
    """Active when FaceTime is frontmost."""

    id = "facetime"
    display_name = "FaceTime"
    sf_symbol_name = "video.fill"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "answer_call": keystroke("return", id="ft-answer", name="Answer Call"),
            "decline_call": keystroke("d", id="ft-decline", name="Decline Call"),
            "end_call": keystroke("escape", id="ft-end", name="End Call"),
            "mute_toggle": keystroke("m", id="ft-mute", name="Toggle Mute"),
            "camera_toggle": keystroke("v", id="ft-camera", name="Toggle Camera"),
            "flip_camera": keystroke("c", id="ft-flip", name="Flip Camera"),
            "effects": keystroke("e", id="ft-effects", name="Video Effects"),
            "full_screen": keystroke("f", id="ft-fullscreen", name="Full Screen"),
        }
        return action_map.get(action_id)
