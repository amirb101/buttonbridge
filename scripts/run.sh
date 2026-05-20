#!/usr/bin/env bash
# Run ButtonBridge from the repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# PyObjC wheels lag behind bleeding-edge Homebrew Pythons — prefer 3.12/3.13 if available.
pick_python() {
  if [[ -n "${PYTHON:-}" ]]; then
    echo "$PYTHON"
    return
  fi
  local c
  for c in python3.13 python3.12 python3.11 python3.10; do
    if command -v "$c" &>/dev/null; then
      echo "$c"
      return
    fi
  done
  echo "python3"
}

PYTHON_CMD="$(pick_python)"
VER="$("$PYTHON_CMD" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"

IFS='.' read -r MAJOR MINOR <<< "${VER}"
if [[ "$MAJOR" -ne 3 ]] || [[ "$MINOR" -gt 13 ]]; then
  echo "→ This repo needs Python 3.10–3.13 for PyObjC wheels (you have ${VER})."
  echo "  Install 3.12 and recreate the venv, e.g.:"
  echo "    brew install python@3.12"
  echo "    rm -rf .venv"
  echo "    /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv   # Apple Silicon"
  echo "    /usr/local/opt/python@3.12/bin/python3.12 -m venv .venv     # Intel Homebrew"
  echo "  Or: PYTHON=/path/to/python3.12 ./scripts/run.sh"
  exit 1
fi

# Drop a venv that was created with an older run (e.g. Python 3.14 — no PyObjC wheels).
if [[ -d .venv ]]; then
  VMINOR="$(.venv/bin/python3 -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo 99)"
  if [[ "$VMINOR" -gt 13 ]]; then
    echo "→ Removing .venv (was Python 3.${VMINOR}; PyObjC needs ≤3.13) …"
    rm -rf .venv
  fi
fi

if [[ ! -d .venv ]]; then
  echo "→ Creating .venv with ${PYTHON_CMD} (${VER}) …"
  "$PYTHON_CMD" -m venv .venv
fi

VPY="${ROOT}/.venv/bin/python3"
VPIP="${ROOT}/.venv/bin/python3"  # same; always use python -m pip

echo "→ Upgrading pip …"
"$VPY" -m pip install -q --upgrade pip

echo "→ Installing deps …"
"$VPY" -m pip install -r requirements.txt

echo "→ Starting app (Ctrl+C to stop) …"
exec "$VPY" -m buttonbridge "$@"
