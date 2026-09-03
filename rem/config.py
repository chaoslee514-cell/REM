"""Simple configuration for REM."""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class RemConfig:
    data_dir: Path = Path(".data")
    skills_dir: Path = Path("./skills")
    installed_dir: Path = Path("./installed_skills")
    default_session: str = "default"

    # Rough token estimate per step (used for savings calculation)
    tokens_per_step_estimate: int = 45


def get_config() -> RemConfig:
    return RemConfig()
