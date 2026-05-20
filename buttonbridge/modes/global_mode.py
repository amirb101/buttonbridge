from __future__ import annotations

from ..constants import BundleID, Volume
from ..core.action import (
    Action,
    adjust_volume,
    apple_script,
    keystroke,
    open_app,
    screenshot,
    switch_space,
    toggle_mute,
)
from ..core.configurable_mode import ConfigurableMode
from ..executors.applescript_executor import AppleScriptExecutor


class GlobalMode(ConfigurableMode):
    """
    Fallback mode — active whenever no specific app is matched.

    Provides universally useful controls: music playback, volume,
    system navigation, and quick app launchers.

    Buttons are configurable via Edit Keybindings.
    """

    id             = "global"
    display_name   = "Global"
    sf_symbol_name = "gamecontroller"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        """Create action from ID."""
        action_map = {
            "play_pause": apple_script(
                AppleScriptExecutor.Spotify.PLAYPAUSE,
                id="global-play-pause",
                name="Play / Pause",
            ),
            "next_track": apple_script(
                AppleScriptExecutor.Spotify.NEXT_TRACK,
                id="global-next-track",
                name="Next Track",
            ),
            "prev_track": apple_script(
                AppleScriptExecutor.Spotify.PREVIOUS_TRACK,
                id="global-previous-track",
                name="Previous Track",
            ),
            "volume_up": adjust_volume(
                Volume.STEP_SIZE,
                id="global-volume-up",
                name="Volume Up",
            ),
            "volume_down": adjust_volume(
                -Volume.STEP_SIZE,
                id="global-volume-down",
                name="Volume Down",
            ),
            "mute": toggle_mute(
                id="global-toggle-mute",
                name="Toggle Mute",
            ),
            "screenshot": screenshot(
                region=True,
                id="global-screenshot-region",
                name="Screenshot (Region)",
            ),
            "screenshot_full": screenshot(
                region=False,
                id="global-screenshot-full",
                name="Screenshot (Full Screen)",
            ),
            "mission_control": keystroke(
                "up_arrow", ["ctrl"],
                id="global-mission-control",
                name="Mission Control",
            ),
            "spotlight": keystroke(
                "space", ["cmd"],
                id="global-spotlight",
                name="Open Spotlight",
            ),
            "lock_screen": keystroke(
                "q", ["cmd", "ctrl"],
                id="global-lock-screen",
                name="Lock Screen",
            ),
            "open_obsidian": open_app(
                BundleID.OBSIDIAN,
                id="global-open-obsidian",
                name="Open Obsidian",
            ),
            "open_spotify": open_app(
                BundleID.SPOTIFY,
                id="global-open-spotify",
                name="Open Spotify",
            ),
            "space_left": switch_space(
                "left",
                id="global-space-left",
                name="Switch Space Left",
            ),
            "space_right": switch_space(
                "right",
                id="global-space-right",
                name="Switch Space Right",
            ),
        }
        return action_map.get(action_id)
