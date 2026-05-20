"""Main entry point for ButtonBridge."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Callable

from .constants import BundleID
from .controller.apple_gc_input import AppleGCControllerInput
from .controller.controller_manager import ControllerManager
from .core.mode_registry import ModeRegistry
from .detection.app_detector import AppDetector
from .modes.apple_music_mode import AppleMusicMode
from .modes.anki_mode import AnkiMode
from .modes.browser_mode import BrowserMode
from .modes.chatgpt_mode import ChatGPTMode
from .modes.claude_desktop_mode import ClaudeDesktopMode
from .modes.cursor_mode import CursorMode
from .modes.facetime_mode import FaceTimeMode
from .modes.finder_mode import FinderMode
from .modes.global_mode import GlobalMode
from .modes.messages_mode import MessagesMode
from .modes.notes_mode import NotesMode
from .modes.notion_mode import NotionMode
from .modes.obsidian_mode import ObsidianMode
from .modes.outlook_mode import OutlookMode
from .modes.phone_mode import PhoneMode
from .modes.photo_booth_mode import PhotoBoothMode
from .modes.preview_mode import PreviewMode
from .modes.spotify_mode import SpotifyMode
from .modes.vscode_mode import VSCodeMode
from .modes.whatsapp_mode import WhatsAppMode
from .modes.word_mode import WordMode
from .core.app_mode import AppMode
from .routing.action_router import ActionRouter
from .ui.menu_bar import MenuBarApp

# Global references for cross-module access
controller: Any = None
app: Any = None

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    """Configure logging for the application."""
    verbose = (
        "--verbose" in sys.argv
        or "-v" in sys.argv
        or os.environ.get("BUTTONBRIDGE_VERBOSE", "").strip().lower() in ("1", "true", "yes")
    )
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
    logging.getLogger("pygame").setLevel(logging.WARNING)


def _check_accessibility() -> bool:
    """Check if the app has accessibility permissions."""
    try:
        from ApplicationServices import AXIsProcessTrusted
        trusted = AXIsProcessTrusted()
        if not trusted:
            logger.warning("Accessibility permissions not granted")
        return trusted
    except Exception as e:
        logger.error("Failed to check accessibility: %s", e)
        return False


def _build_registry() -> ModeRegistry:
    """
    Populate the mode registry.

    To add support for a new app:
    1. Create a new AppMode subclass in modes/
    2. Import it here
    3. Add register() call with the app's bundle ID(s)
    """
    registry = ModeRegistry(fallback=GlobalMode())

    # Media
    registry.register(SpotifyMode(), bundle_ids=[BundleID.SPOTIFY])
    registry.register(AppleMusicMode(), bundle_ids=[BundleID.APPLE_MUSIC])

    # Browsers
    registry.register(BrowserMode(), bundle_ids=BundleID.ALL_BROWSERS)

    # Productivity
    registry.register(AnkiMode(), bundle_ids=BundleID.ALL_ANKI_BUNDLE_IDS)
    registry.register(NotesMode(), bundle_ids=[BundleID.NOTES])
    registry.register(ObsidianMode(), bundle_ids=[BundleID.OBSIDIAN])
    registry.register(NotionMode(), bundle_ids=[BundleID.NOTION])
    registry.register(OutlookMode(), bundle_ids=[BundleID.OUTLOOK])
    registry.register(WordMode(), bundle_ids=[BundleID.WORD])
    registry.register(PhotoBoothMode(), bundle_ids=[BundleID.PHOTO_BOOTH])
    registry.register(ChatGPTMode(), bundle_ids=[BundleID.CHATGPT])
    registry.register(ClaudeDesktopMode(), bundle_ids=[BundleID.CLAUDE_DESKTOP])

    # System apps
    registry.register(FinderMode(), bundle_ids=[BundleID.FINDER])
    registry.register(PreviewMode(), bundle_ids=[BundleID.PREVIEW])

    # Development
    registry.register(VSCodeMode(), bundle_ids=[BundleID.VS_CODE])
    registry.register(CursorMode(), bundle_ids=[BundleID.CURSOR])

    # Communication
    registry.register(MessagesMode(), bundle_ids=[BundleID.MESSAGES])
    registry.register(WhatsAppMode(), bundle_ids=[BundleID.WHATSAPP])
    registry.register(FaceTimeMode(), bundle_ids=[BundleID.FACETIME])
    registry.register(PhoneMode(), bundle_ids=[BundleID.PHONE])

    return registry


def _pick_input_backend() -> str:
    """
    Select input backend.

    - Set BUTTONBRIDGE_INPUT_BACKEND=gc to use Apple's GameController API
    - Set BUTTONBRIDGE_INPUT_BACKEND=pygame to force SDL/pygame
    """
    raw = os.environ.get("BUTTONBRIDGE_INPUT_BACKEND", "pygame").strip().lower()
    if raw in ("gc", "gamecontroller", "apple"):
        return "gc"
    return "pygame"


def _make_controller(
    router: ActionRouter,
    on_connection_changed: Callable[[bool], None] | None = None,
) -> Any:
    """Create and configure the controller manager."""
    backend = _pick_input_backend()
    if backend == "gc":
        logger.info("Input backend: Apple GameController (BUTTONBRIDGE_INPUT_BACKEND=gc)")
        return AppleGCControllerInput(
            on_button_change=router.button_changed,
            on_connection_changed=on_connection_changed,
        )

    logger.info("Input backend: pygame/SDL (BUTTONBRIDGE_INPUT_BACKEND=pygame)")
    return ControllerManager(
        on_button_change=router.button_changed,
        on_connection_changed=on_connection_changed,
    )


def main() -> None:
    """Run the application."""
    global controller, app

    _setup_logging()
    _check_accessibility()

    # Build mode registry
    registry = _build_registry()

    # Menu bar is created below; callbacks use this ref so router/controller can update UI.
    menu_bar_ref: list[Any] = [None]

    def on_mode_changed(mode: AppMode) -> None:
        mb = menu_bar_ref[0]
        if mb is not None:
            mb.update_mode(mode)

    def on_connection_changed(connected: bool) -> None:
        mb = menu_bar_ref[0]
        if mb is not None:
            mb.update_connection(connected)

    # Create action router (notifies menu when foreground app → mode changes)
    router = ActionRouter(registry=registry, on_mode_changed=on_mode_changed)

    # Create controller manager
    controller = _make_controller(router, on_connection_changed=on_connection_changed)

    # Create app detector
    detector = AppDetector(on_app_change=router.update_mode)

    def on_launch() -> None:
        """Called when menu bar app launches."""
        logger.info("Starting controller and detector...")
        controller.start()
        detector.start()

    # Create and run menu bar app
    logger.info("Creating MenuBarApp...")
    app = MenuBarApp(on_launch=on_launch)
    menu_bar_ref[0] = app

    # Store references for external access (e.g., calibration)
    logger.info("Starting main loop...")
    app.run()


if __name__ == "__main__":
    main()
