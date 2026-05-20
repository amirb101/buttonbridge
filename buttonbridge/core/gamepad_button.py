"""Typed enum for every physical button on the 8BitDo Micro."""

from enum import Enum


class GamepadButton(Enum):
    """
    Every button the app can respond to.

    Values are display-friendly strings used in logs and (eventually)
    the preferences UI.  The actual mapping from hardware indices to
    these enum members lives in ControllerManager — nowhere else.
    """

    # Face buttons
    A = "A"
    B = "B"
    X = "X"
    Y = "Y"

    # D-pad
    DPAD_UP    = "D-Pad Up"
    DPAD_DOWN  = "D-Pad Down"
    DPAD_LEFT  = "D-Pad Left"
    DPAD_RIGHT = "D-Pad Right"

    # Shoulder buttons
    LEFT_SHOULDER  = "L1"
    RIGHT_SHOULDER = "R1"
    LEFT_TRIGGER   = "L2"
    RIGHT_TRIGGER  = "R2"

    # Menu buttons
    START  = "Start"
    SELECT = "Select"

    @property
    def display_name(self) -> str:
        return self.value
