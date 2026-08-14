#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$ROOT_DIR/app"
IDENTITY="${APPLE_SIGNING_IDENTITY:-}"
NOTARY_PROFILE="${APPLE_NOTARY_PROFILE:-}"

if [[ -z "$IDENTITY" ]]; then
  echo "APPLE_SIGNING_IDENTITY is required, for example: Developer ID Application: Your Name (TEAMID)" >&2
  exit 2
fi
if [[ -z "$NOTARY_PROFILE" ]]; then
  echo "APPLE_NOTARY_PROFILE is required for xcrun notarytool." >&2
  exit 2
fi
if ! command -v codesign >/dev/null 2>&1 || ! command -v xcrun >/dev/null 2>&1 || ! command -v hdiutil >/dev/null 2>&1; then
  echo "Xcode command-line tools are required." >&2
  exit 2
fi
if ! xcrun stapler help >/dev/null 2>&1; then
  echo "The full Xcode installation is required because xcrun stapler is unavailable." >&2
  exit 2
fi
if ! security find-identity -v -p codesigning | grep -F "$IDENTITY" >/dev/null 2>&1; then
  echo "The requested Apple signing identity is not installed in the current Keychain." >&2
  exit 2
fi

cd "$ROOT_DIR"
./scripts/build_sidecar.sh
cd "$APP_DIR"
npm install --no-audit --no-fund
npm run tauri build -- --bundles app

APP_PATH="$APP_DIR/src-tauri/target/release/bundle/macos/StopSlop.app"
OUT_DIR="$APP_DIR/src-tauri/target/release/bundle/dmg"
DMG_PATH="$OUT_DIR/StopSlop_signed_aarch64.dmg"
mkdir -p "$OUT_DIR"

codesign --force --options runtime --timestamp --sign "$IDENTITY" "$APP_PATH/Contents/MacOS/stopslop-analyse"
codesign --force --options runtime --timestamp --sign "$IDENTITY" "$APP_PATH/Contents/MacOS/stopslop"
codesign --force --options runtime --timestamp --sign "$IDENTITY" "$APP_PATH"
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

rm -f "$DMG_PATH"
hdiutil create -volname "StopSlop" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_PATH"
xcrun notarytool submit "$DMG_PATH" --keychain-profile "$NOTARY_PROFILE" --wait
xcrun stapler staple "$DMG_PATH"
hdiutil verify "$DMG_PATH"

echo "Signed and notarized DMG created at: $DMG_PATH"
