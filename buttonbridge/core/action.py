"""
Action — the single thing a button press can do.

Actions are plain dataclasses wrapping a callable.  All the complexity of
*how* to do something lives in the executor layer.  Modes just declare
*what* they want using the factory methods at the bottom of this file.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

from ..constants import BundleID, Spotify, Volume

logger = logging.getLogger(__name__)


@dataclass
class Action:
    """
    A single thing the controller can do when a button is pressed.

    Attributes:
        id:           Stable kebab-case identifier (e.g. ``"spotify-next-track"``).
                      Used for serialising custom mappings to disk.
        display_name: Human-readable label shown in the preferences UI.
        shortcut_repr: Human-readable chord for logs (keystroke actions); empty otherwise.
        perform:      Zero-argument callable that carries out the action.
                      Threading is the factory method's responsibility.
    """

    id: str
    display_name: str
    perform: Callable[[], None] = field(repr=False)
    shortcut_repr: str = ""

    def __call__(self) -> None:
        """Convenience: ``action()`` is equivalent to ``action.perform()``."""
        logger.debug("Action fired: %s", self.id)
        self.perform()


# ---------------------------------------------------------------------------
# Factory methods
#
# Import executors inside each factory to avoid circular imports and to keep
# the top-level module light.  The callables are captured in closures so the
# import only happens once at definition time.
# ---------------------------------------------------------------------------

def keystroke(
    key: str,
    modifiers: list[str] | None = None,
    *,
    id: str,
    name: str,
) -> Action:
    """
    Send a keyboard shortcut to the active application.

    Args:
        key:       Key name as a string (e.g. ``"t"``, ``"left_arrow"``).
                   Must match a key defined in ``KeystrokeExecutor.Key``.
        modifiers: List of modifier names (``"cmd"``, ``"shift"``,
                   ``"opt"``, ``"ctrl"``).  Defaults to no modifiers.
        id:        Stable action identifier.
        name:      Display name for the preferences UI.
    """
    from ..executors.keystroke_executor import KeystrokeExecutor

    _modifiers = modifiers or []
    chord = "+".join([*_modifiers, key]) if _modifiers else key

    return Action(
        id=id,
        display_name=name,
        perform=lambda: KeystrokeExecutor.send(key, _modifiers),
        shortcut_repr=chord,
    )


def apple_script(
    source: str,
    *,
    id: str,
    name: str,
) -> Action:
    """
    Run an AppleScript source string (dispatched to a background thread).

    Args:
        source: Valid AppleScript source.
        id:     Stable action identifier.
        name:   Display name.
    """
    from ..executors.applescript_executor import AppleScriptExecutor

    return Action(
        id=id,
        display_name=name,
        perform=lambda: AppleScriptExecutor.run(source),
        shortcut_repr="AppleScript",
    )


def open_app(
    bundle_identifier: str,
    *,
    id: str,
    name: str,
) -> Action:
    """
    Bring an application to the front, launching it if not already running.

    Args:
        bundle_identifier: CFBundleIdentifier of the target app.
        id:                Stable action identifier.
        name:              Display name.
    """
    from AppKit import NSWorkspace  # type: ignore[import]

    def _open() -> None:
        url = NSWorkspace.sharedWorkspace().URLForApplicationWithBundleIdentifier_(
            bundle_identifier
        )
        if url is None:
            logger.error("Cannot find application with bundle ID: %s", bundle_identifier)
            return
        config = NSWorkspace.sharedWorkspace()
        NSWorkspace.sharedWorkspace().openApplicationAtURL_configuration_completionHandler_(
            url, None, None
        )

    return Action(
        id=id,
        display_name=name,
        perform=_open,
        shortcut_repr=f"open_app:{bundle_identifier}",
    )


def adjust_volume(delta: int, *, id: str, name: str) -> Action:
    """
    Raise or lower the system output volume by ``delta`` points (0–100 scale).

    Positive values raise the volume; negative values lower it.
    """
    from ..executors.applescript_executor import AppleScriptExecutor

    script = f"""
        set currentVolume to output volume of (get volume settings)
        set volume output volume (currentVolume + {delta})
    """
    return Action(
        id=id,
        display_name=name,
        perform=lambda: AppleScriptExecutor.run(script),
        shortcut_repr="AppleScript:volume",
    )


def toggle_mute(*, id: str, name: str) -> Action:
    """Toggle the system audio mute state."""
    from ..executors.applescript_executor import AppleScriptExecutor

    script = """
        set isMuted to output muted of (get volume settings)
        set volume output muted (not isMuted)
    """
    return Action(
        id=id,
        display_name=name,
        perform=lambda: AppleScriptExecutor.run(script),
        shortcut_repr="AppleScript:mute",
    )


def screenshot(region: bool, *, id: str, name: str) -> Action:
    """
    Trigger a macOS screenshot.

    Args:
        region: If ``True``, capture a region (Cmd+Shift+4).
                If ``False``, capture full screen (Cmd+Shift+3).
    """
    key = "4" if region else "3"
    return keystroke(key, ["cmd", "shift"], id=id, name=name)


def switch_space(direction: str, *, id: str, name: str) -> Action:
    """
    Switch to the macOS Space (virtual desktop) to the left or right.

    Args:
        direction: ``"left"`` or ``"right"``.
    """
    key = "left_arrow" if direction == "left" else "right_arrow"
    return keystroke(key, ["ctrl"], id=id, name=name)


def unassigned(button_name: str) -> Action:
    """Placeholder for intentionally unassigned buttons."""
    return Action(
        id=f"unassigned-{button_name.lower().replace(' ', '-')}",
        display_name="Unassigned",
        perform=lambda: None,
    )
