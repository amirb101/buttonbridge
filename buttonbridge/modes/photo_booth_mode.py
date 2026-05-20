from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class PhotoBoothMode(ConfigurableMode):
    """Active when Photo Booth is frontmost."""

    id = "photo_booth"
    display_name = "Photo Booth"
    sf_symbol_name = "camera"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            # Space triggers the shutter / record button in Photo Booth
            "shutter":         keystroke("space",               id="pb-shutter",   name="Take Photo / Record"),
            "effects":         keystroke("e", ["cmd"],          id="pb-effects",   name="Effects"),
            "flip_photo":      keystroke("f", ["cmd"],          id="pb-flip",      name="Flip Photo"),
            "share":           keystroke("i", ["cmd", "shift"], id="pb-share",     name="Share"),
            "delete":          keystroke("delete",              id="pb-delete",    name="Delete"),
        }
        return action_map.get(action_id)
