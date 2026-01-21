"""Tests for registry module - 100% coverage required."""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from registry import (
    Priority,
    Project,
    Registry,
    RegistryManager,
    Status,
)


class TestPriority:
    def test_default_values(self) -> None:
        p = Priority()
        assert p.urgency == 2
        assert p.difficulty == 2

    def test_custom_values(self) -> None:
        p = Priority(urgency=1, difficulty=4)
        assert p.urgency == 1
        assert p.difficulty == 4

    def test_invalid_urgency_low(self) -> None:
        with pytest.raises(ValueError, match="urgency must be 1-4"):
            Priority(urgency=0, difficulty=2)

    def test_invalid_urgency_high(self) -> None:
        with pytest.raises(ValueError, match="urgency must be 1-4"):
            Priority(urgency=5, difficulty=2)

    def test_invalid_difficulty_low(self) -> None:
        with pytest.raises(ValueError, match="difficulty must be 1-4"):
            Priority(urgency=2, difficulty=0)

    def test_invalid_difficulty_high(self) -> None:
        with pytest.raises(ValueError, match="difficulty must be 1-4"):
            Priority(urgency=2, difficulty=5)

    def test_score_easy_urgent(self) -> None:
        p = Priority(urgency=1, difficulty=1)
        assert p.score() == 8  # (5-1) + (5-1) = 8 (highest priority)

    def test_score_hard_not_urgent(self) -> None:
        p = Priority(urgency=4, difficulty=4)
        assert p.score() == 2  # (5-4) + (5-4) = 2 (lowest priority)

    def test_score_medium(self) -> None:
        p = Priority(urgency=2, difficulty=2)
        assert p.score() == 6  # (5-2) + (5-2) = 6


class TestProject:
    def test_create(self) -> None:
        p = Project.create(
            title="Test Project",
            brief="A test",
            spec="Full spec",
            tech_stack=["Python"],
        )
        assert p.title == "Test Project"
        assert p.brief == "A test"
        assert p.spec == "Full spec"
        assert p.tech_stack == ["Python"]
        assert p.status == Status.IDEA
        assert p.priority.urgency == 2
        assert p.priority.difficulty == 2
        assert len(p.id) == 8
        assert p.created_at.endswith("Z")

    def test_create_with_priority(self) -> None:
        p = Project.create(
            title="Test",
            brief="Brief",
            spec="Spec",
            tech_stack=[],
            urgency=1,
            difficulty=3,
        )
        assert p.priority.urgency == 1
        assert p.priority.difficulty == 3

    def test_to_dict(self) -> None:
        p = Project.create(
            title="Test",
            brief="Brief",
            spec="Spec",
            tech_stack=["Python", "Flask"],
        )
        d = p.to_dict()
        assert d["title"] == "Test"
        assert d["status"] == "idea"
        assert d["priority"]["urgency"] == 2
        assert d["tech_stack"] == ["Python", "Flask"]

    def test_from_dict(self) -> None:
        data = {
            "id": "abc12345",
            "title": "Test",
            "brief": "Brief",
            "spec": "Spec",
            "status": "in_progress",
            "priority": {"urgency": 1, "difficulty": 3},
            "tech_stack": ["Rust"],
            "created_at": "2025-01-01T00:00:00Z",
            "started_at": "2025-01-02T00:00:00Z",
            "completed_at": None,
            "repo_url": "https://github.com/test/test",
            "locked_by": "worker-1",
            "locked_at": "2025-01-02T00:00:00Z",
            "blocked_reason": None,
        }
        p = Project.from_dict(data)
        assert p.id == "abc12345"
        assert p.status == Status.IN_PROGRESS
        assert p.priority.urgency == 1
        assert p.locked_by == "worker-1"

    def test_roundtrip(self) -> None:
        original = Project.create(
            title="Roundtrip",
            brief="Test roundtrip",
            spec="Full spec here",
            tech_stack=["Go", "PostgreSQL"],
            urgency=3,
            difficulty=2,
        )
        data = original.to_dict()
        restored = Project.from_dict(data)
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.status == original.status
        assert restored.priority.urgency == original.priority.urgency


class TestRegistry:
    def test_empty_registry(self) -> None:
        r = Registry()
        assert r.version == "1.0.0"
        assert r.projects == []

    def test_to_dict(self) -> None:
        r = Registry()
        p = Project.create(title="Test", brief="B", spec="S", tech_stack=[])
        r.projects.append(p)
        d = r.to_dict()
        assert d["version"] == "1.0.0"
        assert len(d["projects"]) == 1

    def test_from_dict(self) -> None:
        data = {
            "version": "1.0.0",
            "projects": [
                {
                    "id": "test1234",
                    "title": "Test",
                    "brief": "B",
                    "spec": "S",
                    "status": "idea",
                    "priority": {"urgency": 2, "difficulty": 2},
                    "tech_stack": [],
                    "created_at": "2025-01-01T00:00:00Z",
                    "started_at": None,
                    "completed_at": None,
                    "repo_url": None,
                    "locked_by": None,
                    "locked_at": None,
                    "blocked_reason": None,
                }
            ],
        }
        r = Registry.from_dict(data)
        assert len(r.projects) == 1
        assert r.projects[0].title == "Test"


