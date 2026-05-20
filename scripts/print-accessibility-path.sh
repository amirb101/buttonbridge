#!/usr/bin/env bash
# Print the Python binary path to add under System Settings → Accessibility.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -x "${ROOT}/.venv/bin/python3" ]]; then
  realpath "${ROOT}/.venv/bin/python3"
else
  echo "No ${ROOT}/.venv/bin/python3 — create a venv first; using python3 in PATH:" >&2
  realpath "$(command -v python3)"
fi
