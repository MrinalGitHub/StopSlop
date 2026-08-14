#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT_DIR/app"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required to build StopSlop." >&2
  exit 1
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "Rust and Cargo are required to build the Tauri application." >&2
  exit 1
fi

cd "$APP_DIR"
npm install --no-audit --no-fund
npm run tauri build -- --bundles dmg

printf '%s\n' "DMG build completed. Check app/src-tauri/target/release/bundle/dmg/."
