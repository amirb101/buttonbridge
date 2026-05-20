from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class AppleMusicMode(ConfigurableMode):
    """Active when Apple Music is frontmost."""

    id = "apple_music"
    display_name = "Apple Music"
    sf_symbol_name = "music.note"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        action_map = {
            "play_pause": keystroke("space", id="music-play-pause", name="Play/Pause"),
            "next_track": keystroke("right_arrow", ["cmd"], id="music-next", name="Next Track"),
            "prev_track": keystroke("left_arrow", ["cmd"], id="music-prev", name="Previous Track"),
            "volume_up": keystroke("up_arrow", id="music-vol-up", name="Volume Up"),
            "volume_down": keystroke("down_arrow", id="music-vol-down", name="Volume Down"),
            "love": keystroke("l", id="music-love", name="Love Track"),
            "shuffle": keystroke("s", ["cmd"], id="music-shuffle", name="Toggle Shuffle"),
            "search": keystroke("f", ["cmd"], id="music-search", name="Search"),
        }
        return action_map.get(action_id)
