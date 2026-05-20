"""
SDL / pygame setup for joystick access on macOS.

**rumps + SDL Cocoa video = crash:** SDL's ``Cocoa_RegisterApp`` calls
``[NSApplication sharedApplication]`` and registers the process with HIServices.
The menu bar app already owns NSApplication, so ``pygame.display.set_mode`` on
the main thread aborts on recent macOS (e.g. Tahoe 26.x) with
``_RegisterApplication`` / ``SIGABRT``.

**Menu bar process:** use ``SDL_VIDEODRIVER=dummy`` and never open an SDL
window. Joysticks may still appear if SDL's HIDAPI path works (depends on OS /
SDL build).

**Standalone CLI** (e.g. ``button_logger``): no rumps, so we *may* use a 1×1
hidden window on Darwin to help SDL enumerate devices — still from the main
thread, but only when not sharing the process with AppKit.
"""

from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger(__name__)

_bootstrapped_menu_bar = False
_bootstrapped_standalone = False


def configure_sdl_env(*, embedded_with_rumps: bool) -> None:
    """
    Call before ``import pygame`` the first time in this process.

    Args:
        embedded_with_rumps: ``True`` when rumps owns NSApplication (main app).
    """
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    if sys.platform == "darwin":
        os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")
        os.environ.setdefault("SDL_JOYSTICK_HIDAPI", "1")
        if embedded_with_rumps:
            # Required: SDL must not try to become a second Cocoa GUI app.
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        else:
            if os.environ.get("SDL_VIDEODRIVER") == "dummy":
                del os.environ["SDL_VIDEODRIVER"]
    else:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def bootstrap_pygame_for_menu_bar_app() -> None:
    """
    Run once on the **main thread** from rumps ``on_launch``.

    Does **not** call ``pygame.display.set_mode`` — that crashes when rumps is
    already running an NSApplication.
    """
    global _bootstrapped_menu_bar
    if _bootstrapped_menu_bar:
        return

    configure_sdl_env(embedded_with_rumps=True)

    import pygame

    pygame.init()
    pygame.joystick.init()
    _bootstrapped_menu_bar = True
    logger.info(
        "SDL bootstrap (menu bar, dummy video): pygame reports %d joystick(s)",
        pygame.joystick.get_count(),
    )


def bootstrap_pygame_for_standalone_cli() -> None:
    """
    For ``python -m …`` tools with **no** rumps — safe to use a hidden Cocoa
    window on macOS to improve joystick enumeration.
    """
    global _bootstrapped_standalone
    if _bootstrapped_standalone:
        return

    configure_sdl_env(embedded_with_rumps=False)

    import pygame

    pygame.init()
    if sys.platform == "darwin":
        try:
            flags = getattr(pygame, "HIDDEN", 0)
            pygame.display.set_mode((1, 1), flags)
            logger.info("SDL (standalone CLI): hidden display for joystick enumeration")
        except Exception as e:
            logger.warning("SDL (standalone CLI): hidden display failed (%s)", e)
    pygame.joystick.init()
    _bootstrapped_standalone = True
    logger.info(
        "SDL bootstrap (standalone): pygame reports %d joystick(s)",
        pygame.joystick.get_count(),
    )


# Back-compat alias — menu bar app only
def bootstrap_pygame_joystick() -> None:
    bootstrap_pygame_for_menu_bar_app()
