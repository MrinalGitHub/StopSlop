# StopSlop

<p align="center">
  <a href="https://www.kritrim-ai.com/" title="Visit Kritrim-ai.com">
    <img src="assets/kritrim-k-logo-transparent.png" alt="Kritrim-ai logo" width="96" /><br />
    <strong>Kritrim-ai.com</strong>
  </a>
</p>

<p align="center"><strong>StopSlop by <a href="https://www.kritrim-ai.com/">Kritrim-ai</a></strong><br />Local writing-pattern review for macOS</p>

<p align="center">
  <img src="assets/stopslop-product-preview.gif" alt="Animated StopSlop product preview" width="720" />
</p>

> **Release status:** Version 2.0.2 is an Apple Silicon test build and is currently unsigned. A normal public macOS release requires Developer ID signing and Apple notarization; until that is completed, macOS Gatekeeper may reject the downloaded application.

**StopSlop** is a privacy-first writing-pattern review application for macOS. It runs locally on the user’s Mac, analyzes prose without sending text to a server, and presents a score, severity band, metrics, and named writing-pattern findings.

StopSlop builds on [Sloptrim](https://github.com/seyedehsanhadi/sloptrim), a local detector for AI-writing patterns. StopSlop adds a polished desktop interface, local application packaging, accessibility-minded result presentation, and a downloadable macOS DMG.

> StopSlop reviews writing signals. It does not identify an author, prove AI use, or support academic, employment, legal, disciplinary, or other high-stakes decisions.

## Product status

**Version 2.0.2 is the enriched Apple Silicon test build:** a ready-made Apple Silicon macOS `.dmg` published under GitHub Releases. The repository currently contains the product specification, desktop implementation, local analyzer sidecar build path, and DMG packaging configuration. The release artifact will require no cloud account, hosted API, database, or network connection for core analysis.

The Version 2.0.2 test DMG is available from the [pre-release GitHub page](https://github.com/MrinalGitHub/StopSlop/releases/tag/v2.0.2).

| Property | Version 2.0.2 test build |
|---|---|
| Product type | Native-feeling local macOS desktop application |
| Distribution | Downloadable `.dmg` from GitHub Releases |
| Primary architecture | Tauri interface with a bundled local detector sidecar |
| Supported hardware | Apple Silicon Macs first |
| Analysis mode | Offline by default |
| Data retention | Raw submitted text is not intentionally persisted |
| Cloud dependency | None |
| Accounts | None |
| Upstream engine | Pinned and attributed Sloptrim source |

## Installation

The free installation flow is:

> **Certificate note:** This free build is unsigned and not notarized by Apple. Verify the SHA-256 checksum, then use the one-time macOS **Open** approval if prompted before launching.

1. Download the **StopSlop 2.0.2 Apple Silicon DMG** from the [GitHub pre-release page](https://github.com/MrinalGitHub/StopSlop/releases/tag/v2.0.2).
2. Download the matching `.sha256` file and verify the DMG before opening it:

   ```bash
   shasum -a 256 StopSlop_2.0.2_aarch64.dmg
   cat StopSlop_2.0.2_aarch64.dmg.sha256
   ```

   The two SHA-256 values must match exactly.
3. Open the DMG and drag StopSlop into the Applications folder.
4. On the first launch, **Control-click or right-click StopSlop.app and choose Open**, then confirm Open. This is required because the free build is not signed or notarized by Apple.
5. If macOS still blocks the app after you have verified the checksum and trust the downloaded source, remove the quarantine attribute and launch it:

   ```bash
   xattr -dr com.apple.quarantine /Applications/StopSlop.app
   open /Applications/StopSlop.app
   ```

6. Paste prose and choose **Analyse writing**.

This free release includes richer explainable signals, a visible 8,000-word capacity meter, corrected local analysis execution, a native icon, and Apple Silicon support. It does not require an Apple Developer membership, cloud account, hosted API, database, or internet connection for core analysis. Developers can reproduce the build locally by following [`docs/release.md`](docs/release.md).

The product preview above illustrates the intended StopSlop experience: local, private writing review with a clear score, metrics, findings, and revision-oriented workflow.

## Planned user flow

1. The user opens StopSlop from the Applications folder.
2. The user pastes or types prose into the editor.
3. StopSlop displays the local word count and enables analysis when the minimum input length is met.
4. The bundled detector runs locally and returns a normalized result.
5. The interface presents the score, severity band, metrics, and findings in plain language.
6. The user can clear the draft and result at any time.

## Free distribution and security note

StopSlop is distributed as an unsigned, open-source Apple Silicon test build so that the project can remain free without the Apple Developer Program fee. macOS Gatekeeper may warn or block the first launch. Only bypass the warning after downloading from the official GitHub release, verifying the published SHA-256 checksum, and deciding that you trust the source. A future Developer ID-signed and notarized release would remove this manual step but is not required for local development.

## Privacy model

StopSlop is designed so that analysis does not require an internet connection. The application must not send raw prose to a remote endpoint, log submitted text, store drafts in a database, or include raw text in telemetry. The implementation must preserve this behavior in development, packaged builds, crash handling, and documentation.

## Repository layout

```text
StopSlop/
├── app/                         # Tauri desktop application, added during implementation
├── assets/                      # Application icons, logo variants, and release artwork
├── docs/                        # Product, architecture, privacy, and release specifications
├── src/stopslop_engine/         # Local adapter and normalized analysis contract
├── tests/                       # Contract, adapter, and packaging tests
├── vendor/sloptrim/             # Pinned upstream source or release snapshot
├── .github/workflows/           # Continuous integration and release workflows
├── LICENSE                      # StopSlop project licence
├── NOTICE                       # Upstream and third-party notices
├── THIRD_PARTY_NOTICES.md       # Dependency and attribution record
├── pyproject.toml               # Local adapter tooling
└── README.md
```

## Development documentation

The detailed specification is in [`docs/StopSlop_Technical_Specification.md`](docs/StopSlop_Technical_Specification.md). The implementation decisions are described in [`docs/architecture.md`](docs/architecture.md), while privacy requirements are defined in [`docs/privacy.md`](docs/privacy.md).

## Attribution

> **Detection engine credit:** StopSlop builds on Sloptrim by Seyed Ehsan Hadi, licensed under Apache License 2.0. StopSlop adds the user interface, local adapter, packaging, and distribution configuration. The upstream author does not endorse StopSlop.

Applicable upstream licence, notice, and citation materials must remain in this repository and in release artifacts. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Brand

The application uses Kritrim-ai branding with permission from the project owner. The public brand reference is [Kritrim-ai](https://www.kritrim-ai.com/). The transparent Kritrim-ai mark should be placed in the application About view and in other appropriate product surfaces without reducing readability or suggesting upstream endorsement.

## Contributing

Contributions are welcome after the local contract and privacy requirements are understood. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Changes that introduce network access, raw-text persistence, opaque telemetry, or unsupported authorship claims are out of scope for the first release.

## Licence

StopSlop project code is intended to be released under Apache License 2.0 unless the repository owner selects another compatible open-source licence before the first public release. Upstream Sloptrim materials remain subject to their original licence and notices.

