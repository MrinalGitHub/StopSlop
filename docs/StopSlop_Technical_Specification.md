# StopSlop Technical Specification

**Product:** StopSlop by Kritrim-ai  
**Release target:** Local-only macOS application distributed as a GitHub DMG  
**Specification status:** Build-ready foundation  
**Primary platform:** Apple Silicon macOS  
**Author:** Manus AI

## 1. Product definition

StopSlop is a local writing-pattern review application. It accepts prose, runs an attributed detector on the user’s Mac, and presents a score from 0 to 100, a severity band, metrics, and named findings.

The product must explain results as **writing signals** rather than authorship judgments. It must never claim to identify a person, prove that a text was produced by artificial intelligence, or provide evidence for a high-stakes decision.

StopSlop is a derivative product built on the local Sloptrim detector. The upstream project is described as a command-line and plugin tool with no hosted service, no account, and no text upload. StopSlop adds the desktop interface and packaging layer while preserving applicable licence, notice, and citation materials [1].

## 2. Version 1 goals

| Goal | Definition of success |
|---|---|
| Local analysis | A user can analyze prose without an internet connection. |
| Simple workflow | A user can paste prose, run analysis, understand the result, and clear the workspace without configuration. |
| Explainable output | The result includes a score, severity band, metrics, and named findings with plain-language explanations. |
| Privacy by design | Raw prose is not intentionally sent, persisted, logged, or included in telemetry. |
| Downloadable release | A user can download a DMG from GitHub Releases and install the application on an Apple Silicon Mac. |
| Attribution | The application and repository visibly credit Sloptrim and preserve upstream legal materials. |
| Brand quality | The interface uses Kritrim-ai branding in a restrained, professional manner [2]. |

## 3. Non-goals for Version 1

Version 1 will not include a cloud service, web application, account system, database, history synchronization, team collaboration, online analytics, payment flow, or automatic uploading. It will not make claims about authorship, AI provenance, academic misconduct, employment suitability, legal evidence, or disciplinary decisions.

Document upload, rich text editing, browser extensions, Windows builds, Intel Mac builds, mobile builds, and multi-language analysis should be tracked as future work rather than added to the initial release unless a concrete requirement is approved.

## 4. Target users

The initial target user is a writer, editor, researcher, consultant, student, or professional who wants a private local review of formulaic or machine-like writing signals before revising a draft. The application should be usable by a non-technical Mac user who does not have Python, Node.js, Rust, or a command-line environment installed.

## 5. User experience requirements

### 5.1 Main analysis screen

The main screen must provide a clear editor with a visible label such as **Paste prose to review**. It must show a live word count, a minimum-input message, an **Analyse writing** button, and a **Clear** button. The interface must communicate that analysis is local and that raw text is not intentionally retained.

### 5.2 Result screen

The result view must display the numerical score prominently without presenting it as a probability of AI authorship. It must show a human-readable severity band, the number of words analyzed, a short summary, and an ordered findings list. Each finding must provide a label, severity, and explanation. If offsets are available from the detector, the interface may support highlighting; otherwise, it must not invent or approximate positions.

### 5.3 Required states

The application must have explicit empty, editing, analyzing, successful-result, validation-error, detector-error, and unexpected-error states. Every state must have a recovery action or a clear explanation. The application must remain responsive while analysis runs.

### 5.4 Required information pages

The application must include About, Privacy, Limitations, Credits, and Licences views. The Credits view must identify Sloptrim by Seyed Ehsan Hadi and state that the upstream author does not endorse StopSlop. The Limitations view must make the non-authorship and non-high-stakes-use boundaries visible.

## 6. Functional requirements

