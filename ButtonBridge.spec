# -*- mode: python ; coding: utf-8 -*-
# Build: ./scripts/build_mac_app.sh   → dist/ButtonBridge.app
block_cipher = None

a = Analysis(
    ["packaging/run_app.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=[
        "rumps",
        "pygame",
        "objc",
        "Foundation",
        "AppKit",
        "Cocoa",
        "Quartz",
        "CoreGraphics",
        "ApplicationServices",
        "GameController",
        "Metal",
        "CoreBluetooth",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ButtonBridge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ButtonBridge",
)

app = BUNDLE(
    coll,
    name="ButtonBridge.app",
    icon=None,
    bundle_identifier="dev.buttonbridge.app",
    info_plist={
        "CFBundleName": "ButtonBridge",
        "CFBundleDisplayName": "ButtonBridge",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "0.1.0",
        "LSMinimumSystemVersion": "12.0",
        "NSHighResolutionCapable": True,
        "NSBluetoothAlwaysUsageDescription": "ButtonBridge uses Bluetooth to talk to your game controller.",
    },
)
