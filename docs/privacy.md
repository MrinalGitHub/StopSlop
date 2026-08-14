# StopSlop Privacy and Security Requirements

## Privacy promise

StopSlop Version 1 is designed to analyze prose locally on the user’s Mac. Core analysis must not require a network connection, user account, cloud service, or remote API. The application should communicate this promise plainly without claiming that local software can eliminate every risk associated with the operating system or other applications running on the machine.

## Data inventory

| Data | Purpose | Storage in Version 1 | Network transmission |
|---|---|---|---|
| Pasted prose | Local analysis input. | In memory during the active session; temporary storage only if required by the upstream CLI, followed by deletion. | None for core analysis. |
| Word count | Local UI feedback. | In memory. | None. |
| Score and findings | Local result presentation. | In memory unless the user explicitly exports or copies it. | None. |
| Application settings | Future local preferences. | Only if required, using a documented local settings file. | None. |
| Crash diagnostics | Not included by default. | None. | None. |
| Analytics identifiers | Not collected. | None. | None. |

## Required controls

1. The application must operate correctly with network access disabled.
2. The application must not send raw prose, score results, or findings to a remote endpoint.
3. The application must not log raw submitted text, text fragments, arbitrary detector output, or clipboard contents.
4. Error messages must use controlled categories and must not echo user text.
5. If a temporary file is required, it must be created in an application-controlled temporary directory with restrictive permissions and removed after analysis.
6. The detector process must have an execution timeout and a bounded output size.
7. The UI must clear active text and results when the user selects Clear.
8. The application must not silently restore sensitive drafts after restart unless an explicit future setting is added and clearly disclosed.
9. Telemetry, analytics, remote error monitoring, and update checks must remain disabled in Version 1 unless separately designed, opt-in, and documented.
10. Release documentation must state exactly what the application does and does not store.

## Threat model

The primary threats are accidental transmission, accidental persistence, information leakage through logs or crash reports, execution of an unexpected bundled file, and user confusion about the meaning of the score.

The application should reduce these risks through local-only execution, fixed bundled paths, strict process invocation, input bounds, output validation, sanitized errors, no analytics, and prominent limitations. The detector should not be given arbitrary shell commands or user-controlled executable paths.

## Verification checklist

Before each public release, the maintainer should verify the following:

- Disable network access and analyze a representative sample.
- Inspect the application and detector processes for unexpected network connections.
- Search application logs and temporary directories for the test prose.
- Confirm that clearing the workspace removes the active text and result.
- Kill the detector process and confirm the UI displays a safe recoverable error.
- Feed malformed detector output through the adapter and confirm it is rejected safely.
- Test input containing Unicode, punctuation, long lines, and newlines.
- Install and run the DMG on a clean Apple Silicon Mac.
- Review release notes for privacy, attribution, and limitations language.

## User-facing privacy language

The application may use wording similar to the following:

> **Local and private by default.** StopSlop analyzes your text on this Mac. Core analysis does not require an internet connection, and StopSlop does not intentionally send your prose to a server or retain it as a cloud record. StopSlop reports writing patterns; it does not identify authorship or prove that artificial intelligence was used.

This language must be kept consistent across the main screen, Privacy view, README, and release notes.
