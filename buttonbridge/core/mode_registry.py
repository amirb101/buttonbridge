"""ModeRegistry — maps bundle IDs to AppMode instances."""

from __future__ import annotations

import logging

from .app_mode import AppMode

logger = logging.getLogger(__name__)


class ModeRegistry:
    """
    Associates bundle identifiers with ``AppMode`` instances and resolves
    the active mode for any given frontmost application.

    Usage (in ``main.py``)::

        registry = ModeRegistry(fallback=GlobalMode())
        registry.register(SpotifyMode(), bundle_ids=[BundleID.SPOTIFY])
        registry.register(BrowserMode(), bundle_ids=BundleID.CHROMIUM_BROWSERS)
        registry.register(ObsidianMode(), bundle_ids=[BundleID.OBSIDIAN])

    Adding a new mode requires only a new ``register()`` call here — nothing
    else in the codebase changes.
    """

    def __init__(self, fallback: AppMode) -> None:
        """
        Args:
            fallback: The mode to use when no bundle ID matches.
                      Typically ``GlobalMode()``.
        """
        self._fallback = fallback
        self._bundle_to_mode: dict[str, AppMode] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, mode: AppMode, bundle_ids: list[str]) -> None:
        """
        Register an ``AppMode`` for one or more bundle identifiers.

        Args:
            mode:       The mode to activate when any of the given apps
                        comes to the front.
            bundle_ids: One or more ``CFBundleIdentifier`` strings.
        """
        for bundle_id in bundle_ids:
            if bundle_id in self._bundle_to_mode:
                logger.warning(
                    "Bundle ID %r is already registered — overwriting with %r",
                    bundle_id,
                    mode.id,
                )
            self._bundle_to_mode[bundle_id] = mode

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def mode_for(self, bundle_identifier: str | None) -> AppMode:
        """
        Return the mode for the given bundle identifier, or the fallback
        if none is registered.
        """
        if bundle_identifier is None:
            return self._fallback
        return self._bundle_to_mode.get(bundle_identifier, self._fallback)

    @property
    def fallback(self) -> AppMode:
        return self._fallback