| ID | Requirement | Priority | Acceptance condition |
|---|---|---:|---|
| FR-001 | Accept plain prose through paste or typing. | Must | Text remains in the local editor and can be cleared. |
| FR-002 | Enforce a minimum input length. | Must | Analysis is disabled or rejected below the configured minimum. |
| FR-003 | Enforce a maximum input length. | Must | Oversized input is rejected locally with a clear message. |
| FR-004 | Show word count. | Must | Count updates while the user edits. |
| FR-005 | Execute the bundled detector locally. | Must | Analysis succeeds with networking disabled. |
| FR-006 | Return a normalized result. | Must | The UI receives the documented response structure. |
| FR-007 | Show score, band, metrics, and findings. | Must | A successful result renders all available fields. |
| FR-008 | Avoid fabricated offsets. | Must | Missing offsets remain absent or null. |
| FR-009 | Clear text and result. | Must | The clear action removes both from the active workspace. |
| FR-010 | Handle detector failure. | Must | The user sees a recoverable error without raw text in the error message. |
| FR-011 | Work offline. | Must | No network is required for core analysis. |
| FR-012 | Show attribution and limitations. | Must | Credits and limitations are accessible within the application. |
| FR-013 | Provide a DMG release artifact. | Must | The artifact installs and launches on a clean Apple Silicon Mac. |
| FR-014 | Support text export or copy of results. | Should | A user can copy a result summary without exposing raw text to a remote service. |
| FR-015 | Support document uploads. | Deferred | Only add after a separate input-validation and privacy design. |

## 7. Local architecture

The first release should avoid a local HTTP server. The Tauri application invokes a bundled detector adapter as a controlled sidecar process. Communication should use JSON over standard input and standard output, which avoids local port management and reduces the number of runtime boundaries.

```text
┌──────────────────────────────────────────┐
│ StopSlop Tauri desktop interface          │
│ Editor · score · findings · privacy UI    │
└───────────────────────┬──────────────────┘
                        │ Tauri command / IPC
                        v
┌──────────────────────────────────────────┐
│ Local adapter sidecar                     │
│ Input validation · timeout · normalization│
└───────────────────────┬──────────────────┘
                        │ JSON stdin/stdout
                        v
┌──────────────────────────────────────────┐
│ Pinned Sloptrim detector                  │
│ Local execution · no network · no model   │
└──────────────────────────────────────────┘
```

The desktop UI must not import or modify upstream detector files. All StopSlop-specific logic belongs in the adapter and interface layers. The upstream source should remain isolated under `vendor/sloptrim` or be included as a pinned release snapshot with a clear provenance record.

## 8. Normalized analysis contract

The adapter must expose a stable local contract so that the UI is independent of upstream field names. The contract is JSON and should be versioned from the beginning.

### 8.1 Request

```json
{
  "schema_version": "1.0",
  "text": "Prose to review.",
  "language": "en",
  "include_findings": true
}
```

The local adapter must validate the input before invoking the detector. The initial recommended limits are 20 characters minimum and 50,000 characters maximum. These limits must be configurable for tests but fixed and documented for release builds.

### 8.2 Response

```json
{
  "schema_version": "1.0",
  "score": 38,
  "band": "mixed",
  "summary": "Several writing-pattern signals were found.",
  "metrics": {
    "word_count": 248
  },
  "findings": [
    {
      "id": "40_sentence_monotony",
      "label": "Sentence-length monotony",
      "severity": "medium",
      "message": "cv=0.31 below 0.35 threshold",
      "count": 1,
      "samples": ["cv=0.31 below 0.35 threshold"],
      "start": null,
      "end": null
    }
  ],
  "engine": {
    "name": "sloptrim",
    "version": "pinned-upstream-version"
  },
  "privacy": {
    "text_persisted": false,
    "network_required": false
  }
}
```

The vendored detector currently returns a JSON object whose score and band are nested under `_metrics` as `ai_tell_score` and `ai_tell_band`. Individual findings are top-level keys such as `40_sentence_monotony`, with objects containing `label`, `count`, and `samples`. The adapter must map this real structure into the stable StopSlop contract. It must not fabricate character offsets because the upstream output does not provide them. If the upstream tool changes its output, the adapter must fail safely or update through an explicit compatibility change rather than silently guessing.

