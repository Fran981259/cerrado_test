from pathlib import Path

import yaml


def test_publish_workflow_requires_manual_dispatch_and_immutable_tags() -> None:
    workflow = yaml.safe_load(Path(".github/workflows/deploy.yml").read_text(encoding="utf-8"))
    content = Path(".github/workflows/deploy.yml").read_text(encoding="utf-8")

    assert workflow[True] == {"workflow_dispatch": None}
    assert ":latest" not in content
    assert "${{ github.sha }}" in content


def test_update_script_uses_swarm_stack_and_full_commit_sha() -> None:
    script = Path("scripts/update.sh").read_text(encoding="utf-8")

    assert "docker-stack.swarm.yml" in script
    assert "git rev-parse HEAD" in script
    assert "docker-compose.local.yml" in script
    assert ":latest" not in script


def test_publish_workflow_generates_dependency_inventory() -> None:
    workflow = Path(".github/workflows/deploy.yml").read_text(encoding="utf-8")

    assert "dependency-inventory" in workflow
    assert "pip freeze --all" in workflow
    assert "npm ls --all --json" in workflow
    assert "actions/upload-artifact@v4" in workflow
