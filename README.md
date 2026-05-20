# ButtonBridge

**Turn a Bluetooth gamepad into a Mac keyboard remote.**

ButtonBridge lives in your menu bar and maps controller buttons to keyboard shortcuts — automatically switching mappings based on whichever app is in the foreground. Open Spotify and get media controls. Switch to a browser and get tab navigation. No window, no fuss.

**Supported controllers:** anything macOS recognises as a Game Controller (8BitDo Micro, Xbox, DualSense, and more).

---

## Install

### Option A — Pre-built app (recommended)

Build the `.app` once and it runs on any Mac without Python:

```bash
./scripts/build_mac_app.sh
```

Output: `dist/ButtonBridge.app`. Drag it into **Applications**, then follow the [setup steps](#setup) below.

> For sharing with others: zip `ButtonBridge.app` and distribute the archive. See [docs/beginner-installation-guide.md](docs/beginner-installation-guide.md) for a step-by-step recipient guide.

### Option B — Run from source

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m buttonbridge
# or: ./scripts/run.sh
```

Input backend override (source runs):

```bash
# Apple GameController backend (recommended for 8BitDo Micro troubleshooting)
BUTTONBRIDGE_INPUT_BACKEND=gc ./scripts/run.sh --verbose

# Force pygame/SDL backend
BUTTONBRIDGE_INPUT_BACKEND=pygame ./scripts/run.sh --verbose
```

GameController profile override:

```bash
BUTTONBRIDGE_INPUT_BACKEND=gc BUTTONBRIDGE_GC_PROFILE=physical ./scripts/run.sh --verbose
# BUTTONBRIDGE_GC_PROFILE: auto | physical | extended | micro
```

---

## Setup

### 1. Pair your controller

**System Settings → Bluetooth** — put the pad in pairing mode and connect it. Confirm it appears under **System Settings → Game Controllers**.

If the app shows "Not Connected", try switching the controller's input mode (e.g. the X/S switch on an 8BitDo) so macOS recognises it as a standard gamepad.

### 2. Grant Accessibility permission

ButtonBridge sends keystrokes on your behalf, which requires one permission:

1. Launch `ButtonBridge.app` — the 🎮 icon should appear in your menu bar.
2. Open **System Settings → Privacy & Security → Accessibility**.
3. Enable **ButtonBridge** (click **+** → **Applications** → **ButtonBridge** if it isn't listed yet).

> Running from source? Add the Python interpreter to that list instead. The menu bar has an **Open Accessibility Settings…** shortcut for quick access.

### 3. Calibrate (first run)

Click the menu bar icon → **Calibrate Controller…** and press each button when prompted. This maps the physical buttons on your specific pad to ButtonBridge's internal layout.

---

## How it works

ButtonBridge polls the frontmost app's bundle identifier and routes button presses through the matching **mode**. If no mode matches, **Global** mode handles the input.

| Mode | Activates for |
|------|--------------|
| **Global** | Fallback — any unmatched app |
| **Browser** | Chrome, Safari, Arc, Firefox, Edge, Brave, Opera, Vivaldi, Orion, Zen, Comet |
| **Spotify** | Spotify |
| **Apple Music** | Apple Music |
| **Anki** | Anki |
| **Obsidian** | Obsidian |
| **Notion** | Notion |
| **Notes** | Apple Notes |
| **VS Code** | Visual Studio Code |
| **Cursor** | Cursor |
| **Claude** | Claude desktop app |
| **Word** | Microsoft Word |
| **Outlook** | Microsoft Outlook |
| **Finder** | Finder |
| **Photo Booth** | Photo Booth |
| **ChatGPT** | ChatGPT desktop app |
| **Preview** | Preview |
| **Messages** | Messages |
| **WhatsApp** | WhatsApp |
| **FaceTime** | FaceTime |
| **Phone** | Phone |

---

## Keybindings

Click **Hotkey List…** in the menu bar to see your current mappings.

- If ButtonBridge is running from a terminal, the list prints in that terminal.
- If launched from the `.app` (Finder), ButtonBridge opens Terminal and prints the list there.

To edit mappings, run:

```bash
python -m buttonbridge --buttonbridge-keybind-gui
```

Or use the keybinding editor launched at first startup. Mappings are saved to `~/.buttonbridge/keybindings.json`.

Each mode has a list of **actions** (e.g. `next_track`, `new_tab`). You assign a gamepad button to each action. Unassigned actions do nothing.

---

## Mode reference

### Global
Spotlight · Screenshot (region) · Mission Control · Play/Pause (Spotify) · Lock screen · Volume up/down · Mute — other actions (Obsidian, Spotify, spaces) are available in the keybinding editor

### Browser
New tab · Close tab · Reopen closed tab · Back/Forward · Prev/Next tab · Scroll · Tab search · Address bar · Bookmark

### Spotify
Play/Pause · Next/Prev track · Volume · Shuffle · Repeat · Like/Unlike · Search

### Apple Music
Play/Pause · Next/Prev track · Volume · Love · Shuffle · Search

### Anki
Show answer · Again / Hard / Good / Easy · Undo · Bury · Suspend

### Obsidian
Command palette · Quick switcher · Daily note · Toggle checklist · Insert template · Graph view · Navigate back/forward · Toggle sidebar · Search · New note

> Obsidian actions that send custom chords require matching hotkeys in **Obsidian → Settings → Hotkeys**. Suggested mappings are in the keybinding editor.

### Notion
Quick find · New page · Toggle todo · Slash command · Back/Forward · Command palette

### Photo Booth
Take photo / record · Effects · Flip photo · Share · Delete

### ChatGPT
New chat · Send · New line · Search chats · Copy last response · Stop generating · Close


### Notes
New note · New folder · Search · Delete · Bold · Italic · Toggle checklist · Navigate back

### Word
Save · Find · Bold · Italic · Undo · Redo · Page up/down · Zoom in/out · Word count · New document

### Outlook
New email · Reply · Reply all · Forward · Send · Delete · Search · Next/Prev message · Mark as read

### VS Code
Command palette · Quick open · Toggle terminal · Go to definition · Find · Save · New file · Close tab

### Cursor
Same defaults as VS Code (separate mode so you can remap per editor).

### Claude
New chat · Send · New line · Search chats · Settings · Stop · Close chat

### Finder
New folder · Quick Look · Get Info · Search · Back/Forward · Move to Trash

### Preview
Next/Prev page · Zoom in/out · Actual size · Rotate · Share

### Messages
New message · Send · Next/Prev conversation · Search · Chat info

### WhatsApp
New chat · Send · Search · Archive · Mute

### FaceTime / Phone
Answer · Decline · End call · Toggle mute · Toggle camera

---

## Adding a mode

1. Create `buttonbridge/modes/yourapp_mode.py` — subclass `ConfigurableMode`.
2. Add the bundle ID to `buttonbridge/constants.py` → `BundleID`.
3. Register it in `buttonbridge/main.py` → `_build_registry()`.
4. Add default keybindings in `buttonbridge/config/keybind_config.py`.

To find any app's bundle ID:

```bash
mdls -name kMDItemCFBundleIdentifier /Applications/YourApp.app
```

---

## Project structure

```
buttonbridge/
├── __main__.py         Entry point; startup dialog
├── main.py             Controller manager, mode registry
├── constants.py        Bundle IDs, button indices, timing
├── controller/         GameController input backend
├── detection/          Frontmost-app polling
├── routing/            Mode switching logic
├── executors/          Keystroke / AppleScript execution
├── modes/              One file per app mode
├── config/             Keybinding persistence
└── ui/                 Menu bar, keybind GUI
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Not Connected" in menu | Re-pair Bluetooth; try the controller's mode switch; check System Settings → Game Controllers |
| Button presses do nothing | Verify Accessibility permission is granted to **ButtonBridge** (not Terminal or Python) |
| Face buttons (A/B/X/Y) fire together in D mode | Try Apple GameController backend (`BUTTONBRIDGE_INPUT_BACKEND=gc`), test profile override (`BUTTONBRIDGE_GC_PROFILE=physical`), or switch controller mode (X/S) |
| Wrong mode activates | Check bundle ID in `constants.py`; run `mdls -name kMDItemCFBundleIdentifier /path/to/App.app` to confirm |
| App blocked by macOS | Right-click → **Open** on first launch; or Privacy & Security → **Open Anyway** |
| Keybindings reset | Check `~/.buttonbridge/keybindings.json` exists and is valid JSON |

---

## License

MIT
