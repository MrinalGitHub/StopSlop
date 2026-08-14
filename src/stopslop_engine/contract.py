"""Stable, UI-facing response types for local StopSlop analysis."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Finding:
    """A normalized upstream writing-pattern finding."""

    id: str
    label: str
    severity: str
    message: str
    count: Optional[int] = None
    samples: List[str] = field(default_factory=list)
    start: Optional[int] = None
    end: Optional[int] = None


@dataclass
class AnalysisResponse:
    """The versioned response consumed by the desktop interface."""

    schema_version: str
    score: int
    band: str
    summary: str
    metrics: Dict[str, Any]
    findings: List[Finding]
    engine: Dict[str, str]
    privacy: Dict[str, bool]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
