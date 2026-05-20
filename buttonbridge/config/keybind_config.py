"""Keybinding configuration for ButtonBridge controller."""

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class KeybindAction:
    """Represents a single keybinding action."""
    name: str
    description: str
    key_sequence: str
    button_id: int = 0
    enabled: bool = True


@dataclass
class ModeConfig:
    """Configuration for a single mode."""
    name: str
    description: str
    button_map: Dict[int, KeybindAction] = field(default_factory=dict)
    combo_map: Dict[str, KeybindAction] = field(default_factory=dict)


class KeybindConfig:
    """Manages keybinding configurations for all modes."""
    
    CONFIG_FILE = Path.home() / ".buttonbridge" / "keybindings.json"
    
    def __init__(self):
        self.modes: Dict[str, ModeConfig] = {}
        self.global_shortcuts: Dict[str, str] = {}
        self._create_defaults()
    
    def _create_defaults(self):
        """Create default configurations for all built-in modes."""
        # Default gamepad slot convention (button_id → face button order in GamepadButton):
        #   1=A primary "new/open", 2=B "close/dismiss" where the app supports it,
        #   3–4 support actions, 5–6 search/navigation, 7–8 secondary / tabs / extras.
        # Browser, VS Code, and Cursor share the same slot for close-tab (cmd+w) on 2.

        # 1. Browser Mode (Chrome/Safari)
        self.modes["browser"] = ModeConfig(
            name="Browser",
            description="Web browser navigation",
            button_map={
                1: KeybindAction("new_tab", "Open new tab", "cmd+t", 1),
                2: KeybindAction("close_tab", "Close current tab", "cmd+w", 2),
                3: KeybindAction("reload", "Reload page", "cmd+r", 3),
                4: KeybindAction("page_back", "Go back", "cmd+[", 4),
                5: KeybindAction("page_forward", "Go forward", "cmd+]", 5),
                6: KeybindAction("find", "Find in page", "cmd+f", 6),
                7: KeybindAction("prev_tab", "Previous tab", "cmd+shift+left", 7),
                8: KeybindAction("next_tab", "Next tab", "cmd+shift+right", 8),
            }
        )
        
        # 2. Spotify Mode
        self.modes["spotify"] = ModeConfig(
            name="Spotify",
            description="Music playback controls",
            button_map={
                1: KeybindAction("play_pause", "Play/Pause", "space", 1),
                2: KeybindAction("next_track", "Next track", "cmd+right", 2),
                3: KeybindAction("prev_track", "Previous track", "cmd+left", 3),
                4: KeybindAction("volume_up", "Volume up", "cmd+up", 4),
                5: KeybindAction("volume_down", "Volume down", "cmd+down", 5),
                6: KeybindAction("shuffle", "Toggle shuffle", "cmd+s", 6),
                7: KeybindAction("repeat", "Toggle repeat", "cmd+r", 7),
                8: KeybindAction("like", "Like song", "cmd+l", 8),
            }
        )
        
        # 3. Obsidian Mode
        self.modes["obsidian"] = ModeConfig(
            name="Obsidian",
            description="Note-taking and knowledge management",
            button_map={
                1: KeybindAction("new_note", "New note", "cmd+n", 1),
                2: KeybindAction("quick_switcher", "Quick switcher", "cmd+o", 2),
                3: KeybindAction("command_palette", "Command palette", "cmd+p", 3),
                4: KeybindAction("graph_view", "Open graph view", "ctrl+shift+g", 4),
                5: KeybindAction("daily_note", "Open daily note", "ctrl+shift+d", 5),
                6: KeybindAction("search_all", "Search all files", "cmd+shift+f", 6),
                7: KeybindAction("toggle_preview", "Toggle preview", "cmd+e", 7),
                8: KeybindAction("insert_link", "Insert link", "cmd+k", 8),
            }
        )
        
        # 4. Global Mode (System-wide)
        self.modes["global"] = ModeConfig(
            name="Global",
            description="System-wide shortcuts",
            button_map={
                1: KeybindAction("spotlight", "Open Spotlight", "cmd+space", 1),
                2: KeybindAction("screenshot", "Screenshot (region)", "cmd+shift+4", 2),
                3: KeybindAction("mission_control", "Mission Control", "ctrl+up", 3),
                4: KeybindAction("play_pause", "Play / Pause (Spotify)", "space", 4),
                5: KeybindAction("lock_screen", "Lock screen", "cmd+ctrl+q", 5),
                6: KeybindAction("volume_up", "Volume up", "cmd+up", 6),
                7: KeybindAction("volume_down", "Volume down", "cmd+down", 7),
                8: KeybindAction("mute", "Toggle mute", "mute", 8),
            }
        )
        
        # 5. Finder Mode
        self.modes["finder"] = ModeConfig(
            name="Finder",
            description="File management",
            button_map={
                1: KeybindAction("new_folder", "New folder", "cmd+shift+n", 1),
                2: KeybindAction("quick_look", "Quick Look", "space", 2),
                3: KeybindAction("search", "Search", "cmd+f", 3),
                4: KeybindAction("get_info", "Get info", "cmd+i", 4),
                5: KeybindAction("go_back", "Go back", "cmd+[", 5),
                6: KeybindAction("go_forward", "Go forward", "cmd+]", 6),
                7: KeybindAction("trash", "Move to trash", "cmd+delete", 7),
                8: KeybindAction("show_hidden", "Show hidden files", "cmd+shift+.", 8),
            }
        )
        
        # 6. Apple Music Mode
        self.modes["apple_music"] = ModeConfig(
            name="Apple Music",
            description="Apple Music controls",
            button_map={
                1: KeybindAction("play_pause", "Play/Pause", "space", 1),
                2: KeybindAction("next_track", "Next track", "right", 2),
                3: KeybindAction("prev_track", "Previous track", "left", 3),
                4: KeybindAction("volume_up", "Volume up", "up", 4),
                5: KeybindAction("volume_down", "Volume down", "down", 5),
                6: KeybindAction("shuffle", "Toggle shuffle", "cmd+s", 6),
                7: KeybindAction("search", "Search", "cmd+f", 7),
                8: KeybindAction("love", "Love song", "l", 8),
            }
        )
        
        # 7. Preview Mode
        self.modes["preview"] = ModeConfig(
            name="Preview",
            description="Image/PDF viewing",
            button_map={
                1: KeybindAction("zoom_in", "Zoom in", "cmd+=", 1),
                2: KeybindAction("zoom_out", "Zoom out", "cmd+-", 2),
                3: KeybindAction("actual_size", "Actual size", "cmd+0", 3),
                4: KeybindAction("share", "Share", "cmd+s", 4),
                5: KeybindAction("next_page", "Next page", "right", 5),
                6: KeybindAction("prev_page", "Previous page", "left", 6),
                7: KeybindAction("rotate_left", "Rotate left", "cmd+l", 7),
                8: KeybindAction("rotate_right", "Rotate right", "cmd+r", 8),
            }
        )
        
        # 8. VS Code Mode
        self.modes["vscode"] = ModeConfig(
            name="VS Code",
            description="Code editor shortcuts",
            button_map={
                1: KeybindAction("command_palette", "Command palette", "cmd+shift+p", 1),
                2: KeybindAction("close_tab", "Close tab", "cmd+w", 2),
                3: KeybindAction("toggle_terminal", "Toggle terminal", "ctrl+`", 3),
                4: KeybindAction("go_definition", "Go to definition", "f12", 4),
                5: KeybindAction("find", "Find", "cmd+f", 5),
                6: KeybindAction("save", "Save", "cmd+s", 6),
                7: KeybindAction("new_file", "New file", "cmd+n", 7),
                8: KeybindAction("quick_open", "Quick open", "cmd+p", 8),
            }
        )

        # 8b. Cursor Mode (same defaults as VS Code; edit separately if you want)
        self.modes["cursor"] = ModeConfig(
            name="Cursor",
            description="Cursor editor shortcuts",
            button_map={
                1: KeybindAction("command_palette", "Command palette", "cmd+shift+p", 1),
                2: KeybindAction("close_tab", "Close tab", "cmd+w", 2),
                3: KeybindAction("toggle_terminal", "Toggle terminal", "ctrl+`", 3),
                4: KeybindAction("go_definition", "Go to definition", "f12", 4),
                5: KeybindAction("find", "Find", "cmd+f", 5),
                6: KeybindAction("save", "Save", "cmd+s", 6),
                7: KeybindAction("new_file", "New file", "cmd+n", 7),
                8: KeybindAction("quick_open", "Quick open", "cmd+p", 8),
            }
        )

        # 9. Anki Mode
        self.modes["anki"] = ModeConfig(
            name="Anki",
            description="Spaced-repetition study flow",
            button_map={
                1: KeybindAction("show_answer", "Show answer", "space", 1),
                2: KeybindAction("again", "Rate Again", "1", 2),
                3: KeybindAction("hard", "Rate Hard", "2", 3),
                4: KeybindAction("good", "Rate Good", "3", 4),
                5: KeybindAction("easy", "Rate Easy", "4", 5),
                6: KeybindAction("undo", "Undo", "cmd+z", 6),
                7: KeybindAction("bury", "Bury card", "-", 7),
                8: KeybindAction("suspend", "Suspend card", "=", 8),
            }
        )

        # 10. Notion Mode
        self.modes["notion"] = ModeConfig(
            name="Notion",
            description="Workspace management",
            button_map={
                1: KeybindAction("quick_find", "Quick find", "cmd+k", 1),
                2: KeybindAction("new_page", "New page", "cmd+n", 2),
                3: KeybindAction("toggle_todo", "Toggle todo", "cmd+return", 3),
                4: KeybindAction("slash_command", "Slash command", "slash", 4),
                5: KeybindAction("back", "Go back", "cmd+[", 5),
                6: KeybindAction("forward", "Go forward", "cmd+]", 6),
                7: KeybindAction("command_palette", "Command palette", "cmd+shift+p", 7),
                8: KeybindAction("duplicate", "Duplicate", "cmd+d", 8),
            }
        )
        
        # 11. Messages Mode
        self.modes["messages"] = ModeConfig(
            name="Messages",
            description="Messaging app controls",
            button_map={
                1: KeybindAction("new_message", "New message", "cmd+n", 1),
                2: KeybindAction("send_message", "Send", "return", 2),
                3: KeybindAction("search", "Search conversations", "cmd+f", 3),
                4: KeybindAction("details", "Show details", "cmd+i", 4),
                5: KeybindAction("next_conversation", "Next chat", "cmd+]", 5),
                6: KeybindAction("prev_conversation", "Previous chat", "cmd+[", 6),
            }
        )
        
        # 12. WhatsApp Mode
        self.modes["whatsapp"] = ModeConfig(
            name="WhatsApp",
            description="WhatsApp messaging",
            button_map={
                1: KeybindAction("new_chat", "New chat", "cmd+n", 1),
                2: KeybindAction("send", "Send", "return", 2),
                3: KeybindAction("search", "Search chats", "cmd+f", 3),
                4: KeybindAction("search_in_chat", "Search in chat", "cmd+shift+f", 4),
                5: KeybindAction("archive_chat", "Archive chat", "cmd+shift+e", 5),
                6: KeybindAction("mute_chat", "Mute chat", "cmd+shift+m", 6),
            }
        )
        
        # 13. FaceTime Mode
        self.modes["facetime"] = ModeConfig(
            name="FaceTime",
            description="Video calling controls",
            button_map={
                1: KeybindAction("answer_call", "Answer call", "return", 1),
                2: KeybindAction("decline_call", "Decline call", "d", 2),
                3: KeybindAction("mute_toggle", "Mute/unmute", "m", 3),
                4: KeybindAction("camera_toggle", "Camera on/off", "v", 4),
                5: KeybindAction("end_call", "End call", "escape", 5),
                6: KeybindAction("full_screen", "Full screen", "f", 6),
                7: KeybindAction("effects", "Video effects", "e", 7),
                8: KeybindAction("flip_camera", "Flip camera", "c", 8),
            }
        )
        
        # 15. Notes Mode
        self.modes["notes"] = ModeConfig(
            name="Notes",
            description="Apple Notes",
            button_map={
                1: KeybindAction("new_note",   "New Note",          "cmd+n",       1),
                2: KeybindAction("new_folder", "New Folder",        "cmd+shift+n", 2),
                3: KeybindAction("search",     "Search",            "cmd+f",       3),
                4: KeybindAction("delete",     "Delete Note",       "cmd+delete",  4),
                5: KeybindAction("bold",       "Bold",              "cmd+b",       5),
                6: KeybindAction("italic",     "Italic",            "cmd+i",       6),
                7: KeybindAction("checklist",  "Toggle Checklist",  "cmd+shift+l", 7),
                8: KeybindAction("back",       "Navigate Back",     "cmd+[",       8),
            }
        )

        # 16. Word Mode
        self.modes["word"] = ModeConfig(
            name="Word",
            description="Microsoft Word",
            button_map={
                1: KeybindAction("save",         "Save",          "cmd+s",       1),
                2: KeybindAction("find",         "Find",          "cmd+f",       2),
                3: KeybindAction("bold",         "Bold",          "cmd+b",       3),
                4: KeybindAction("italic",       "Italic",        "cmd+i",       4),
                5: KeybindAction("undo",         "Undo",          "cmd+z",       5),
                6: KeybindAction("redo",         "Redo",          "cmd+shift+z", 6),
                7: KeybindAction("page_up",      "Page Up",       "pageup",      7),
                8: KeybindAction("page_down",    "Page Down",     "pagedown",    8),
            }
        )

        # 17. Outlook Mode
        self.modes["outlook"] = ModeConfig(
            name="Outlook",
            description="Microsoft Outlook",
            button_map={
                1: KeybindAction("new_email",    "New Email",       "cmd+n",       1),
                2: KeybindAction("reply",        "Reply",           "cmd+r",       2),
                3: KeybindAction("reply_all",    "Reply All",       "cmd+shift+r", 3),
                4: KeybindAction("forward",      "Forward",         "cmd+j",       4),
                5: KeybindAction("send",         "Send",            "cmd+return",  5),
                6: KeybindAction("delete",       "Delete",          "delete",      6),
                7: KeybindAction("next_message", "Next Message",    "cmd+]",       7),
                8: KeybindAction("prev_message", "Previous Message","cmd+[",       8),
            }
        )

        # 14. Photo Booth Mode
        self.modes["photo_booth"] = ModeConfig(
            name="Photo Booth",
            description="Apple Photo Booth",
            button_map={
                1: KeybindAction("shutter",    "Take Photo / Record", "space",       1),
                2: KeybindAction("effects",    "Effects",             "cmd+e",       2),
                3: KeybindAction("flip_photo", "Flip Photo",          "cmd+f",       3),
                4: KeybindAction("share",      "Share",               "cmd+shift+i", 4),
                5: KeybindAction("delete",     "Delete",              "delete",      5),
            }
        )

        # 15. ChatGPT Mode
        self.modes["chatgpt"] = ModeConfig(
            name="ChatGPT",
            description="ChatGPT desktop app",
            button_map={
                1: KeybindAction("new_chat",     "New Chat",            "cmd+n",       1),
                2: KeybindAction("send",         "Send Message",        "return",      2),
                3: KeybindAction("new_line",     "New Line",            "shift+return",3),
                4: KeybindAction("search_chats", "Search Chats",        "cmd+k",       4),
                5: KeybindAction("copy_last",    "Copy Last Response",  "cmd+shift+c", 5),
                6: KeybindAction("stop",         "Stop Generating",     "cmd+.",       6),
                7: KeybindAction("close",        "Close Chat",          "cmd+w",       7),
            }
        )

        # 15b. Claude desktop
        self.modes["claude"] = ModeConfig(
            name="Claude",
            description="Claude desktop app",
            button_map={
                1: KeybindAction("new_chat",     "New Chat",            "cmd+n",       1),
                2: KeybindAction("send",         "Send Message",        "return",      2),
                3: KeybindAction("new_line",     "New Line",            "shift+return",3),
                4: KeybindAction("search_chats", "Search Chats",        "cmd+k",       4),
                5: KeybindAction("settings",     "Settings",            "cmd+comma",   5),
                6: KeybindAction("stop",         "Stop",                "escape",      6),
                7: KeybindAction("close",        "Close Chat",          "cmd+w",       7),
            }
        )

        # 16. Phone Mode
        self.modes["phone"] = ModeConfig(
            name="Phone",
            description="Phone call controls",
            button_map={
                1: KeybindAction("answer_call", "Answer call", "return", 1),
                2: KeybindAction("decline_call", "Decline call", "d", 2),
                3: KeybindAction("mute_toggle", "Mute call", "m", 3),
                4: KeybindAction("keypad", "Show keypad", "k", 4),
                5: KeybindAction("contacts", "Contacts", "l", 5),
                6: KeybindAction("recents", "Recents", "r", 6),
                7: KeybindAction("voicemail", "Voicemail", "v", 7),
                8: KeybindAction("end_call", "End call", "escape", 8),
            }
        )
    
    def save(self) -> None:
        """Save configuration to JSON file."""
        try:
            self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                "modes": {},
                "global_shortcuts": self.global_shortcuts
            }
            
            for mode_name, mode_config in self.modes.items():
                config_data["modes"][mode_name] = {
                    "name": mode_config.name,
                    "description": mode_config.description,
                    "button_map": {
                        str(k): asdict(v) for k, v in mode_config.button_map.items()
                    },
                    "combo_map": mode_config.combo_map
                }
            
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def load(self) -> None:
        """Load configuration from JSON file."""
        if not self.CONFIG_FILE.exists():
            logger.info("No existing configuration found, using defaults")
            self.save()
            return
        
        try:
            with open(self.CONFIG_FILE, "r") as f:
                config_data = json.load(f)
            
            self.global_shortcuts = config_data.get("global_shortcuts", {})
            
            for mode_name, mode_data in config_data.get("modes", {}).items():
                if mode_name in self.modes:
                    self.modes[mode_name].button_map = {
                        int(k): KeybindAction(**v) 
                        for k, v in mode_data.get("button_map", {}).items()
                    }
                    self.modes[mode_name].combo_map = mode_data.get("combo_map", {})
            
            self._migrate_browser_dpad_tab_direction()
            self._migrate_anki_suspend_shortcut()
            logger.info(f"Configuration loaded from {self.CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    def _migrate_browser_dpad_tab_direction(self) -> None:
        """Fix older configs that swapped D-pad left/right tab shortcuts."""
        browser = self.modes.get("browser")
        if not browser:
            return
        bmap = browser.button_map
        left = bmap.get(7)
        right = bmap.get(8)
        if not left or not right:
            return
        # Old default: slot 7 = next_tab on D-pad Left, slot 8 = prev_tab on D-pad Right.
        if left.name == "next_tab" and right.name == "prev_tab":
            bmap[7] = KeybindAction(
                "prev_tab", right.description, right.key_sequence, left.button_id
            )
            bmap[8] = KeybindAction(
                "next_tab", left.description, left.key_sequence, right.button_id
            )
            logger.info("Migrated browser D-pad: Left = previous tab, Right = next tab")
            self.save()

    def _migrate_anki_suspend_shortcut(self) -> None:
        """Replace old unsupported '@' display key for Anki suspend with '='."""
        anki = self.modes.get("anki")
        if not anki:
            return
        changed = False
        for bid, act in list(anki.button_map.items()):
            if act.name == "suspend" and act.key_sequence == "@":
                anki.button_map[bid] = KeybindAction(
                    name=act.name,
                    description=act.description,
                    key_sequence="=",
                    button_id=act.button_id,
                    enabled=act.enabled,
                )
                changed = True
        if changed:
            logger.info("Migrated Anki suspend shortcut display key: '@' -> '='")
            self.save()

    def get_mode(self, mode_name: str) -> Optional[ModeConfig]:
        """Get configuration for a specific mode."""
        return self.modes.get(mode_name)
    
    def update_action(self, mode_name: str, button_id: int, action: KeybindAction) -> bool:
        """Update an action for a specific button in a mode."""
        if mode_name not in self.modes:
            return False
        
        self.modes[mode_name].button_map[button_id] = action
        return True


# Global config instance
_config_instance: Optional[KeybindConfig] = None


def get_config() -> KeybindConfig:
    """Get or create the global KeybindConfig instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = KeybindConfig()
        _config_instance.load()
    return _config_instance


def _config_to_gui_dict(cfg: KeybindConfig) -> dict[str, dict[str, str]]:
    """Flatten KeybindConfig into the dict shape used by ``ui/keybind_gui.py``."""
    from ..core.gamepad_button import GamepadButton

    ordered = list(GamepadButton)
    out: dict[str, dict[str, str]] = {}
    for mode_id, mc in cfg.modes.items():
        inner: dict[str, str] = {}
        for bid, act in sorted(mc.button_map.items(), key=lambda x: x[0]):
            if (act.button_id or bid) <= 0 or not act.enabled:
                inner[act.name] = "Unassigned"
                continue
            idx = (act.button_id or bid) - 1
            idx = max(0, min(len(ordered) - 1, idx))
            inner[act.name] = ordered[idx].value
        out[mode_id] = inner
    return out


def load_config() -> dict[str, dict[str, str]]:
    """Load current keybindings as ``{ mode_id: { action_name: button_label } }``."""
    return _config_to_gui_dict(get_config())


def get_default_config() -> dict[str, dict[str, str]]:
    """Defaults only (does not read disk); used by Reset in the keybind editor."""
    return _config_to_gui_dict(KeybindConfig())


def save_config(data: dict[str, dict[str, str]]) -> None:
    """Persist GUI-shaped dict back into :class:`KeybindConfig` and save JSON."""
    from ..core.gamepad_button import GamepadButton

    cfg = get_config()
    for mode_id, action_to_label in data.items():
        if mode_id not in cfg.modes:
            continue
        mc = cfg.modes[mode_id]
        for bid, act in list(mc.button_map.items()):
            if act.name not in action_to_label:
                continue
            label = action_to_label[act.name]
            if label == "Unassigned":
                mc.button_map[bid] = KeybindAction(
                    name=act.name,
                    description=act.description,
                    key_sequence=act.key_sequence,
                    button_id=0,
                    enabled=False,
                )
                continue
            btn_id = next(
                (i + 1 for i, b in enumerate(GamepadButton) if b.value == label),
                act.button_id or bid,
            )
            mc.button_map[bid] = KeybindAction(
                name=act.name,
                description=act.description,
                key_sequence=act.key_sequence,
                button_id=btn_id,
                enabled=act.enabled,
            )
    cfg.save()


def load_hotkey_list() -> dict[str, dict[str, dict[str, str]]]:
    """Return per-mode action rows for the read-only hotkey list UI.

    Shape: ``{ mode_id: { action_name: {"button": "…", "keys": "…"} } }``.
    ``button`` is the gamepad control (same labels as the keybind editor);
    ``keys`` is the macOS shortcut string sent when that button fires.
    """
    cfg = get_config()
    button_by_mode = _config_to_gui_dict(cfg)
    out: dict[str, dict[str, dict[str, str]]] = {}
    for mode_id, mc in cfg.modes.items():
        inner: dict[str, dict[str, str]] = {}
        labels = button_by_mode.get(mode_id, {})
        for _bid, act in sorted(mc.button_map.items(), key=lambda x: x[0]):
            inner[act.name] = {
                "button": labels.get(act.name, "Unassigned"),
                "keys": act.key_sequence,
            }
        out[mode_id] = inner
    return out


def format_hotkey_list_text() -> str:
    """Return a terminal-friendly multiline hotkey list."""
    rows_by_mode = load_hotkey_list()
    lines: list[str] = []
    lines.append("ButtonBridge hotkey list")
    lines.append("=" * 24)

    for mode_id in sorted(rows_by_mode):
        mode_label = mode_id.replace("_", " ").title()
        lines.append("")
        lines.append(f"[{mode_label}]")

        rows = rows_by_mode[mode_id]
        if not rows:
            lines.append("  (no actions)")
            continue

        action_w = max(6, max(len(a) for a in rows.keys()))
        button_w = max(6, max(len(str(v.get("button", ""))) for v in rows.values()))
        header = (
            f"  {'Action'.ljust(action_w)}  "
            f"{'Button'.ljust(button_w)}  Keys"
        )
        lines.append(header)
        lines.append("  " + "-" * max(12, len(header) - 2))

        for action_name, info in rows.items():
            button = str(info.get("button", "Unassigned"))
            keys = str(info.get("keys", ""))
            lines.append(
                f"  {action_name.ljust(action_w)}  {button.ljust(button_w)}  {keys}"
            )

    return "\n".join(lines)
