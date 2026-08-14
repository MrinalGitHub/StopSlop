import json
import sys
from pathlib import Path

import pytest

from stopslop_engine.adapter import AnalysisError, analyse_text


FAKE_DETECTOR = Path(__file__).parent / "fixtures" / "fake_detector.py"


def test_normalizes_verified_sloptrim_shape():
    result = analyse_text(
        "This is a sufficiently long sample of prose for the local test detector.",
        detector_path=FAKE_DETECTOR,
        python_path=sys.executable,
    )

    assert result.schema_version == "1.0"
    assert result.score == 38
    assert result.band == "mixed"
    assert result.findings[0].id == "40_sentence_monotony"
    assert result.findings[0].start is None
    assert result.privacy["text_persisted"] is False
    assert result.privacy["network_required"] is False


def test_rejects_short_input():
    with pytest.raises(AnalysisError) as error:
        analyse_text("Too short", detector_path=FAKE_DETECTOR)

    assert error.value.code == "invalid_input"


def test_rejects_missing_detector():
    with pytest.raises(AnalysisError) as error:
        analyse_text(
            "This is a sufficiently long sample of prose for the local test detector.",
            detector_path=Path("does-not-exist.py"),
        )

    assert error.value.code == "detector_unavailable"


def test_never_returns_raw_text_in_failure():
    secret = "PRIVATE_SAMPLE_THAT_MUST_NOT_APPEAR"
    with pytest.raises(AnalysisError) as error:
        analyse_text(secret, detector_path=Path("does-not-exist.py"))

    assert secret not in error.value.message


def test_cli_request_shape_can_be_serialized():
    request = {"text": "A sufficiently long local test request for StopSlop.", "include_findings": True}
    assert json.dumps(request).startswith("{")
