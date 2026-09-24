"""Contrato estático para observabilidade, alertas e recuperação."""

from pathlib import Path

import yaml

ROOT = Path(__file__).parents[2]


def _config() -> dict:
    return yaml.safe_load((ROOT / "config/observability.yaml").read_text(encoding="utf-8"))


def test_observability_declares_required_metrics_and_alerts() -> None:
    config = _config()
    metric_names = {
        metric["name"]
        for group in config["service_metrics"].values()
        for metric in group
    }
    assert {"database_health", "redis_health", "disk_usage_ratio"} <= metric_names
    alert_ids = {alert["id"] for alert in config["alerts"]}
    assert {"publication_stale", "dependency_unhealthy", "disk_pressure"} <= alert_ids


def test_observability_forbids_sensitive_log_fields_and_requires_backup_evidence() -> None:
    config = _config()
    assert {"password", "token", "api_key"} <= set(config["log_policy"]["forbidden_fields"])
    assert config["backup_policy"]["retention_days"] == 30
    assert "sha256" in config["backup_policy"]["required_evidence"]
    assert config["rollback_policy"]["production_requires_explicit_approval"] is True
