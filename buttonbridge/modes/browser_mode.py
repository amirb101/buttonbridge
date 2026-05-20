from __future__ import annotations

from ..core.action import Action, keystroke
from ..core.configurable_mode import ConfigurableMode


class BrowserMode(ConfigurableMode):
    """
    Active when any web browser is frontmost.

    Covers Chrome, Safari, Firefox, Arc, Edge, Brave, Opera, Vivaldi,
    Orion, Zen Browser, and Comet. All share standard macOS browser
    shortcuts (Cmd+T, Cmd+W, Cmd+[, Cmd+Shift+[, etc.).
    """

    id             = "browser"
    display_name   = "Browser"
    sf_symbol_name = "globe"

    def _create_action_from_id(self, action_id: str) -> Action | None:
        """Create action from ID."""
        action_map = {
            "new_tab": keystroke("t", ["cmd"], id="browser-new-tab", name="New Tab"),
            "reload": keystroke("r", ["cmd"], id="browser-reload", name="Reload Page"),
            "find": keystroke("f", ["cmd"], id="browser-find", name="Find in Page"),
            "go_back": keystroke("left_bracket", ["cmd"], id="browser-go-back", name="Go Back"),
            "close_tab": keystroke("w", ["cmd"], id="browser-close-tab", name="Close Tab"),
            "reopen_tab": keystroke("t", ["cmd", "shift"], id="browser-reopen-tab", name="Reopen Closed Tab"),
            "page_back": keystroke("left_bracket", ["cmd"], id="browser-back", name="Page Back"),
            "page_forward": keystroke("right_bracket", ["cmd"], id="browser-forward", name="Page Forward"),
            "scroll_up": keystroke("page_up", id="browser-scroll-up", name="Scroll Up"),
            "scroll_down": keystroke("page_down", id="browser-scroll-down", name="Scroll Down"),
            "prev_tab": keystroke("left_bracket", ["cmd", "shift"], id="browser-prev-tab", name="Previous Tab"),
            "next_tab": keystroke("right_bracket", ["cmd", "shift"], id="browser-next-tab", name="Next Tab"),
            "new_window": keystroke("n", ["cmd"], id="browser-new-window", name="New Window"),
            "tab_search": keystroke("a", ["cmd", "shift"], id="browser-tab-search", name="Search Tabs"),
            "focus_address": keystroke("l", ["cmd"], id="browser-focus-address-bar", name="Focus Address Bar"),
            "bookmark": keystroke("d", ["cmd"], id="browser-bookmark", name="Bookmark Page"),
        }
        return action_map.get(action_id)
