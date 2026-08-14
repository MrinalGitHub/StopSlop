"""Local adapter around the vendored Sloptrim detector.

The adapter deliberately keeps the upstream source isolated. It invokes the
pinned CLI, validates the JSON shape, and maps upstream findings into the
StopSlop UI contract.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contract import AnalysisResponse, Finding


class AnalysisError(RuntimeError):
    """Safe, user-facing analysis failure without submitted text."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def score_band(score: int) -> str:
    """Map the upstream score to a display band, not an authorship label."""

    if score == 0:
        return "clean"
    if score < 20:
        return "light tells"
    if score < 40:
        return "mixed"
    if score < 60:
        return "heavy tells"
    return "pervasive tells"


def _severity(count: Optional[int]) -> str:
    """Derive a modest UI severity from finding count only."""

    if count is not None and count >= 3:
        return "high"
    if count is not None and count >= 2:
        return "medium"
    return "low"


def _safe_samples(value: Any) -> List[str]:
    """Keep samples bounded and textual before returning them to the UI."""

    if not isinstance(value, list):
        return []
    result = []
    for item in value[:5]:
        if isinstance(item, str):
            result.append(item[:300])
    return result


def _normalise_finding(identifier: str, value: Any) -> Finding:
    """Map one Sloptrim top-level finding into a StopSlop finding."""

    if not isinstance(value, dict):
        raise AnalysisError("detector_output_invalid", "A detector finding was malformed.")

    label = value.get("label")
    if not isinstance(label, str) or not label.strip():
        label = "Writing pattern"

    count = value.get("count")
    if not isinstance(count, int):
        count = None

    samples = _safe_samples(value.get("samples"))
    message = samples[0] if samples else "Review this writing pattern."

    return Finding(
        id=str(identifier),
        label=label[:160],
        severity=_severity(count),
        message=message[:300],
        count=count,
        samples=samples,
        start=None,
        end=None,
    )


def _normalise(raw: Dict[str, Any], engine_version: str) -> AnalysisResponse:
    """Normalize the verified Sloptrim JSON structure."""

    raw_metrics = raw.get("_metrics")
    if not isinstance(raw_metrics, dict):
        raise AnalysisError("detector_output_invalid", "Detector metrics were missing.")

    raw_score = raw_metrics.get("ai_tell_score")
    if not isinstance(raw_score, int) or not 0 <= raw_score <= 100:
        raise AnalysisError("detector_output_invalid", "Detector score was invalid.")

    findings = []
    for identifier, value in raw.items():
        if identifier == "_metrics":
            continue
        findings.append(_normalise_finding(identifier, value))

    findings.sort(key=lambda item: (item.severity != "high", item.severity != "medium", item.id))
    metrics = dict(raw_metrics)
    metrics["finding_count"] = len(findings)

    if findings:
        summary = "{} writing-pattern signal(s) were found for review.".format(len(findings))
    else:
        summary = "No scored writing-pattern signals were returned."

    return AnalysisResponse(
        schema_version="1.0",
        score=raw_score,
        band=score_band(raw_score),
        summary=summary,
        metrics=metrics,
        findings=findings,
        engine={"name": "sloptrim", "version": engine_version},
        privacy={"text_persisted": False, "network_required": False},
    )


def _run_frozen_detector(detector_path: Path, text: str) -> Dict[str, Any]:
    """Load the bundled detector directly when running as a frozen binary."""

    import importlib.util

    spec = importlib.util.spec_from_file_location("sloptrim_detect", detector_path)
    if spec is None or spec.loader is None:
        raise AnalysisError("detector_unavailable", "The bundled detector is unavailable.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.scan(text)
    if not isinstance(result, dict):
        raise AnalysisError("detector_output_invalid", "The detector returned an unsupported result.")
    return result


def analyse_text(
    text: str,
    detector_path: Path,
    python_path: Optional[str] = None,
    timeout_seconds: int = 20,
    engine_version: str = "pinned-upstream",
) -> AnalysisResponse:
    """Run the detector locally and return a normalized response."""

    if not isinstance(text, str) or len(text.strip()) < 20:
        raise AnalysisError("invalid_input", "Please provide at least 20 characters of prose.")
    if len(text) > 50000:
        raise AnalysisError("invalid_input", "Please keep the text below 50,000 characters.")
    if not detector_path.is_file():
        raise AnalysisError("detector_unavailable", "The bundled detector is unavailable.")

    if getattr(sys, "frozen", False):
        try:
            raw = _run_frozen_detector(detector_path, text)
        except AnalysisError:
            raise
        except Exception as exc:
            raise AnalysisError("analysis_failed", "The local analysis could not be completed.") from exc
        return _normalise(raw, engine_version)

    executable = python_path or sys.executable
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            encoding="utf-8",
            delete=False,
        ) as draft:
            draft.write(text)
            temp_path = Path(draft.name)
            os.chmod(temp_path, 0o600)

        completed = subprocess.run(
            [executable, str(detector_path), str(temp_path)],
            cwd=str(detector_path.parent.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AnalysisError("detector_timeout", "The local analysis timed out.") from exc
    except OSError as exc:
        raise AnalysisError("detector_unavailable", "The local detector could not start.") from exc
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    if completed.returncode != 0:
        raise AnalysisError("analysis_failed", "The local analysis could not be completed.")

    try:
        raw = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AnalysisError("detector_output_invalid", "The detector returned invalid output.") from exc

    if not isinstance(raw, dict):
        raise AnalysisError("detector_output_invalid", "The detector returned an unsupported result.")

    return _normalise(raw, engine_version)
