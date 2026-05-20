#!/usr/bin/env python3
"""Exit 0 if every default KeybindAction.name maps to a mode action; else print gaps and exit 1."""
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buttonbridge.config.keybind_config import KeybindConfig
from buttonbridge.core.configurable_mode import ConfigurableMode


def main() -> int:
    mode_classes: list[tuple[str, type]] = []
    for p in sorted((ROOT / "buttonbridge" / "modes").glob("*_mode.py")):
        mod = importlib.import_module(f"buttonbridge.modes.{p.stem}")
        for _name, cls in inspect.getmembers(mod, inspect.isclass):
            if not issubclass(cls, ConfigurableMode) or cls is ConfigurableMode:
                continue
            mid = getattr(cls, "id", None)
            if isinstance(mid, str):
                mode_classes.append((mid, cls))

    cfg = KeybindConfig()
    issues: list[str] = []
    for mode_id, cls in sorted(mode_classes, key=lambda x: x[0]):
        inst = cls()
        mc = cfg.modes.get(mode_id)
        if not mc:
            issues.append(f"missing mode in defaults: {mode_id} ({cls.__name__})")
            continue
        for bid, act in sorted(mc.button_map.items()):
            if not act.enabled:
                continue
            if inst._create_action_from_id(act.name) is None:
                issues.append(f"{mode_id} button {bid}: no action for name={act.name!r}")

    if issues:
        print(f"validate_keybind_actions: {len(issues)} issue(s)\n")
        for line in issues:
            print(line)
        return 1
    print(f"validate_keybind_actions: OK ({len(mode_classes)} modes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
