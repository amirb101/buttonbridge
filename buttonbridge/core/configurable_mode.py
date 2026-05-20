"""
AppMode subclass that reads keybindings from configuration.

This allows users to customize button mappings via the GUI editor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .app_mode import AppMode
from .action import Action, keystroke
from .button_combo import ButtonCombo
from .gamepad_button import GamepadButton

if TYPE_CHECKING:
    from ..config.keybind_config import ModeConfig


class ConfigurableMode(AppMode):
    """
    A mode that reads its button mappings from the keybinding configuration.

    Subclasses define their available actions, and the actual button mappings
    are loaded from the user's config file.
    """

    @property
    def config_mode_id(self) -> str:
        """The mode ID in the configuration file."""
        return self.id

    def _get_mode_config(self) -> ModeConfig | None:
        """Get the configuration for this mode."""
        from ..config.keybind_config import get_config
        return get_config().get_mode(self.config_mode_id)

    def _action_to_keystroke(self, action_id: str) -> Action:
        """Convert an action ID to an Action. Override in subclasses."""
        # Default: just press a key (subclasses should override)
        return keystroke("a", id=action_id, name=action_id)

    @property
    def button_map(self) -> dict[GamepadButton, Action]:
        """Build button map from configuration."""
        result: dict[GamepadButton, Action] = {}
        mode_config = self._get_mode_config()
        if not mode_config:
            return result

        ordered = list(GamepadButton)
        for bid, act in sorted(mode_config.button_map.items(), key=lambda x: x[0]):
            if not act.enabled:
                continue
            idx = (act.button_id or bid) - 1
            if idx < 0 or idx >= len(ordered):
                continue
            button = ordered[idx]
            keystroke_action = self._create_action_from_id(act.name)
            if keystroke_action:
                result[button] = keystroke_action

        return result

    @property
    def combo_map(self) -> dict[ButtonCombo, Action]:
        """Combo bindings (not yet used in JSON defaults)."""
        return {}

    def _create_action_from_id(self, action_id: str) -> Action | None:
        """
        Create an Action from an action ID.
        Subclasses should override this to provide the actual keystrokes.
        """
        raise NotImplementedError("Subclasses must implement _create_action_from_id")