class TestRegistryManager:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def manager(self, temp_dir: Path) -> RegistryManager:
        return RegistryManager(temp_dir)

    def test_add_project(self, manager: RegistryManager) -> None:
        p = Project.create(title="New", brief="B", spec="S", tech_stack=[])
        result = manager.add(p)
        assert result.id == p.id
        assert manager.registry_path.exists()

    def test_get_project(self, manager: RegistryManager) -> None:
        p = Project.create(title="Find Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        found = manager.get(p.id)
        assert found is not None
        assert found.title == "Find Me"

    def test_get_nonexistent(self, manager: RegistryManager) -> None:
        assert manager.get("nonexistent") is None

    def test_list_all(self, manager: RegistryManager) -> None:
        p1 = Project.create(title="P1", brief="B", spec="S", tech_stack=[])
        p2 = Project.create(title="P2", brief="B", spec="S", tech_stack=[])
        manager.add(p1)
        manager.add(p2)
        projects = manager.list()
        assert len(projects) == 2

    def test_list_with_status_filter(self, manager: RegistryManager) -> None:
        p1 = Project.create(title="P1", brief="B", spec="S", tech_stack=[])
        p2 = Project.create(title="P2", brief="B", spec="S", tech_stack=[])
        manager.add(p1)
        manager.add(p2)
        manager.update(p2.id, status="in_progress")

        ideas = manager.list(status_filter=[Status.IDEA])
        assert len(ideas) == 1
        assert ideas[0].title == "P1"

        in_progress = manager.list(status_filter=[Status.IN_PROGRESS])
        assert len(in_progress) == 1
        assert in_progress[0].title == "P2"

    def test_list_unlocked_only(self, manager: RegistryManager) -> None:
        p1 = Project.create(title="Unlocked", brief="B", spec="S", tech_stack=[])
        p2 = Project.create(title="Locked", brief="B", spec="S", tech_stack=[])
        manager.add(p1)
        manager.add(p2)
        manager.lock(p2.id, "worker-1")

        unlocked = manager.list(unlocked_only=True)
        assert len(unlocked) == 1
        assert unlocked[0].title == "Unlocked"

    def test_update_project(self, manager: RegistryManager) -> None:
        p = Project.create(title="Original", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        updated = manager.update(p.id, status="in_progress")
        assert updated is not None
        assert updated.status == Status.IN_PROGRESS

    def test_update_nonexistent(self, manager: RegistryManager) -> None:
        result = manager.update("nonexistent", status="completed")
        assert result is None

    def test_update_priority(self, manager: RegistryManager) -> None:
        p = Project.create(title="Update Priority", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        updated = manager.update(p.id, priority={"urgency": 1, "difficulty": 4})
        assert updated is not None
        assert updated.priority.urgency == 1
        assert updated.priority.difficulty == 4

    def test_lock_project(self, manager: RegistryManager) -> None:
        p = Project.create(title="Lock Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        locked = manager.lock(p.id, "worker-42")
        assert locked is not None
        assert locked.locked_by == "worker-42"
        assert locked.locked_at is not None

    def test_unlock_project(self, manager: RegistryManager) -> None:
        p = Project.create(title="Unlock Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        manager.lock(p.id, "worker-1")
        unlocked = manager.unlock(p.id)
        assert unlocked is not None
        assert unlocked.locked_by is None
        assert unlocked.locked_at is None

    def test_unlock_all_by_worker(self, manager: RegistryManager) -> None:
        p1 = Project.create(title="P1", brief="B", spec="S", tech_stack=[])
        p2 = Project.create(title="P2", brief="B", spec="S", tech_stack=[])
        p3 = Project.create(title="P3", brief="B", spec="S", tech_stack=[])
        manager.add(p1)
        manager.add(p2)
        manager.add(p3)
        manager.lock(p1.id, "worker-1")
        manager.lock(p2.id, "worker-1")
        manager.lock(p3.id, "worker-2")

        count = manager.unlock_all_by_worker("worker-1")
        assert count == 2

        projects = manager.list()
        locked_by_1 = [p for p in projects if p.locked_by == "worker-1"]
        locked_by_2 = [p for p in projects if p.locked_by == "worker-2"]
        assert len(locked_by_1) == 0
        assert len(locked_by_2) == 1

    def test_delete_project(self, manager: RegistryManager) -> None:
        p = Project.create(title="Delete Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        assert manager.delete(p.id) is True
        assert manager.get(p.id) is None

    def test_delete_nonexistent(self, manager: RegistryManager) -> None:
        assert manager.delete("nonexistent") is False

    def test_empty_registry_load(self, manager: RegistryManager) -> None:
        projects = manager.list()
        assert projects == []

    def test_persistence(self, temp_dir: Path) -> None:
        manager1 = RegistryManager(temp_dir)
        p = Project.create(title="Persist", brief="B", spec="S", tech_stack=[])
        manager1.add(p)

        manager2 = RegistryManager(temp_dir)
        found = manager2.get(p.id)
        assert found is not None
        assert found.title == "Persist"

    def test_save_failure_cleanup(self, manager: RegistryManager, temp_dir: Path) -> None:
        from unittest.mock import patch

        p = Project.create(title="Fail", brief="B", spec="S", tech_stack=[])
        registry = Registry()
        registry.projects.append(p)

        # Mock Path.rename to fail, should cleanup temp file
        with patch.object(Path, "rename", side_effect=OSError("disk full")):
            with pytest.raises(OSError, match="disk full"):
                manager._save(registry)

        # Verify no temp files left behind
        temp_files = list(temp_dir.glob(".registry-*.tmp"))
        assert len(temp_files) == 0
