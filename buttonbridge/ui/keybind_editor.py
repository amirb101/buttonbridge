"""
Legacy import path for opening the keybinding UI.

An older tab-based editor lived here; it depended on removed types
(``InputType``, ``KeybindMapping``) and a config shape that no longer exists.
The supported editor is :mod:`buttonbridge.ui.keybind_gui` (mode dropdown,
combobox assignment, reset). Start it from the menu bar or::

    python -m buttonbridge --buttonbridge-keybind-gui

For programmatic launch, use :func:`launch_keybinding_gui` or the alias
:func:`show_keybind_editor` (same callable).
"""

from __future__ import annotations

from .keybind_launch import launch_keybinding_gui

# Backwards-compatible name used by older snippets / forks.
show_keybind_editor = launch_keybinding_gui

__all__ = ["launch_keybinding_gui", "show_keybind_editor"]