## 9. Score bands

The initial bands are presentation labels, not probabilities and not authorship classifications.

| Score range | Display band | UI explanation |
|---:|---|---|
| 0 | Clean | No scored writing-pattern signals were returned. |
| 1–19 | Light tells | A small number of signals may be worth reviewing. |
| 20–39 | Mixed | Several signals were found, with mixed intensity. |
| 40–59 | Heavy tells | Multiple strong signals may benefit from revision. |
| 60–100 | Pervasive tells | Many signals were detected across the submitted prose. |

The bands must be reviewed against the real upstream scoring behavior before public release. They must not be marketed as calibrated probabilities.

## 10. Privacy and security requirements

The application must satisfy the following requirements:

1. Core analysis must work with network access disabled.
2. The application must not transmit raw prose to a server.
3. The application must not write raw prose to application logs.
4. Error messages must not include raw prose or arbitrary detector output.
5. Temporary files, if required by the upstream CLI, must be deleted after analysis and created with restrictive permissions.
6. The application must use bounded execution time for the detector process.
7. The application must avoid analytics or crash-reporting integrations that capture request contents.
8. The application must document whether drafts remain in memory, temporary storage, application state restoration, or system clipboard history.
9. Any future file-upload feature must have a separate threat model and retention design.

## 11. Packaging requirements

The output must be a macOS application bundle distributed as a DMG. The bundle must include the UI, the local adapter, the detector runtime or executable, upstream notices, and application metadata. The user must not need to install Python, Node.js, Rust, or other development tools.

The initial build should target Apple Silicon. The release process should produce an unsigned internal artifact first. Public releases should add Apple Developer signing and notarization when the appropriate developer credentials are available. Credentials must never be committed to the repository.

## 12. Branding requirements

StopSlop should use a restrained Kritrim-ai visual identity based on the official public brand reference [2]. The logo must have sufficient contrast and should appear in the application header or About view, the README, and release screenshots where appropriate. Branding must not obscure the product’s independent relationship to the upstream detector.

The interface should prioritize readable typography, generous spacing, high-contrast controls, and clear result hierarchy. Branding should support trust without making the score appear authoritative beyond its documented limitations.

## 13. Accessibility requirements

The application must support keyboard navigation, visible focus states, descriptive labels, readable contrast, non-color-only severity indicators, and error messages that are understandable without relying on animation or color. Dynamic result updates must be announced appropriately to assistive technologies where supported by the chosen desktop framework.

## 14. Testing requirements

Testing must include unit tests for input validation, score-band mapping, normalization, missing-field behavior, malformed detector output, timeout handling, and sanitized errors. Integration tests must run the pinned detector against fixture prose and verify the normalized contract. Packaging tests must confirm that the bundled application can locate its sidecar and operate without Python installed globally.

Manual testing must be performed on a clean Apple Silicon Mac with networking disabled. The test checklist must cover first launch, installation, removal, Gatekeeper behavior, paste handling, long input, Unicode text, empty findings, detector failure, application restart, and clearing of sensitive text.

## 15. Definition of done

The local-only Version 1 is complete when all of the following are true:

- A user can download a DMG from GitHub Releases.
- The application installs and launches on a clean Apple Silicon Mac.
- A user can paste prose and receive a local result without network access.
- The application does not require a cloud account or remote API.
- The detector output is normalized through a documented versioned contract.
- Raw prose is not intentionally persisted or logged.
- Sloptrim licence, notice, citation, and credit materials are preserved.
- StopSlop clearly rejects authorship and high-stakes-use claims.
- The Kritrim-ai brand is present in appropriate product surfaces.
- Tests and build instructions are documented and reproducible.

## References

[1]: https://github.com/seyedehsanhadi/sloptrim "Sloptrim upstream repository"

[2]: https://www.kritrim-ai.com/ "Kritrim-ai public website and branding reference"
