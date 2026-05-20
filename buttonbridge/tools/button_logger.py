"""
Button logger — prints every raw pygame joystick event to the terminal.

Run this first to verify the 8BitDo Micro's button indices on your machine,
then update ``buttonbridge/constants.py`` → ``Controller.ButtonIndex``.

Standalone process (no rumps) — on macOS may use a hidden SDL window so devices enumerate.

Usage:
    python -m buttonbridge.tools.button_logger
"""

from __future__ import annotations

import sys


def main() -> None:
    from buttonbridge.sdl_bootstrap import bootstrap_pygame_for_standalone_cli

    bootstrap_pygame_for_standalone_cli()
    import pygame

    print("Waiting for a controller… (press Ctrl+C to quit)\n")

    joystick = None

    while True:
        count = pygame.joystick.get_count()

        if count > 0 and joystick is None:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"✓ Controller connected: {joystick.get_name()}")
            print(f"  Buttons: {joystick.get_numbuttons()}")
            print(f"  Axes:    {joystick.get_numaxes()}")
            print(f"  Hats:    {joystick.get_numhats()}\n")
            print("Press buttons to see their indices:\n")

        elif count == 0 and joystick is not None:
            print("Controller disconnected.")
            joystick = None

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                print(f"  BUTTON DOWN  index={event.button}")
                print(
                    "    → add to ~/.buttonbridge/pygame_button_map.json "
                    f'as "{event.button}": "A"  (change A to the face button you pressed)'
                )
            elif event.type == pygame.JOYBUTTONUP:
                print(f"  BUTTON UP    index={event.button}")
            elif event.type == pygame.JOYHATMOTION:
                print(f"  HAT MOTION   value={event.value}")
            elif event.type == pygame.JOYAXISMOTION:
                if abs(event.value) > 0.1:  # ignore tiny drift
                    print(f"  AXIS MOTION  axis={event.axis}  value={event.value:.3f}")

        pygame.time.wait(16)  # ~60 Hz


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDone.")
        sys.exit(0)
