"""
Controller diagnose tool for 8BitDo/SDL quirks on macOS.

Runs pygame joystick input in standalone mode and prints timestamped raw events.
Useful for spotting:
- one physical press generating multiple JOYBUTTONDOWN events
- D-pad hat direction inversion
- differences between SDL HIDAPI on/off

Usage examples:
    python -m buttonbridge.tools.controller_diagnose --seconds 20
    python -m buttonbridge.tools.controller_diagnose --seconds 20 --hidapi 0
    python -m buttonbridge.tools.controller_diagnose --seconds 20 --hidapi 1
"""

from __future__ import annotations

import argparse
import os
import time


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnose raw controller events.")
    p.add_argument(
        "--seconds",
        type=float,
        default=20.0,
        help="How long to capture events (default: 20).",
    )
    p.add_argument(
        "--hidapi",
        choices=["0", "1"],
        default=None,
        help="Set SDL_JOYSTICK_HIDAPI explicitly before pygame init.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    if args.hidapi is not None:
        os.environ["SDL_JOYSTICK_HIDAPI"] = args.hidapi

    from buttonbridge.sdl_bootstrap import bootstrap_pygame_for_standalone_cli

    bootstrap_pygame_for_standalone_cli()
    import pygame

    print("=== ButtonBridge Controller Diagnose ===")
    print(f"SDL_JOYSTICK_HIDAPI={os.environ.get('SDL_JOYSTICK_HIDAPI', '(unset)')}")
    print(f"Capture window: {args.seconds:.1f}s")
    print("Tip: Press A only 5x, then B only 5x, then X only 5x, then Y only 5x.")
    print("      Press D-pad up/down/left/right once each.\n")

    start = time.monotonic()
    last_down = 0.0
    joystick = None

    while time.monotonic() - start < args.seconds:
        count = pygame.joystick.get_count()
        if count > 0 and joystick is None:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"CONNECTED: {joystick.get_name()}")
            print(
                f"buttons={joystick.get_numbuttons()} axes={joystick.get_numaxes()} hats={joystick.get_numhats()}\n"
            )
        elif count == 0 and joystick is not None:
            print("DISCONNECTED")
            joystick = None

        for event in pygame.event.get():
            t = time.monotonic() - start
            if event.type == pygame.JOYBUTTONDOWN:
                delta_ms = (time.monotonic() - last_down) * 1000.0 if last_down else 0.0
                last_down = time.monotonic()
                print(f"{t:7.3f}s  BUTTON_DOWN index={event.button:>2}  dt={delta_ms:>6.1f}ms")
            elif event.type == pygame.JOYBUTTONUP:
                print(f"{t:7.3f}s  BUTTON_UP   index={event.button:>2}")
            elif event.type == pygame.JOYHATMOTION:
                print(f"{t:7.3f}s  HAT        value={event.value}")
            elif event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.15:
                print(f"{t:7.3f}s  AXIS       axis={event.axis} value={event.value:+.3f}")

        pygame.time.wait(8)

    print("\nDone.")


if __name__ == "__main__":
    main()

