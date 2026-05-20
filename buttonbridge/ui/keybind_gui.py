#!/usr/bin/env python3
"""Standalone Tkinter GUI for editing keybindings - runs in subprocess."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from buttonbridge.config.keybind_config import (
    get_default_config,
    load_config,
    load_hotkey_list,
    save_config,
)
from buttonbridge.core.gamepad_button import GamepadButton


def _mode_display_label(mode_id: str) -> str:
    """Stable menu title for a mode id (must match keys in ``_mode_display_to_id``)."""
    return mode_id.replace("_", " ").title()


def _mode_id_from_display_label(label: str, display_to_id: dict[str, str]) -> str | None:
    """Resolve combobox text back to config key."""
    if not label:
        return None
    if label in display_to_id:
        return display_to_id[label]
    guess = label.lower().replace(" ", "_")
    return guess if guess in display_to_id.values() else None

UNASSIGNED = "Unassigned"


class KeybindGUI:
    """GUI for editing controller keybindings."""
    
    def __init__(self, root, readonly: bool = False):
        self.root = root
        self.readonly = readonly
        self.root.title("ButtonBridge - Hotkey List" if readonly else "ButtonBridge - Keybind Editor")
        self.root.geometry("620x480" if readonly else "500x480")
        self.root.minsize(460, 360)
        
        # Load configuration (readonly: controller + macOS shortcut per action)
        self.config = load_hotkey_list() if readonly else load_config()
        self.modified_config = {mode: dict(actions) for mode, actions in self.config.items()}

        self.mode_choices = sorted(self.config.keys())
        self._mode_display_to_id = {
            _mode_display_label(m): m for m in self.mode_choices
        }
        if readonly:
            n_rows = sum(
                len(v) for v in self.modified_config.values() if isinstance(v, dict)
            )
            print(
                f"ButtonBridge hotkey list: {len(self.mode_choices)} mode(s), {n_rows} action row(s)",
                file=sys.stderr,
            )

        # Track UI elements for each action
        self.bind_widgets = {}
        self.active_mode_id: str | None = None

        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        # Header
        header = ttk.Frame(self.root, padding="10")
        header.pack(fill="x")
        
        ttk.Label(
            header, 
            text="ButtonBridge Hotkey List" if self.readonly else "ButtonBridge Keybind Editor",
            font=("Helvetica", 16, "bold")
        ).pack(side="left")
        if self.readonly:
            hint = ttk.Frame(self.root, padding=(10, 0, 10, 4))
            hint.pack(fill="x")
            ttk.Label(
                hint,
                text="Each row shows which controller button is bound and which macOS shortcut it sends in this mode.",
                font=("Helvetica", 9),
                foreground="#555",
                wraplength=580,
            ).pack(anchor="w")
        
        # Mode selector (replaces crowded tabs)
        mode_selector = ttk.Frame(self.root, padding=(10, 0, 10, 5))
        mode_selector.pack(fill="x")
        ttk.Label(mode_selector, text="Mode:", font=("Helvetica", 10, "bold")).pack(side="left")
        self.mode_var = tk.StringVar()
        display_values = [_mode_display_label(m) for m in self.mode_choices]
        self.mode_dropdown = ttk.Combobox(
            mode_selector,
            textvariable=self.mode_var,
            values=display_values,
            state="readonly",
            width=28,
        )
        self.mode_dropdown.pack(side="left", padx=8)
        self.mode_dropdown.bind("<<ComboboxSelected>>", self._on_mode_changed)

        # Shared panel area
        self.mode_container = ttk.Frame(self.root, padding="5")
        self.mode_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Build first mode view
        if self.mode_choices:
            first = self.mode_choices[0]
            self.mode_var.set(_mode_display_label(first))
            self._render_mode(first)
        
        # Buttons at bottom
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill="x", side="bottom")

        if self.readonly:
            ttk.Button(
                button_frame,
                text="Close",
                command=self._cancel,
            ).pack(side="right", padx=5)
        else:
            ttk.Button(
                button_frame, 
                text="Reset All to Defaults",
                command=self._reset_all
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancel",
                command=self._cancel
            ).pack(side="right", padx=5)
            
            ttk.Button(
                button_frame,
                text="Save & Close",
                command=self._save_and_close
            ).pack(side="right", padx=5)
    
    def _create_mode_panel(self, parent: ttk.Frame, mode_id: str) -> ttk.Frame:
        """Create panel content for a specific mode."""
        tab = ttk.Frame(parent, padding="10")
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)

        if self.readonly:
            return self._create_readonly_table(tab, mode_id)

        # Scrollable frame for actions (editor only)
        canvas = tk.Canvas(tab, highlightthickness=0, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, padding="5")

        scroll_frame.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas_win = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _stretch_scroll_inner(event: tk.Event) -> None:
            canvas.itemconfigure(canvas_win, width=event.width)

        canvas.bind("<Configure>", _stretch_scroll_inner)

        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Headers
        ttk.Label(scroll_frame, text="Action", font=("Helvetica", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        if self.readonly:
            ttk.Label(
                scroll_frame,
                text="Controller",
                font=("Helvetica", 10, "bold"),
            ).grid(row=0, column=1, sticky="w", padx=5, pady=5)
            ttk.Label(
                scroll_frame,
                text="Sends (macOS)",
                font=("Helvetica", 10, "bold"),
            ).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        else:
            ttk.Label(
                scroll_frame,
                text="Button",
                font=("Helvetica", 10, "bold"),
            ).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Get actions for this mode
        actions = self.modified_config.get(mode_id, {})

        if not actions:
            ttk.Label(
                scroll_frame,
                text="No actions in config for this mode (check ~/.buttonbridge/keybindings.json).",
                font=("Helvetica", 10),
                foreground="#666",
                wraplength=520,
            ).grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=12)

        # Create dropdown for each action
        for idx, (action_name, info) in enumerate(actions.items(), start=1):
            ttk.Label(scroll_frame, text=action_name).grid(
                row=idx, column=0, sticky="w", padx=5, pady=3
            )

            if self.readonly:
                if isinstance(info, dict):
                    btn = str(info.get("button", "—"))
                    keys = str(info.get("keys", "—"))
                else:
                    btn = "—"
                    keys = f"(invalid row: {type(info).__name__})"
                btn_var = tk.StringVar(value=btn)
                keys_var = tk.StringVar(value=keys)
                ttk.Label(scroll_frame, textvariable=btn_var, width=14).grid(
                    row=idx, column=1, sticky="w", padx=5, pady=3
                )
                ttk.Label(scroll_frame, textvariable=keys_var, width=28).grid(
                    row=idx, column=2, sticky="w", padx=5, pady=3
                )
                self.bind_widgets[(mode_id, action_name)] = (btn_var, keys_var)
            else:
                # Button dropdown
                button_var = tk.StringVar(value=info)
                dropdown = ttk.Combobox(
                    scroll_frame,
                    textvariable=button_var,
                    values=[UNASSIGNED] + [b.value for b in GamepadButton],
                    state="readonly",
                    width=20
                )
                dropdown.grid(row=idx, column=1, sticky="w", padx=5, pady=3)
                
                # Store reference
                self.bind_widgets[(mode_id, action_name)] = (dropdown, button_var)

        scroll_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        return tab

    def _create_readonly_table(self, tab: ttk.Frame, mode_id: str) -> ttk.Frame:
        """
        Read-only hotkey list using Treeview (reliable on macOS system Tk).

        Canvas + ttk.Label(textvariable=…) often renders blank on deprecated macOS Tk.
        """
        actions = self.modified_config.get(mode_id, {})
        outer = ttk.Frame(tab)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)

        columns = ("action", "button", "keys")
        tree = ttk.Treeview(
            outer,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=min(20, max(6, len(actions) + 1)),
        )
        tree.heading("action", text="Action")
        tree.heading("button", text="Controller")
        tree.heading("keys", text="Sends (macOS)")
        tree.column("action", width=180, minwidth=120, stretch=True)
        tree.column("button", width=120, minwidth=80, stretch=False)
        tree.column("keys", width=260, minwidth=160, stretch=True)

        if not actions:
            tree.insert("", tk.END, values=("(no actions for this mode)", "—", "—"))
        else:
            for action_name, info in actions.items():
                if isinstance(info, dict):
                    btn = str(info.get("button", "—"))
                    keys = str(info.get("keys", "—"))
                else:
                    btn = "—"
                    keys = f"(invalid: {type(info).__name__})"
                tree.insert("", tk.END, values=(action_name, btn, keys))

        vsb = ttk.Scrollbar(outer, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        return tab

    def _save_current_mode_from_widgets(self) -> None:
        """Persist on-screen edits for the active mode to modified_config."""
        if self.readonly:
            return
        if not self.active_mode_id:
            return
        for (mode, action), (_, var) in self.bind_widgets.items():
            if mode == self.active_mode_id:
                self.modified_config[mode][action] = var.get()

    def _render_mode(self, mode_id: str) -> None:
        """Render exactly one mode panel."""
        # Save current state before switching.
        self._save_current_mode_from_widgets()
        self.active_mode_id = mode_id

        # Clear previous content/widgets.
        for child in self.mode_container.winfo_children():
            child.destroy()
        self.bind_widgets = {
            key: value for key, value in self.bind_widgets.items() if key[0] != mode_id
        }

        panel = self._create_mode_panel(self.mode_container, mode_id)
        panel.pack(fill="both", expand=True)

    def _on_mode_changed(self, _event=None):
        """Handle mode dropdown change."""
        label = self.mode_var.get()
        mode_id = _mode_id_from_display_label(label, self._mode_display_to_id)
        if mode_id and mode_id in self.modified_config:
            self._render_mode(mode_id)
    
    def _reset_all(self):
        """Reset all keybindings to defaults."""
        if messagebox.askyesno(
            "Reset All",
            "Are you sure you want to reset all keybindings to defaults?"
        ):
            self.modified_config = get_default_config()
            self._refresh_ui()
    
    def _refresh_ui(self):
        """Refresh the UI with current configuration."""
        if self.readonly:
            for (mode, action), (btn_var, keys_var) in self.bind_widgets.items():
                if mode in self.modified_config and action in self.modified_config[mode]:
                    cell = self.modified_config[mode][action]
                    if isinstance(cell, dict):
                        btn_var.set(cell.get("button", ""))
                        keys_var.set(cell.get("keys", ""))
            return
        for (mode, action), (_, var) in self.bind_widgets.items():
            if mode in self.modified_config and action in self.modified_config[mode]:
                var.set(self.modified_config[mode][action])
    
    def _cancel(self):
        """Close without saving."""
        self.root.destroy()
    
    def _save_and_close(self):
        """Save configuration and close."""
        if self.readonly:
            self.root.destroy()
            return
        self._save_current_mode_from_widgets()
        # Collect all bindings from UI
        for (mode, action), (_, var) in self.bind_widgets.items():
            self.modified_config[mode][action] = var.get()
        
        # Save to file
        try:
            save_config(self.modified_config)
            messagebox.showinfo("Success", "Configuration saved successfully!")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")


def run_standalone(readonly: bool = False) -> None:
    """Entry point for subprocess / ``python -m buttonbridge --buttonbridge-keybind-gui``."""
    os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")
    root = tk.Tk()
    # macOS system Tk: force a normal light background so labels/trees are visible
    try:
        root.tk.call("tk", "scaling", 1.0)
    except tk.TclError:
        pass
    KeybindGUI(root, readonly=readonly)
    root.update_idletasks()
    root.mainloop()


if __name__ == "__main__":
    run_standalone()
