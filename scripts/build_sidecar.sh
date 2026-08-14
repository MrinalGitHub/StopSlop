#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required to build the local analyzer." >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [ -x "$ROOT_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

if ! "$PYTHON_BIN" -c 'import PyInstaller' >/dev/null 2>&1; then
  echo "PyInstaller is required. Install it in .venv with: python3 -m venv .venv && .venv/bin/python -m pip install pyinstaller" >&2
  exit 1
fi

TARGET_TRIPLE="$(rustc --print host-tuple)"
"$PYTHON_BIN" -m PyInstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name stopslop-analyse \
  --paths src \
  --add-data "vendor/sloptrim:vendor/sloptrim" \
  src/stopslop_engine/cli.py

mkdir -p app/src-tauri/binaries
rm -f app/src-tauri/binaries/stopslop-analyse-*
mv dist/stopslop-analyse "app/src-tauri/binaries/stopslop-analyse-${TARGET_TRIPLE}"
chmod +x "app/src-tauri/binaries/stopslop-analyse-${TARGET_TRIPLE}"

printf '%s\n' "Built app/src-tauri/binaries/stopslop-analyse-${TARGET_TRIPLE}"
