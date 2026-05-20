"""
MenuBarController — rumps-based status bar app.

The status item icon shows whether the controller is connected.
Clicking it opens a menu with the current mode, connection state,
launch-at-login toggle, and Quit.

The mode-change overlay is implemented here as a brief title flash:
the status item label switches to the mode name for ``Overlay.HOLD_SECONDS``
then clears back to just the icon.  Simple, zero extra dependencies.
"""

from __future__ import annotations

import logging
import shlex
import subprocess
import sys

import rumps  # type: ignore[import]

from ..constants import Overlay
from ..core.app_mode import AppMode

logger = logging.getLogger(__name__)

# Status item icons (text fallbacks if SF Symbols aren't available in rumps)
_ICON_CONNECTED    = "🎮"
_ICON_DISCONNECTED = "🎮"   # same for now — swap for a dimmed icon if desired


class MenuBarApp(rumps.App):
    """
    The rumps application object.  Owns the AppKit run loop.

    All other components are started from ``application_did_finish_launching``
    (called automatically by rumps) and communicate back via callbacks set in
    ``main.py``.
    """

    def __init__(self, on_launch: "Callable[[], None]") -> None:  # noqa: F821
        logger.info("MenuBarApp.__init__ starting")
        super().__init__(
            name="ButtonBridge",
            title=_ICON_DISCONNECTED,
            quit_button=None,   # we add our own quit item below
        )
        self._on_launch    = on_launch
        self._current_mode = "—"
        self._is_connected = False
        self._overlay_timer: rumps.Timer | None = None
        self._launch_called = False

        self._rebuild_menu()
        # Fallback: if application_did_finish_launching never fires (rumps bug),
        # force-start after 2s. Cancelled if real launch happens first.
        self._fallback_timer = rumps.Timer(self._fallback_start, 2.0)
        self._fallback_timer.start()
        logger.info("MenuBarApp.__init__ complete (fallback timer armed)")

    def _fallback_start(self, _timer) -> None:
        """Emergency start if rumps never calls application_did_finish_launching."""
        if not self._launch_called:
            logger.warning("MenuBarApp: FALLBACK START — application_did_finish_launching never fired!")
            self._start_controller()

    # ------------------------------------------------------------------
    # Public updates (called from other threads — must dispatch to main thread)
    # ------------------------------------------------------------------

    def _dispatch_main(self, fn, *args):
        """Dispatch a function to the main thread."""
        from Foundation import NSOperationQueue

        def operation():
            fn(*args)

        NSOperationQueue.mainQueue().addOperationWithBlock_(operation)

    def update_mode(self, mode: AppMode) -> None:
        """Reflect a mode change in the status bar and flash the mode name."""
        # Must dispatch to main thread for UI updates
        def _update():
            self._current_mode = mode.display_name
            self._rebuild_menu()
            self._flash_overlay(mode)

        self._dispatch_main(_update)

    def update_connection(self, is_connected: bool) -> None:
        """Reflect the controller connection state."""
        def _update():
            self._is_connected = is_connected
            self._update_title()
            self._rebuild_menu()

        self._dispatch_main(_update)

    def _update_title(self) -> None:
        """Update title based on connection state (respects calibration overlay)."""
        if getattr(self, "_calibration_prompt", None):
            self.title = f"🎮 {self._calibration_prompt}"
        else:
            self.title = _ICON_CONNECTED if self._is_connected else _ICON_DISCONNECTED

    def show_calibration_prompt(self, button_name: str) -> None:
        """Show calibration prompt in menu bar title."""
        def _update():
            self._calibration_prompt = f"Press: {button_name}"
            self._update_title()

        self._dispatch_main(_update)

    def clear_calibration_prompt(self) -> None:
        """Clear calibration prompt from menu bar title."""
        def _update():
            self._calibration_prompt = None
            self._update_title()

        self._dispatch_main(_update)

    # ------------------------------------------------------------------
    # rumps lifecycle
    # ------------------------------------------------------------------

    def application_did_finish_launching(self, notification) -> None:
        """Called by rumps after the AppKit run loop starts."""
        logger.info("MenuBarApp: application_did_finish_launching — starting controller")
        self._start_controller()

    def _start_controller(self) -> None:
        """Initialize controller and detector — called from launch or fallback timer."""
        if getattr(self, "_launch_called", False):
            return
        self._launch_called = True
        # Cancel fallback timer if real launch happened
        try:
            if hasattr(self, "_fallback_timer") and self._fallback_timer:
                self._fallback_timer.stop()
        except Exception:
            pass

        # GameController defaults to ignoring pads while this process is not key;
        # menu bar remotes must opt in or the controller appears "dead" in other apps.
        try:
            from GameController import GCController

            GCController.setShouldMonitorBackgroundEvents_(True)
            logger.info("GameController: shouldMonitorBackgroundEvents enabled")
        except Exception as e:
            logger.debug("GameController shouldMonitorBackgroundEvents: %s", e)

        try:
            self._on_launch()
        except Exception as e:
            logger.exception("MenuBarApp: _on_launch failed: %s", e)

    # ------------------------------------------------------------------
    # Private: overlay flash
    # ------------------------------------------------------------------

    def _flash_overlay(self, mode: AppMode) -> None:
        """
        Briefly show the mode name in the status bar title, then reset.

        This is the simplest possible mode-change indicator that requires
        zero extra dependencies and no Accessibility permissions.
        """
        # Cancel any in-flight reset timer
        if self._overlay_timer:
            self._overlay_timer.stop()

        self.title = f"{mode.display_name}"

        self._overlay_timer = rumps.Timer(self._reset_title, Overlay.HOLD_SECONDS)
        self._overlay_timer.start()

    def _reset_title(self, _timer) -> None:
        self.title = _ICON_CONNECTED if self._is_connected else _ICON_DISCONNECTED
        if self._overlay_timer:
            self._overlay_timer.stop()
            self._overlay_timer = None

    # ------------------------------------------------------------------
    # Private: menu
    # ------------------------------------------------------------------

    def _rebuild_menu(self) -> None:
        connection_label = (
            "Controller: Connected ✓" if self._is_connected
            else "Controller: Not Connected"
        )

        self.menu.clear()
        self.menu = [
            rumps.MenuItem("ButtonBridge", callback=None),
            None,
            rumps.MenuItem(f"Mode: {self._current_mode}", callback=None),
            rumps.MenuItem(connection_label, callback=None),
            None,
            rumps.MenuItem(
                "Calibrate Controller…",
                callback=self._calibrate_controller,
            ),
            rumps.MenuItem(
                "Hotkey List…",
                callback=self._open_hotkey_list,
            ),
            None,
            rumps.MenuItem(
                "Open Accessibility Settings…",
                callback=self._open_accessibility_settings,
            ),
            None,
            rumps.MenuItem("Quit", callback=rumps.quit_application),
        ]

    def _calibrate_controller(self, _) -> None:
        """Start controller calibration wizard (clears any existing mapping first)."""
        from ..main import controller
        from ..controller.apple_gc_input import AppleGCControllerInput

        if controller and isinstance(controller, AppleGCControllerInput):
            # Clear any existing calibration first
            controller.clear_calibration()

            def on_done():
                rumps.notification(
                    "ButtonBridge",
                    "Calibration Complete",
                    "Controller mapping saved!",
                )
            if controller.start_calibration(on_done):
                logger.info("Calibration started (previous mapping cleared)")
            else:
                rumps.alert(
                    title="No Controller",
                    message="Please connect a controller first.",
                    ok="OK",
                )
        else:
            rumps.alert(
                title="Calibration Not Available",
                message="Calibration is only available for GameController backend.",
                ok="OK",
            )

    def _open_accessibility_settings(self, _) -> None:
        """System Settings → Privacy & Security → Accessibility (for simulated keystrokes)."""
        subprocess.run(
            [
                "open",
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
            ],
            check=False,
        )

    def _open_hotkey_list(self, _) -> None:
        """Print the hotkey list to terminal in a readable format."""
        try:
            from ..config.keybind_config import format_hotkey_list_text

            text = format_hotkey_list_text()
            if sys.stdout.isatty():
                logger.info("\n%s", text)
            else:
                # Finder-launched .app has no attached TTY; open Terminal to display output.
                if getattr(sys, "frozen", False):
                    cmd = f"{shlex.quote(sys.executable)} --print-hotkeys"
                else:
                    cmd = f"{shlex.quote(sys.executable)} -m buttonbridge --print-hotkeys"
                apple_script = (
                    'tell application "Terminal" to activate\n'
                    f'tell application "Terminal" to do script "{cmd}"\n'
                )
                subprocess.run(["osascript", "-e", apple_script], check=False)
            rumps.notification(
                "ButtonBridge",
                "Hotkey list printed",
                "Check Terminal for the hotkey list output.",
            )
        except Exception as e:
            logger.exception("Failed to print hotkey list: %s", e)
            rumps.alert(
                title="Hotkey List Error",
                message=str(e),
                ok="OK",
            )
