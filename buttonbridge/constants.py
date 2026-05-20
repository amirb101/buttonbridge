"""
All app-wide constants live here.

Nothing elsewhere in the codebase should contain a raw number or
bundle-ID string — if it isn't obvious at the call site, it belongs
here with a comment explaining it.
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Overlay / status bar
# ---------------------------------------------------------------------------

class Overlay:
    """Timing for the mode-change status bar flash."""
    HOLD_SECONDS: float = 2.0          # how long the mode label stays visible


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------

class Controller:
    """Pygame joystick behaviour."""

    # Minimum axis value (0–1) to count a trigger as "pressed".
    TRIGGER_PRESS_THRESHOLD: float = 0.5

    # How often (seconds) to poll the pygame event queue.
    POLL_INTERVAL_SECONDS: float = 0.016   # ~60 Hz

    # ---------------------------------------------------------------------------
    # 8BitDo Micro button indices in D-input mode (pygame joystick)
    #
    # These were determined empirically. If buttons feel wrong on your unit,
    # run `python -m buttonbridge.tools.button_logger` (see tools/)
    # to print every raw event and remap here.
    # ---------------------------------------------------------------------------
    class ButtonIndex:
        A      = 0
        B      = 1
        X      = 2   # 8BitDo Micro often uses 5 for X — see EIGHTBITDO_MICRO_MAP
        Y      = 4
        X_ALT  = 5   # secondary X on some 8BitDo firmware (SDL)
        L1     = 6
        R1     = 7
        L2     = 8   # may arrive as axis on some firmware — see ControllerManager
        R2     = 9
        SELECT = 10
        START  = 11

    # D-pad arrives as a pygame "hat" event. Hat value → direction name.
    # Hat tuples are (x, y) where x: -1=left, 1=right; y: -1=down, 1=up.
    class HatDirection:
        UP    = (0,  1)
        DOWN  = (0, -1)
        LEFT  = (-1, 0)
        RIGHT = (1,  0)

    # Axis index for analogue triggers (if the firmware uses axes not buttons).
    class AxisIndex:
        LEFT_TRIGGER  = 4
        RIGHT_TRIGGER = 5


# ---------------------------------------------------------------------------
# App detection polling
# ---------------------------------------------------------------------------

class Detection:
    # How often (seconds) to check the frontmost application.
    # 0.5 s is imperceptible to the user and light on CPU.
    POLL_INTERVAL_SECONDS: float = 0.5


# ---------------------------------------------------------------------------
# Spotify
# ---------------------------------------------------------------------------

class Spotify:
    VOLUME_STEP: int    = 10    # points per press (Spotify's 0–100 scale)
    SEEK_STEP_SECONDS: float = 15.0


# ---------------------------------------------------------------------------
# System volume
# ---------------------------------------------------------------------------

class Volume:
    STEP_SIZE: int = 10   # points per press (system 0–100 scale)


# ---------------------------------------------------------------------------
# Bundle identifiers
# ---------------------------------------------------------------------------

class BundleID:
    """
    CFBundleIdentifier strings for every app the app cares about.

    ⚠  Comet browser: verify on the target Mac before shipping:
        mdls -name kMDItemCFBundleIdentifier /Applications/Comet.app
    """
    SPOTIFY  = "com.spotify.client"
    OBSIDIAN = "md.obsidian"
    
    # Productivity apps
    APPLE_MUSIC = "com.apple.Music"
    FINDER = "com.apple.finder"
    PREVIEW = "com.apple.Preview"
    
    # Development
    VS_CODE = "com.microsoft.VSCode"
    CURSOR = "com.todesktop.230313mzl4w4u92"  # Cursor IDE
    
    # Productivity
    # Anki: bundle ID changed across releases; we register all known values.
    # If Anki still maps to Global, focus Anki once and read the log line
    # ``Frontmost app bundle id: …`` from AppDetector, then add the id here.
    ANKI = "net.ankiweb.dtop"
    ALL_ANKI_BUNDLE_IDS: list[str] = [
        "net.ankiweb.dtop",       # classic official macOS build
        "net.ankiweb.launcher",   # newer launcher-based packaging (common on recent releases)
        "net.ankiweb.Anki",       # some builds / channels
        "net.ichi2.anki",         # very old installs
    ]
    NOTION = "notion.id"
    FIGMA = "com.figma.Desktop"
    NOTES = "com.apple.Notes"

    # Microsoft Office
    WORD = "com.microsoft.Word"
    OUTLOOK = "com.microsoft.Outlook"

    # Apple
    PHOTO_BOOTH = "com.apple.PhotoBooth"

    # AI
    CHATGPT = "com.openai.chat"
    CLAUDE_DESKTOP = "com.anthropic.claudefordesktop"

    # Communication
    MESSAGES = "com.apple.MobileSMS"
    WHATSAPP = "net.whatsapp.WhatsApp"
    FACETIME = "com.apple.FaceTime"
    # macOS Phone app (verify with: mdls -name kMDItemCFBundleIdentifier /System/Applications/Phone.app)
    PHONE = "com.apple.mobilephone"

    # Browser bundle IDs (most share standard macOS shortcuts)
    CHROME   = "com.google.Chrome"
    ARC      = "company.thebrowser.Browser"
    EDGE     = "com.microsoft.Edge"
    BRAVE    = "com.brave.Browser"
    COMET    = "ai.perplexity.comet"
    SAFARI   = "com.apple.Safari"
    FIREFOX  = "org.mozilla.firefox"
    FIREFOX_NIGHTLY = "org.mozilla.nightly"
    OPERA    = "com.operasoftware.Opera"
    VIVALDI  = "com.vivaldi.Vivaldi"
    ORION    = "com.kagi.kagimac"
    ZEN      = "app.zen-browser.zen"

    # All browsers that use standard macOS shortcuts (Cmd+T, Cmd+W, Cmd+[, etc.)
    ALL_BROWSERS: list[str] = [
        CHROME,
        ARC,
        EDGE,
        BRAVE,
        COMET,
        SAFARI,
        FIREFOX,
        FIREFOX_NIGHTLY,
        OPERA,
        VIVALDI,
        ORION,
        ZEN,
    ]

    # Keep for backwards compatibility
    CHROMIUM_BROWSERS = ALL_BROWSERS
