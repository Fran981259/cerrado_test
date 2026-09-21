"""Small, validated runtime settings loaded from repository configuration."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SchedulerSettings:
    min_articles_per_day: int = 50
    update_interval_minutes: int = 30

    @property
    def pipeline_interval_seconds(self) -> int:
        return self.update_interval_minutes * 60


def _positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


@lru_cache(maxsize=1)
def get_scheduler_settings() -> SchedulerSettings:
    """Load the runtime-owned scheduler policy, falling back to safe defaults."""
    path = Path(__file__).resolve().parents[1] / "config" / "scheduler.yaml"
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        payload = {}
    volume = payload.get("volume", {}) if isinstance(payload, dict) else {}
    if not isinstance(volume, dict):
        volume = {}
    return SchedulerSettings(
        min_articles_per_day=_positive_int(volume.get("min_articles_per_day"), 50),
        update_interval_minutes=_positive_int(volume.get("update_interval_minutes"), 30),
    )
