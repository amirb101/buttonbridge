# Beginner installation guide (macOS)

This guide is for **end users** who receive a pre-built **ButtonBridge.app** (no Xcode, Homebrew, or Python required). It also covers what the **developer** does once to produce that app.

---

## For the developer (one-time build)

1. On your Mac, from the repository root:
   ```bash
   ./scripts/run.sh          # ensures .venv + dependencies exist
   ./scripts/build_mac_app.sh
   ```
2. You get `dist/ButtonBridge.app`.
3. **Zip** `ButtonBridge.app` (right-click → Compress). Zipping avoids odd quarantine behaviour on some file hosts.
4. Share the zip (AirDrop, cloud storage, etc.).

**Code signing:** the build script produces an **unsigned** app. That is normal for informal distribution: the recipient uses **Right-click → Open** the first time. For public distribution, use an Apple Developer ID certificate and notarization.

---

## For the recipient (first-time setup)

### 1. Unzip and move to Applications

- Unzip the archive → drag **ButtonBridge.app** into **Applications**.

### 2. First launch (Gatekeeper)

Because the app is not from the Mac App Store, macOS may block a double-click:

- **Right-click** **ButtonBridge** → **Open** → confirm **Open**.

Alternatively: **System Settings → Privacy & Security** → find the blocked-app message → **Open Anyway**.

### 3. Accessibility (required)

ButtonBridge sends keyboard shortcuts; macOS must allow it:

1. Launch **ButtonBridge** once (a menu bar icon should appear shortly).
2. Open **System Settings → Privacy & Security → Accessibility**.
3. Enable **ButtonBridge** (use **+** if needed: **Applications** → **ButtonBridge**).

If controller buttons do nothing, recheck this list — the wrong binary is the most common cause.

### 4. Bluetooth controller

- **System Settings → Bluetooth** — pair the gamepad.
- Optional: **System Settings → Game Controllers** — confirm the device appears.

### 5. Optional: keybindings

On first launch, ButtonBridge may offer to open the keybinding editor. Mappings can be changed there, or defaults can be used as-is.

Settings are stored under the user’s home folder, typically:

`~/.buttonbridge/keybindings.json`

---

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| “App is damaged” / will not open | Right-click → **Open**, or **Privacy & Security** → **Open Anyway**. Ensure the zip downloaded completely. |
| No menu bar icon | Check **Activity Monitor** for **ButtonBridge**; quit and relaunch. |
| Controller not detected | Re-pair Bluetooth; try the controller’s **mode** switch (e.g. X / S); restart the Mac once. |
| Keystrokes have no effect | Enable **ButtonBridge** (the app) under **Accessibility**, not only Terminal. |

---

## Fallback: run from source

If the `.app` does not run on a particular Mac, the same project can be run from a terminal using **Python 3.10–3.13** and `./scripts/run.sh` after cloning or copying the repository folder. See the main [README](../README.md) for developer setup.
