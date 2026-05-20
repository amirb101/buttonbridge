"""Run with: ``python -m buttonbridge`` (from the repository root)."""

import sys

# Child process: keybind editor (works when frozen as a .app — no path to keybind_gui.py).
if "--buttonbridge-keybind-gui" in sys.argv:
    from buttonbridge.ui.keybind_gui import run_standalone

    run_standalone(readonly="--readonly" in sys.argv)
    raise SystemExit(0)

# Child process: print hotkey list to stdout (used by menu action for Terminal output).
if "--print-hotkeys" in sys.argv:
    from buttonbridge.config.keybind_config import format_hotkey_list_text

    print(format_hotkey_list_text())
    raise SystemExit(0)


def _ns_app_bootstrap() -> None:
    """Ensure NSApplication exists before any AppKit modal UI."""
    from AppKit import NSApplication

    app = NSApplication.sharedApplication()
    app.activateIgnoringOtherApps_(True)


def show_startup_choice():
    """
    Ask whether to open the keybinding editor first.

    Uses AppKit (NSAlert), not Tkinter: loading Tcl/Tk before rumps/AppKit and then
    tearing it down can crash later with ``Tcl_FindHashEntry on deleted table``.
    """
    from AppKit import NSAlert, NSAlertSecondButtonReturn

    _ns_app_bootstrap()

    alert = NSAlert.alloc().init()
    alert.setMessageText_("ButtonBridge")
    alert.setInformativeText_("Configure controller keybindings first?")
    # Right-to-left in sheet: first added is the trailing (right) button on macOS.
    alert.addButtonWithTitle_("No - Launch Now")
    alert.addButtonWithTitle_("Yes - Configure First")
    resp = alert.runModal()
    return resp == NSAlertSecondButtonReturn


def _show_error_alert(title: str, message: str) -> None:
    from AppKit import NSAlert, NSApplication

    NSApplication.sharedApplication()
    _ns_app_bootstrap()
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    text = message if len(message) <= 12000 else message[:12000] + "\n…(truncated)"
    alert.setInformativeText_(text)
    alert.addButtonWithTitle_("OK")
    alert.runModal()


def _show_yes_no_alert(title: str, message: str) -> bool:
    from AppKit import NSAlert, NSAlertSecondButtonReturn, NSApplication

    NSApplication.sharedApplication()
    _ns_app_bootstrap()
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(message)
    alert.addButtonWithTitle_("Cancel")
    alert.addButtonWithTitle_("Launch")
    return alert.runModal() == NSAlertSecondButtonReturn


def launch_keybinding_gui(readonly: bool = False) -> bool:
    """Launch the keybinding GUI in a subprocess (separate Tk main loop)."""
    from buttonbridge.ui.keybind_launch import launch_keybinding_gui as _launch

    return _launch(readonly=readonly)


def main():
    """Entry point with startup choice."""
    # Check if launched with --configure flag
    if "--configure" in sys.argv:
        if launch_keybinding_gui():
            launch = _show_yes_no_alert(
                "Configuration Complete",
                "Keybindings saved.\n\nLaunch ButtonBridge now?",
            )

            if launch:
                from buttonbridge.main import main as real_main
                real_main()
        return
    
    # Check if launched with --no-gui flag (skip startup dialog)
    if "--no-gui" in sys.argv:
        try:
            from buttonbridge.main import main as real_main
            real_main()
        except Exception as e:
            import traceback

            _show_error_alert(
                "ButtonBridge launch failed",
                f"{e}\n\n{traceback.format_exc()}",
            )
        return
    
    # Show startup choice
    choice = show_startup_choice()
    
    if choice:
        # User wants to configure first
        if launch_keybinding_gui():
            # After GUI closes, launch main app
            try:
                from buttonbridge.main import main as real_main
                real_main()
            except Exception as e:
                import traceback

                _show_error_alert(
                    "ButtonBridge launch failed",
                    f"{e}\n\n{traceback.format_exc()}",
                )
    else:
        # User wants to launch directly
        try:
            from buttonbridge.main import main as real_main
            real_main()
        except Exception as e:
            import traceback

            _show_error_alert(
                "ButtonBridge launch failed",
                f"{e}\n\n{traceback.format_exc()}",
            )


if __name__ == "__main__":
    main()
