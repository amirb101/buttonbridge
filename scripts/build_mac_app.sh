#!/usr/bin/env bash
# Build dist/ButtonBridge.app with PyInstaller (macOS, same machine you develop on).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python3 ]]; then
  echo "→ No .venv found. Run ./scripts/run.sh once to create it, then try again."
  exit 1
fi

echo "→ Installing build deps …"
.venv/bin/python3 -m pip install -q -r requirements-build.txt

echo "→ Running PyInstaller …"
.venv/bin/pyinstaller --noconfirm --clean "${ROOT}/ButtonBridge.spec"

echo "→ Done: ${ROOT}/dist/ButtonBridge.app"
echo "  Zip that folder or the .app and share it. See docs/beginner-installation-guide.md for setup steps."
