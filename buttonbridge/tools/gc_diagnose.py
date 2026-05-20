"""
Diagnose controller input via Apple's GameController framework (PyObjC).

This bypasses pygame/SDL and prints what GameController itself reports.
Useful when a device behaves differently between browser testers and pygame.

Examples:
    python -m buttonbridge.tools.gc_diagnose --seconds 20
    BUTTONBRIDGE_GC_PROFILE=physical python -m buttonbridge.tools.gc_diagnose --seconds 20
"""

from __future__ import annotations

import argparse
import os
import time

from Foundation import NSDate, NSRunLoop


def _objc_prop(obj, name: str):
    if obj is None:
        return None
    attr = getattr(obj, name, None)
    if attr is None:
        return None
    return attr() if callable(attr) else attr


def _btn_pressed(btn) -> bool:
    if btn is None:
        return False
    try:
        return bool(btn.isPressed())
    except Exception:
        return False


def _norm(s: str) -> str:
    return "".join(c.lower() for c in s if c.isalnum())


def _face_state_extended(pad) -> dict[str, bool]:
    return {
        "A": _btn_pressed(_objc_prop(pad, "buttonA")),
        "B": _btn_pressed(_objc_prop(pad, "buttonB")),
        "X": _btn_pressed(_objc_prop(pad, "buttonX")),
        "Y": _btn_pressed(_objc_prop(pad, "buttonY")),
    }


def _face_state_physical(pip) -> dict[str, bool]:
    out = {"A": False, "B": False, "X": False, "Y": False}
    try:
        buttons = pip.allButtons()
    except Exception:
        return out
    if buttons is None:
        return out

    for i in range(buttons.count()):
        el = buttons.objectAtIndex_(i)
        alias = str(
            _objc_prop(el, "primaryAlias")
            or _objc_prop(el, "localizedName")
            or _objc_prop(el, "unmappedLocalizedName")
            or ""
        )
        n = _norm(alias)
        if "buttona" in n or n == "a" or "cross" in n:
            out["A"] = out["A"] or _btn_pressed(el)
        elif "buttonb" in n or n == "b" or "circle" in n:
            out["B"] = out["B"] or _btn_pressed(el)
        elif "buttonx" in n or n == "x" or "square" in n:
            out["X"] = out["X"] or _btn_pressed(el)
        elif "buttony" in n or n == "y" or "triangle" in n:
            out["Y"] = out["Y"] or _btn_pressed(el)
    return out


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnose Apple GameController input")
    p.add_argument("--seconds", type=float, default=20.0, help="Capture duration")
    p.add_argument("--interval-ms", type=float, default=16.0, help="Poll interval")
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    from GameController import GCController

    print("=== ButtonBridge GC Diagnose ===")
    print(f"BUTTONBRIDGE_GC_PROFILE={os.environ.get('BUTTONBRIDGE_GC_PROFILE', '(unset)')}")
    print(
        "Tip: press A/B/X/Y one at a time. If all four become True together, "
        "GameController profile is collapsing them."
    )
    print()

    start = time.monotonic()
    last_print = None
    profile_once = False

    while time.monotonic() - start < args.seconds:
        ctrls = GCController.controllers()
        if not ctrls:
            if last_print != "no-devices":
                print("No GameController devices.")
                last_print = "no-devices"
            NSRunLoop.currentRunLoop().runUntilDate_(
                NSDate.dateWithTimeIntervalSinceNow_(args.interval_ms / 1000.0)
            )
            continue

        c = ctrls[0]
        name = _objc_prop(c, "vendorName") or "controller"
        ext = _objc_prop(c, "extendedGamepad") or _objc_prop(c, "gamepad")
        micro = _objc_prop(c, "microGamepad")
        pip = _objc_prop(c, "physicalInputProfile")

        if not profile_once:
            print(
                f"Connected: {name} | profiles: "
                f"extended={'yes' if ext else 'no'} "
                f"micro={'yes' if micro else 'no'} "
                f"physical={'yes' if pip else 'no'}"
            )
            profile_once = True

        ext_state = _face_state_extended(ext) if ext else None
        pip_state = _face_state_physical(pip) if pip else None
        current = (tuple(ext_state.items()) if ext_state else None, tuple(pip_state.items()) if pip_state else None)
        if current != last_print:
            t = time.monotonic() - start
            if ext_state:
                print(f"{t:7.3f}s extended A/B/X/Y: {ext_state}")
            if pip_state:
                print(f"{t:7.3f}s physical A/B/X/Y: {pip_state}")
            last_print = current

        NSRunLoop.currentRunLoop().runUntilDate_(
            NSDate.dateWithTimeIntervalSinceNow_(args.interval_ms / 1000.0)
        )

    print("Done.")


if __name__ == "__main__":
    main()

