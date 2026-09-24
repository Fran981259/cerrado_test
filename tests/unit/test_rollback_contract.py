"""Contrato de segurança para rollback por imagem imutável."""

from pathlib import Path

SCRIPT = Path("scripts/rollback.sh").read_text(encoding="utf-8")


def test_rollback_defaults_to_dry_run_and_requires_explicit_confirmation() -> None:
    assert "DRY-RUN" in SCRIPT
    assert 'CONFIRM="${2:-}"' in SCRIPT
    assert '[[ "$CONFIRM" != "--confirm" ]]' in SCRIPT
    assert 'ROLLBACK_APPROVED:-' in SCRIPT


def test_rollback_requires_full_sha_and_updates_all_runtime_services() -> None:
    assert "^[0-9a-f]{40,64}$" in SCRIPT
    assert '"${STACK_NAME}_${service}"' in SCRIPT
    assert "for service in portal_cerrado celery_worker celery_beat flower" in SCRIPT
    for service in ("portal_cerrado", "celery_worker", "celery_beat", "flower"):
        assert service in SCRIPT
    assert '"${STACK_NAME}_frontend"' in SCRIPT
    assert "docker service update --image" in SCRIPT
