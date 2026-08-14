# StopSlop Local Architecture

## Decision summary

StopSlop Version 1 is a local-only macOS desktop application. It uses a Tauri user interface and a bundled detector sidecar. The sidecar receives a JSON request through standard input, invokes the pinned Sloptrim detector, normalizes the result, and writes one JSON response to standard output.

The first release does not include FastAPI, Wasp, Railway, PostgreSQL, user accounts, cloud synchronization, or a local HTTP server. This keeps the security boundary small and avoids unnecessary runtime and deployment complexity.

## Component responsibilities

| Component | Responsibility | Must not do |
|---|---|---|
| Tauri UI | Editing, validation messages, progress state, results, About, Privacy, Credits, and Limitations views. | Invoke upstream detector files directly or send text to the network. |
| Tauri command bridge | Receive a typed request from the UI and invoke the sidecar with bounded input and execution time. | Persist drafts, expose arbitrary shell execution, or return raw process diagnostics. |
| Local adapter | Validate input, invoke Sloptrim, normalize output, map score bands, and sanitize errors. | Modify upstream detector files or invent finding offsets. |
| Sloptrim source | Perform the upstream writing-pattern analysis. | Make network requests or be treated as an authorship classifier. |
| Release bundle | Contain all runtime assets needed by a user. | Require developer tooling or secrets on the user’s machine. |

## Data flow

```text
User prose
   |
   v
In-memory Tauri editor
   |
   | typed IPC request
   v
Rust command / sidecar launcher
   |
   | bounded JSON stdin
   v
Local StopSlop adapter
   |
   | controlled invocation
   v
Pinned Sloptrim detector
   |
   | normalized JSON stdout
   v
Tauri result renderer
```

## Process boundary

The adapter should run as a separate process rather than importing a large amount of upstream code into the UI process. This creates a clear failure boundary: detector crashes, malformed output, and timeouts can be converted into safe user-facing errors without terminating the interface.

The process launcher must use an explicit executable path resolved from the application bundle. It must not depend on the current working directory, a user’s shell configuration, or a globally installed Python executable. The bundled runtime strategy must be selected during implementation and recorded in a decision log.

## Runtime packaging options

| Option | Advantages | Risks | Recommendation |
|---|---|---|---|
| Bundle a Python executable created by a packaging tool | Reuses the upstream Python detector with minimal source changes. | Larger bundle, platform-specific build work, executable path and signing concerns. | Preferred if the upstream detector cannot be ported cleanly. |
| Bundle a self-contained Python runtime and adapter | More predictable than depending on system Python. | Larger release artifact and more complex updates. | Viable fallback. |
| Port the detector to Rust or Swift | Potentially smaller native runtime. | High compatibility risk and likely semantic drift from upstream. | Not suitable for Version 1. |
| Run a local HTTP server | Familiar API boundary. | Adds ports, lifecycle management, server configuration, and attack surface. | Do not use for Version 1. |

## Versioning

The JSON response includes `schema_version` and the engine metadata includes the pinned upstream version or commit. Any change that alters field meaning, score-band interpretation, finding identifiers, or privacy metadata must update the schema version or document backward compatibility.

The repository must keep fixture outputs for the pinned upstream detector. When the upstream version changes, a pull request must include a compatibility review and updated fixtures.

## Failure handling

The UI should receive only controlled error categories:

- `invalid_input`: the user input violates local limits.
- `detector_unavailable`: the bundled executable is missing or cannot start.
- `detector_timeout`: analysis exceeded the configured execution limit.
- `detector_output_invalid`: the process returned malformed or unsupported output.
- `analysis_failed`: a safe generic fallback for unexpected failures.

Raw command output, file paths containing user data, submitted prose, and arbitrary stack traces must not be shown in the UI or written to logs.

## Future extension boundary

A future cloud or multi-device edition may reuse the normalized response contract, but it must be designed as a separate product boundary. Adding cloud functionality later must not silently change the local-only application’s privacy promise. Any future network feature must be opt-in, separately documented, and protected by an independent threat model.
