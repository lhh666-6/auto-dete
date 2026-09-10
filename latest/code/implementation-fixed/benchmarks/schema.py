from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PredictionRow:
    case_id: str
    seed: int
    target: str
    prediction: str | None
    accepted: bool
    score: float
    perturbation: str
    severity: float
    latency_ms: float
    model: str = "auto-decte"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    relative_path: str
    sha256: str
    rows: int
