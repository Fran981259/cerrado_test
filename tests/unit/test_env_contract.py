from pathlib import Path


def _example_names() -> set[str]:
    lines = Path(".env.example").read_text(encoding="utf-8").splitlines()
    return {line.split("=", 1)[0] for line in lines if line and not line.startswith("#") and "=" in line}


def test_env_example_documents_runtime_llm_and_archive_contract() -> None:
    names = _example_names()

    assert {"LLM_PROVIDER", "GEMINI_MODEL", "OPENAI_MODEL", "ARCHIVE_DAYS_AFTER_PUBLISH"}.issubset(names)
    assert "API_URL" in names


def test_env_example_no_longer_documents_retired_llm_or_monitoring_keys() -> None:
    names = _example_names()

    assert "OPENROUTER_API_KEY" not in names
    assert "LLM_MODEL" not in names
    assert "GRAFANA_API_KEY" not in names
