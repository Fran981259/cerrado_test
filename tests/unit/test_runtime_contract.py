from pathlib import Path

import yaml


def _swarm_stack() -> dict:
    return yaml.safe_load(Path("docker-stack.swarm.yml").read_text(encoding="utf-8"))


def test_swarm_stack_has_required_services_and_isolated_network() -> None:
    stack = _swarm_stack()
    services = stack["services"]

    assert {"postgres", "redis", "portal_cerrado", "celery_worker", "celery_beat", "frontend", "caddy"} <= set(services)
    assert stack["networks"]["cerrado_test_net"]["driver"] == "overlay"
    assert all(service.get("deploy", {}).get("replicas") == 1 for service in services.values())


def test_swarm_stack_uses_digests_and_healthchecks() -> None:
    stack = _swarm_stack()

    for name, service in stack["services"].items():
        assert service.get("healthcheck"), name
        if name in {"portal_cerrado", "celery_worker", "celery_beat", "flower", "frontend"}:
            assert "IMAGE:?" in service["image"] and "SHA" in service["image"]


def test_swarm_stack_isolated_volumes_do_not_use_legacy_names() -> None:
    stack = _swarm_stack()

    assert all(name.startswith("cerrado_test_") for name in stack["volumes"])
    volume_text = str(stack["services"])
    assert "botgram_" not in volume_text
