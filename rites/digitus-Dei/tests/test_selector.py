"""Tests for selector module - 100% coverage required."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from registry import Project, RegistryManager, Status
from selector import select, weighted_random_select


class TestWeightedRandomSelect:
    def test_empty_list(self) -> None:
        assert weighted_random_select([]) is None

    def test_single_project(self) -> None:
        p = Project.create(title="Only", brief="B", spec="S", tech_stack=[])
        result = weighted_random_select([p])
        assert result == p

    def test_returns_project_from_list(self) -> None:
        projects = [
            Project.create(title="P1", brief="B", spec="S", tech_stack=[]),
            Project.create(title="P2", brief="B", spec="S", tech_stack=[]),
            Project.create(title="P3", brief="B", spec="S", tech_stack=[]),
        ]
        result = weighted_random_select(projects)
        assert result in projects

    def test_weights_favor_easy_urgent(self) -> None:
        # Create projects with different priorities
        easy_urgent = Project.create(
            title="EasyUrgent",
            brief="B",
            spec="S",
            tech_stack=[],
            urgency=1,
            difficulty=1,
        )
        hard_not_urgent = Project.create(
            title="HardNotUrgent",
            brief="B",
            spec="S",
            tech_stack=[],
            urgency=4,
            difficulty=4,
        )

        # Run many selections and count
        counts = {"EasyUrgent": 0, "HardNotUrgent": 0}
        for _ in range(1000):
            result = weighted_random_select([easy_urgent, hard_not_urgent])
            counts[result.title] += 1

        # Easy+urgent should be selected much more often
        # Weight ratio is 7:1 (score 8 vs 2, weight = 9 - score)
        assert counts["EasyUrgent"] > counts["HardNotUrgent"] * 3

    def test_equal_priority_roughly_equal_selection(self) -> None:
        p1 = Project.create(
            title="P1",
            brief="B",
            spec="S",
            tech_stack=[],
            urgency=2,
            difficulty=2,
        )
        p2 = Project.create(
            title="P2",
            brief="B",
            spec="S",
            tech_stack=[],
            urgency=2,
            difficulty=2,
        )

        counts = {"P1": 0, "P2": 0}
        for _ in range(1000):
            result = weighted_random_select([p1, p2])
            counts[result.title] += 1

        # Should be roughly 50/50 (within reasonable variance)
        assert 350 < counts["P1"] < 650
        assert 350 < counts["P2"] < 650


class TestSelect:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def populated_registry(self, temp_dir: Path) -> RegistryManager:
        manager = RegistryManager(temp_dir)

        # Add projects with different statuses
        idea1 = Project.create(title="Idea1", brief="B", spec="S", tech_stack=[])
        idea2 = Project.create(title="Idea2", brief="B", spec="S", tech_stack=[])
        in_progress = Project.create(title="InProgress", brief="B", spec="S", tech_stack=[])
        blocked = Project.create(title="Blocked", brief="B", spec="S", tech_stack=[])

        manager.add(idea1)
        manager.add(idea2)
        manager.add(in_progress)
        manager.add(blocked)

        manager.update(in_progress.id, status="in_progress")
        manager.update(blocked.id, status="blocked")

        return manager

    def test_select_ideas_only(self, temp_dir: Path, populated_registry: RegistryManager) -> None:
        with patch("selector.get_registry_dir", return_value=temp_dir):
            result = select([Status.IDEA])
            assert result is not None
            assert result.status == Status.IDEA
            assert result.title in ["Idea1", "Idea2"]

    def test_select_in_progress(self, temp_dir: Path, populated_registry: RegistryManager) -> None:
        with patch("selector.get_registry_dir", return_value=temp_dir):
            result = select([Status.IN_PROGRESS])
            assert result is not None
            assert result.title == "InProgress"

    def test_select_blocked(self, temp_dir: Path, populated_registry: RegistryManager) -> None:
        with patch("selector.get_registry_dir", return_value=temp_dir):
            result = select([Status.BLOCKED])
            assert result is not None
            assert result.title == "Blocked"

    def test_select_multiple_statuses(
        self, temp_dir: Path, populated_registry: RegistryManager
    ) -> None:
        with patch("selector.get_registry_dir", return_value=temp_dir):
            result = select([Status.IDEA, Status.IN_PROGRESS])
            assert result is not None
            assert result.title in ["Idea1", "Idea2", "InProgress"]

    def test_select_no_matches(self, temp_dir: Path, populated_registry: RegistryManager) -> None:
        with patch("selector.get_registry_dir", return_value=temp_dir):
            result = select([Status.COMPLETED])
            assert result is None

    def test_select_unlocked_only(
        self, temp_dir: Path, populated_registry: RegistryManager
    ) -> None:
        # Lock one idea
        ideas = populated_registry.list(status_filter=[Status.IDEA])
        populated_registry.lock(ideas[0].id, "worker-1")

        with patch("selector.get_registry_dir", return_value=temp_dir):
            # Should only get the unlocked idea
            results = []
            for _ in range(20):
                result = select([Status.IDEA], unlocked_only=True)
                if result:
                    results.append(result.title)

            # All results should be the unlocked one
            assert all(title != ideas[0].title for title in results)

    def test_select_empty_registry(self, temp_dir: Path) -> None:
        RegistryManager(temp_dir)  # Create empty registry
        with patch("selector.get_registry_dir", return_value=temp_dir):
            result = select([Status.IDEA])
            assert result is None
