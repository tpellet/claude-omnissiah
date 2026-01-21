"""Tests for session hook scripts (lock_project, unlock_project)."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from registry import Project, RegistryManager


class TestLockProject:
    @pytest.fixture
    def temp_registry(self) -> tuple[Path, RegistryManager]:
        with tempfile.TemporaryDirectory() as d:
            registry_dir = Path(d)
            manager = RegistryManager(registry_dir)
            yield registry_dir, manager

    @pytest.fixture
    def project_in_registry(
        self, temp_registry: tuple[Path, RegistryManager]
    ) -> tuple[Path, RegistryManager, Project]:
        registry_dir, manager = temp_registry
        p = Project.create(title="Test", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        return registry_dir, manager, p

    def test_locks_project_when_env_vars_set(
        self, project_in_registry: tuple[Path, RegistryManager, Project]
    ) -> None:
        registry_dir, manager, project = project_in_registry

        env = {
            "DIGITUS_PROJECT_ID": project.id,
            "CLAUDE_SESSION_ID": "test-session-123",
        }

        with patch.dict(os.environ, env, clear=False):
            with patch("registry.get_registry_dir", return_value=registry_dir):
                import importlib

                import lock_project

                importlib.reload(lock_project)
                lock_project.main()

        updated = manager.get(project.id)
        assert updated is not None
        assert updated.locked_by == "test-session-123"

    def test_no_action_when_no_project_id(
        self, project_in_registry: tuple[Path, RegistryManager, Project]
    ) -> None:
        registry_dir, manager, project = project_in_registry

        env = {"CLAUDE_SESSION_ID": "test-session-123"}

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import lock_project

            importlib.reload(lock_project)
            lock_project.main()

        updated = manager.get(project.id)
        assert updated is not None
        assert updated.locked_by is None

    def test_no_action_when_no_session_id(
        self, project_in_registry: tuple[Path, RegistryManager, Project]
    ) -> None:
        registry_dir, manager, project = project_in_registry

        env = {"DIGITUS_PROJECT_ID": project.id}

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import lock_project

            importlib.reload(lock_project)
            lock_project.main()

        updated = manager.get(project.id)
        assert updated is not None
        assert updated.locked_by is None

    def test_handles_missing_config(self, capsys: pytest.CaptureFixture) -> None:
        env = {
            "DIGITUS_PROJECT_ID": "test-id",
            "CLAUDE_SESSION_ID": "test-session",
        }

        with patch.dict(os.environ, env, clear=False):
            with patch("registry.get_registry_dir", side_effect=FileNotFoundError("No config")):
                import importlib

                import lock_project

                importlib.reload(lock_project)
                lock_project.main()

        # Should not raise, just silently pass
        captured = capsys.readouterr()
        assert "Error" not in captured.err

    def test_handles_unexpected_error(self, capsys: pytest.CaptureFixture) -> None:
        env = {
            "DIGITUS_PROJECT_ID": "test-id",
            "CLAUDE_SESSION_ID": "test-session",
        }

        with patch.dict(os.environ, env, clear=False):
            with patch("registry.get_registry_dir", side_effect=RuntimeError("Unexpected")):
                import importlib

                import lock_project

                importlib.reload(lock_project)
                lock_project.main()

        captured = capsys.readouterr()
        assert "Error locking project" in captured.err


class TestUnlockProject:
    @pytest.fixture
    def temp_registry(self) -> tuple[Path, RegistryManager]:
        with tempfile.TemporaryDirectory() as d:
            registry_dir = Path(d)
            manager = RegistryManager(registry_dir)
            yield registry_dir, manager

    @pytest.fixture
    def locked_project(
        self, temp_registry: tuple[Path, RegistryManager]
    ) -> tuple[Path, RegistryManager, Project]:
        registry_dir, manager = temp_registry
        p = Project.create(title="Locked", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        manager.lock(p.id, "session-to-unlock")
        return registry_dir, manager, p

    def test_unlocks_project_for_session(
        self, locked_project: tuple[Path, RegistryManager, Project]
    ) -> None:
        registry_dir, manager, project = locked_project

        env = {"CLAUDE_SESSION_ID": "session-to-unlock"}

        with patch.dict(os.environ, env, clear=False):
            with patch("registry.get_registry_dir", return_value=registry_dir):
                import importlib

                import unlock_project

                importlib.reload(unlock_project)
                unlock_project.main()

        updated = manager.get(project.id)
        assert updated is not None
        assert updated.locked_by is None

    def test_no_action_when_no_session_id(
        self, locked_project: tuple[Path, RegistryManager, Project]
    ) -> None:
        registry_dir, manager, project = locked_project

        with patch.dict(os.environ, {}, clear=True):
            import importlib

            import unlock_project

            importlib.reload(unlock_project)
            unlock_project.main()

        updated = manager.get(project.id)
        assert updated is not None
        assert updated.locked_by == "session-to-unlock"

    def test_does_not_unlock_other_sessions(
        self, locked_project: tuple[Path, RegistryManager, Project]
    ) -> None:
        registry_dir, manager, project = locked_project

        env = {"CLAUDE_SESSION_ID": "different-session"}

        with patch.dict(os.environ, env, clear=False):
            with patch("registry.get_registry_dir", return_value=registry_dir):
                import importlib

                import unlock_project

                importlib.reload(unlock_project)
                unlock_project.main()

        updated = manager.get(project.id)
        assert updated is not None
        assert updated.locked_by == "session-to-unlock"
