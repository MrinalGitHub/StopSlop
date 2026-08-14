"""Local StopSlop analysis adapter."""

from .adapter import AnalysisError, analyse_text
from .contract import AnalysisResponse, Finding

__all__ = ["AnalysisError", "AnalysisResponse", "Finding", "analyse_text"]
