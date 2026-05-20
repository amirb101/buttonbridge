from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class SpotifyMode(ConfigurableMode):
    """
    Active when Spotify is frontmost.

    Controls playback, navigation, and library management.
    """

    id = "spotify"
    display_name = "Spotify"
    sf_symbol_name = "play.circle"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        """Create action from ID."""
        action_map = {
            "play_pause": keystroke("space", id="spotify-play-pause", name="Play/Pause"),
            "next_track": keystroke("right_arrow", ["cmd"], id="spotify-next", name="Next Track"),
            "prev_track": keystroke("left_arrow", ["cmd"], id="spotify-prev", name="Previous Track"),
            "volume_up": keystroke("up_arrow", ["cmd"], id="spotify-vol-up", name="Volume Up"),
            "volume_down": keystroke("down_arrow", ["cmd"], id="spotify-vol-down", name="Volume Down"),
            "shuffle": keystroke("s", id="spotify-shuffle", name="Toggle Shuffle"),
            "repeat": keystroke("r", id="spotify-repeat", name="Toggle Repeat"),
            "like": keystroke("s", ["cmd"], id="spotify-like", name="Like/Unlike"),
            "search": keystroke("f", ["cmd"], id="spotify-search", name="Search"),
        }
        return action_map.get(action_id)
