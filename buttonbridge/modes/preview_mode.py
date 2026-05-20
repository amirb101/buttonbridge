from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class PreviewMode(ConfigurableMode):
    """Active when Preview is frontmost."""

    id = "preview"
    display_name = "Preview"
    sf_symbol_name = "eye"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "next_page": keystroke("right_arrow", id="preview-next", name="Next Page"),
            "prev_page": keystroke("left_arrow", id="preview-prev", name="Previous Page"),
            "zoom_in": keystroke("equal", ["cmd"], id="preview-zoom-in", name="Zoom In"),
            "zoom_out": keystroke("minus", ["cmd"], id="preview-zoom-out", name="Zoom Out"),
            "actual_size": keystroke("0", ["cmd"], id="preview-actual", name="Actual Size"),
            "share": keystroke("s", ["cmd"], id="preview-share", name="Share"),
            "rotate_left": keystroke("l", ["cmd"], id="preview-rotate-l", name="Rotate Left"),
            "rotate_right": keystroke("r", ["cmd"], id="preview-rotate-r", name="Rotate Right"),
        }
        return action_map.get(action_id)
