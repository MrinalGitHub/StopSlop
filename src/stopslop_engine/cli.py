"""JSON line interface for the StopSlop local detector adapter."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .adapter import AnalysisError, analyse_text


DEFAULT_DETECTOR = (
    Path(__file__).resolve().parents[2]
    / "vendor"
    / "sloptrim"
    / "scripts"
    / "detect.py"
)


def main(argv: Optional[List[str]] = None) -> int:
    """Read one request from stdin and write one response to stdout."""

    parser = argparse.ArgumentParser(description="Run local StopSlop analysis.")
    parser.add_argument("--detector", type=Path, default=DEFAULT_DETECTOR)
    parser.add_argument("--engine-version", default="pinned-upstream")
    args = parser.parse_args(argv)

    try:
        request = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        response = {
            "ok": False,
            "error": {"code": "invalid_input", "message": "The analysis request was invalid."},
        }
        json.dump(response, sys.stdout)
        return 2

    if not isinstance(request, dict):
        response = {
            "ok": False,
            "error": {"code": "invalid_input", "message": "The analysis request was invalid."},
        }
        json.dump(response, sys.stdout)
        return 2

    try:
        result = analyse_text(
            text=request.get("text", ""),
            detector_path=args.detector,
            engine_version=args.engine_version,
        )
    except AnalysisError as exc:
        response = {"ok": False, "error": {"code": exc.code, "message": exc.message}}
        json.dump(response, sys.stdout)
        return 1

    json.dump({"ok": True, "result": result.to_dict()}, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
