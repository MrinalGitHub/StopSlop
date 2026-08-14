# StopSlop macOS Release Procedure

## Release artifact

A public release should contain a versioned macOS DMG for the supported architecture, a SHA-256 checksum, release notes, and a link to the source commit. The DMG should contain the StopSlop application in a conventional drag-to-Applications layout.

## Build sequence

The desktop build is expected to run from `app/` after the Rust and Node toolchains are installed:

```bash
npm install
npm run build
npm run tauri build -- --bundles dmg
```

The exact Tauri CLI command may change with the selected Tauri major version. The maintainer must verify the command against the installed CLI before publishing a release.

## Pre-release checks

Before creating a public tag, run the Python adapter tests, verify that the bundled detector is present, build the application, install the DMG on a clean Apple Silicon Mac, disable networking, analyze a representative sample, and inspect the application for unexpected logs or network activity.

The release reviewer should also confirm that the README, Privacy view, Credits view, Limitations view, `NOTICE`, `THIRD_PARTY_NOTICES.md`, and upstream licence materials are included and consistent.

## Signing and notarization

The first internal DMG may be unsigned. Public distribution should use Apple Developer signing and notarization when the repository owner has configured the required credentials. Signing identities, certificates, API keys, and provisioning files must remain outside Git and must be supplied through protected CI secrets.

The release workflow must never print signing credentials or include them in build logs. If signing is unavailable, the release notes must clearly explain that macOS may show a Gatekeeper warning and should provide a safe verification path.

## Versioning

Use semantic version tags such as `v0.1.0`. The application version in `app/src-tauri/tauri.conf.json`, the Python package version, release notes, and DMG filename should agree. Any change to the normalized response contract requires a documented schema compatibility decision.

## GitHub release contents

Each release should include:

- The DMG artifact.
- A SHA-256 checksum file.
- A short summary of user-visible changes.
- Privacy and offline-operation notes.
- Known limitations.
- Upstream attribution and licence information.
- The exact source commit and supported macOS architecture.
