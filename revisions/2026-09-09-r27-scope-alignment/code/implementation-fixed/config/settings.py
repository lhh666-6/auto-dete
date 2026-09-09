"""Environment-driven application settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration with all generated data below one root."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FORM_DEMO_",
        extra="ignore",
    )

    data_root: Path = Path("data")
    ai_enabled: bool = False

    # Authority registries (B + C certificate): producers and selection
    # artifacts known to the review contract. The artifact ids identify the
    # selection rule applied, not a statistical calibration claim (D1(c)).
    authority_known_producers: tuple[tuple[str, str], ...] = (
        ("opencv-template-digit", "1"),
        ("opencv-fill-ratio-omr", "1"),
        ("recognizer-a", "1.0"),
        ("recognizer-b", "2.0"),
        ("human-reviewer", "manual-entry-v1"),
    )
    authority_selection_artifacts: tuple[str, ...] = (
        "recognition-threshold-v1",
        "cal-1",
        "cal-2",
    )
    # Prototype authorization only. Authentication/session integrity is a
    # host assumption and is deliberately outside this artifact's claims.
    authority_fact_admission_principals: tuple[str, ...] = (
        "reviewer",
        "reviewer-1",
        "reviewer-2",
        "reviewer-a",
        "reviewer-b",
    )

    @property
    def database_path(self) -> Path:
        return self.data_root / "database" / "demo.db"

    @property
    def evidence_root(self) -> Path:
        return self.data_root / "evidence"

    @property
    def exports_root(self) -> Path:
        return self.data_root / "exports"
