# Contributing to StopSlop

Thank you for helping improve StopSlop. The project prioritizes local execution, explainable writing-pattern feedback, privacy, accessibility, and respectful upstream attribution.

## Before opening a pull request

Please read `docs/StopSlop_Technical_Specification.md`, `docs/architecture.md`, and `docs/privacy.md`. A change should preserve the local-only Version 1 boundary unless the product specification is updated first.

Pull requests should explain the user problem, the implementation boundary, how the change was tested, and whether it affects the normalized analysis contract. Changes to the contract require fixture updates and a documented compatibility decision.

## Changes that need special review

Changes that add network access, telemetry, raw-text persistence, automatic draft restoration, file upload, an external runtime, a new detector, or authorship-related language require explicit product and privacy review. Do not add secrets, signing certificates, API keys, or private user data to the repository.

## Development expectations

Use clear names, small modules, deterministic tests, and safe error messages. Keep StopSlop-specific code outside `vendor/sloptrim`. Preserve upstream files and attribution when updating the vendored detector.

## Pull request checklist

- The change is scoped to the issue and does not add an undeclared cloud dependency.
- Tests cover new behavior and failure paths.
- No raw sample text appears in logs, fixtures intended for release, or error messages.
- Documentation and screenshots are updated when the user experience changes.
- Attribution and licence files are preserved.
- The application limitation statement remains visible and accurate.
