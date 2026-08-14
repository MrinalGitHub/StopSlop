# StopSlop Roadmap

## Milestone 0 — Repository foundation

- Public GitHub repository created.
- Product and technical specification committed.
- Upstream Sloptrim source pinned under `vendor/sloptrim`.
- Licence, notice, attribution, privacy, and contribution documents added.

## Milestone 1 — Engine contract

- Verify the current upstream CLI behavior.
- Implement the local adapter and normalized response schema.
- Add fixture-based tests for score, metrics, findings, malformed output, and timeouts.
- Confirm that adapter errors never expose submitted prose.

## Milestone 2 — Desktop MVP

- Scaffold the Tauri application.
- Add the editor, word count, analyze action, clear action, score view, findings view, and required information pages.
- Add Kritrim-ai branding and a restrained visual system.
- Connect the desktop UI to the local sidecar.

## Milestone 3 — Packaging validation

- Bundle the detector runtime and adapter.
- Produce an unsigned DMG.
- Test installation and offline analysis on a clean Apple Silicon Mac.
- Verify that the application does not rely on globally installed developer tools.

## Milestone 4 — Public release readiness

- Add release documentation and screenshots.
- Add GitHub Actions for tests and packaging.
- Add Apple Developer signing and notarization when credentials are available.
- Publish the first tagged GitHub Release with the DMG and checksums.

## Deferred work

Cloud analysis, accounts, history synchronization, online analytics, browser extensions, document uploads, Windows builds, Intel Mac support, mobile applications, and additional detector engines are deferred until the local release is stable and user feedback justifies expansion.
