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

from .contract import AnalysisResponse, Finding, Insight


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


def _build_insights(raw_metrics: Dict[str, Any], text: str) -> List[Insight]:
    """Create plain-language text metrics without changing the detector score."""

    words = len(text.split())
    characters = len(text)
    paragraphs = max(1, len([item for item in text.split("\n\n") if item.strip()]))
    sentences = raw_metrics.get("sentences")
    if not isinstance(sentences, int):
        sentences = 0
    insights = [
        Insight(
            id="text_shape",
            label="Text shape",
            value="{} words".format(words),
            message="{} characters across {} sentence(s) and {} paragraph(s).".format(characters, sentences, paragraphs),
            tone="neutral",
        )
    ]

    length_cv = raw_metrics.get("length_cv")
    if isinstance(length_cv, (int, float)):
        label = "Varied" if length_cv >= 0.35 else "Consistent"
        tone = "positive" if length_cv >= 0.35 else "attention"
        message = "Sentence-length variation is {:.2f}; higher variation usually reads as more natural.".format(length_cv)
    else:
        label = "Not enough text"
        tone = "neutral"
        message = "More sentences are needed to evaluate sentence-length variation."
    insights.append(Insight("sentence_variety", "Sentence variety", label, message, tone))

    passive_ratio = raw_metrics.get("passive_voice_ratio")
    if isinstance(passive_ratio, (int, float)):
        passive_percent = round(passive_ratio * 100)
        tone = "attention" if passive_percent >= 25 else "neutral"
        message = "Approximately {}% of detected clauses use passive voice.".format(passive_percent)
        value = "{}% passive".format(passive_percent)
    else:
        tone = "neutral"
        message = "Passive-voice estimation was not available for this text."
        value = "Not available"
    insights.append(Insight("voice", "Voice", value, message, tone))

    readability_stdev = raw_metrics.get("readability_fk_stdev")
    if isinstance(readability_stdev, (int, float)):
        value = "{:.1f} spread".format(readability_stdev)
        message = "Readability varies by {:.1f} grade-level points across sentences.".format(readability_stdev)
        tone = "positive" if readability_stdev >= 1.0 else "attention"
    else:
        value = "Not available"
        message = "More sentences are needed to compare readability across the text."
        tone = "neutral"
    insights.append(Insight("readability", "Readability", value, message, tone))

    formatting_keys = ("invisible_chars", "nonstandard_spaces", "trailing_newlines", "eol_trailing_spaces", "leading_whitespace", "homoglyphs")
    formatting_flags = sum(int(raw_metrics.get(key) or 0) for key in formatting_keys)
    if formatting_flags:
        format_value = "{} flag(s)".format(formatting_flags)
        format_message = "Formatting or character-level anomalies were detected and should be reviewed."
        format_tone = "attention"
    else:
        format_value = "Clean"
        format_message = "No hidden characters, unusual spaces, or trailing formatting anomalies were detected."
        format_tone = "positive"
    insights.append(Insight("formatting", "Formatting", format_value, format_message, format_tone))

    confidence = raw_metrics.get("confidence")
    confidence_reason = raw_metrics.get("confidence_reason")
    confidence_value = str(confidence or "none").replace("_", " ").title()
    confidence_message = str(confidence_reason or "Confidence is limited for short text.")[:240]
    insights.append(Insight("confidence", "Signal confidence", confidence_value, confidence_message, "neutral"))
    return insights


def _normalise(raw: Dict[str, Any], engine_version: str, text: str = "") -> AnalysisResponse:
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
    metrics["word_count"] = len(text.split())
    metrics["character_count"] = len(text)
    metrics["paragraph_count"] = max(1, len([item for item in text.split("\n\n") if item.strip()]))
    metrics["finding_count"] = len(findings)
    insights = _build_insights(raw_metrics, text)

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
        insights=insights,
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
    if len(text.split()) > 8000:
        raise AnalysisError("invalid_input", "Please keep the text below 8,000 words.")
    if not detector_path.is_file():
        raise AnalysisError("detector_unavailable", "The bundled detector is unavailable.")

    if getattr(sys, "frozen", False):
        try:
            raw = _run_frozen_detector(detector_path, text)
        except AnalysisError:
            raise
        except Exception as exc:
            raise AnalysisError("analysis_failed", "The local analysis could not be completed.") from exc
        return _normalise(raw, engine_version, text)

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

    return _normalise(raw, engine_version, text)
