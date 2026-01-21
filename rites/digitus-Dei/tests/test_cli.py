"""Tests for CLI main functions - 100% coverage required."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestRegistryCLI:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mock_registry_dir(self, temp_dir: Path):
        with patch("registry.get_registry_dir", return_value=temp_dir):
            yield temp_dir

    def test_main_no_args(self, capsys: pytest.CaptureFixture, mock_registry_dir: Path) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc, patch("sys.argv", ["registry.py"]):
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    def test_main_list(self, capsys: pytest.CaptureFixture, mock_registry_dir: Path) -> None:
        from registry import main

        with patch("sys.argv", ["registry.py", "list"]):
            main()
        captured = capsys.readouterr()
        assert "[]" in captured.out

    def test_main_list_with_status(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager, main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Test", brief="B", spec="S", tech_stack=[])
        manager.add(p)

        with patch("sys.argv", ["registry.py", "list", "--status=idea"]):
            main()
        captured = capsys.readouterr()
        assert "Test" in captured.out

    def test_main_list_unlocked(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager, main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Test", brief="B", spec="S", tech_stack=[])
        manager.add(p)

        with patch("sys.argv", ["registry.py", "list", "--unlocked"]):
            main()
        captured = capsys.readouterr()
        assert "Test" in captured.out

    def test_main_get(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager, main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Find Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)

        with patch("sys.argv", ["registry.py", "get", p.id]):
            main()
        captured = capsys.readouterr()
        assert "Find Me" in captured.out

    def test_main_get_not_found(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["registry.py", "get", "nonexistent"]):
                main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_main_get_no_id(self, mock_registry_dir: Path, capsys: pytest.CaptureFixture) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc, patch("sys.argv", ["registry.py", "get"]):
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    def test_main_add(self, mock_registry_dir: Path, capsys: pytest.CaptureFixture) -> None:
        from registry import main

        data = json.dumps(
            {
                "title": "New Project",
                "brief": "Brief",
                "spec": "Spec",
                "tech_stack": ["Python"],
            }
        )
        with patch("sys.argv", ["registry.py", "add"]):
            with patch("sys.stdin.read", return_value=data):
                main()
        captured = capsys.readouterr()
        assert "New Project" in captured.out

    def test_main_add_with_file(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        data = {
            "title": "File Project",
            "brief": "Brief with\nnewlines",
            "spec": "Multi-line\nspec—with em-dash",
            "tech_stack": ["Python", "Flutter"],
        }
        json_file = temp_dir / "project.json"
        json_file.write_text(json.dumps(data))

        with patch("sys.argv", ["registry.py", "add", f"--file={json_file}"]):
            main()
        captured = capsys.readouterr()
        assert "File Project" in captured.out
        assert "em-dash" in captured.out

    def test_main_update(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager, main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Update Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)

        data = json.dumps({"status": "in_progress"})
        with patch("sys.argv", ["registry.py", "update", p.id]):
            with patch("sys.stdin.read", return_value=data):
                main()
        captured = capsys.readouterr()
        assert "in_progress" in captured.out

    def test_main_update_no_id(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc, patch("sys.argv", ["registry.py", "update"]):
            main()
        assert exc.value.code == 1

    def test_main_update_not_found(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["registry.py", "update", "nonexistent"]):
                with patch("sys.stdin.read", return_value="{}"):
                    main()
        assert exc.value.code == 1

    def test_main_lock(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager, main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Lock Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)

        with patch("sys.argv", ["registry.py", "lock", p.id, "worker-1"]):
            main()
        captured = capsys.readouterr()
        assert "worker-1" in captured.out

    def test_main_lock_no_args(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc, patch("sys.argv", ["registry.py", "lock"]):
            main()
        assert exc.value.code == 1

    def test_main_lock_not_found(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["registry.py", "lock", "nonexistent", "worker"]):
                main()
        assert exc.value.code == 1

    def test_main_unlock(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager, main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Unlock Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        manager.lock(p.id, "worker-1")

        with patch("sys.argv", ["registry.py", "unlock", p.id]):
            main()
        captured = capsys.readouterr()
        assert "locked_by" in captured.out

    def test_main_unlock_no_id(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc, patch("sys.argv", ["registry.py", "unlock"]):
            main()
        assert exc.value.code == 1

    def test_main_unlock_not_found(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["registry.py", "unlock", "nonexistent"]):
                main()
        assert exc.value.code == 1

    def test_main_unlock_worker(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager, main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Test", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        manager.lock(p.id, "worker-1")

        with patch("sys.argv", ["registry.py", "unlock-worker", "worker-1"]):
            main()
        captured = capsys.readouterr()
        assert "Unlocked 1" in captured.out

    def test_main_unlock_worker_no_id(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["registry.py", "unlock-worker"]):
                main()
        assert exc.value.code == 1

    def test_main_delete(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager, main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Delete Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)

        with patch("sys.argv", ["registry.py", "delete", p.id]):
            main()
        captured = capsys.readouterr()
        assert "Deleted" in captured.out

    def test_main_delete_no_id(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc, patch("sys.argv", ["registry.py", "delete"]):
            main()
        assert exc.value.code == 1

    def test_main_delete_not_found(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["registry.py", "delete", "nonexistent"]):
                main()
        assert exc.value.code == 1

    def test_main_unknown_command(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["registry.py", "unknown"]):
                main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Unknown command" in captured.err


class TestGetRegistryDir:
    def test_missing_config(self, tmp_path: Path) -> None:
        from registry import get_registry_dir

        with patch.object(Path, "home", return_value=tmp_path):
            with pytest.raises(FileNotFoundError, match="Config not found"):
                get_registry_dir()

    def test_missing_registry_dir_key(self, tmp_path: Path) -> None:
        from registry import get_registry_dir

        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "digitus-Dei.local.md").write_text("---\nother: value\n---")

        with patch.object(Path, "home", return_value=tmp_path):
            with pytest.raises(ValueError, match="registry_dir not found"):
                get_registry_dir()

    def test_valid_config(self, tmp_path: Path) -> None:
        from registry import get_registry_dir

        registry_dir = tmp_path / "my-projects"
        registry_dir.mkdir()
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "digitus-Dei.local.md").write_text(
            f"---\nregistry_dir: {registry_dir}\n---"
        )

        with patch.object(Path, "home", return_value=tmp_path):
            result = get_registry_dir()
            assert result == registry_dir


class TestSelectorCLI:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mock_registry_dir(self, temp_dir: Path):
        with patch("selector.get_registry_dir", return_value=temp_dir):
            yield temp_dir

    def test_main_no_args(self, capsys: pytest.CaptureFixture) -> None:
        from selector import main

        with pytest.raises(SystemExit) as exc, patch("sys.argv", ["selector.py"]):
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    def test_main_no_status(self, capsys: pytest.CaptureFixture) -> None:
        from selector import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["selector.py", "--unlocked"]):
                main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "--status is required" in captured.err

    def test_main_with_status(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager
        from selector import main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Select Me", brief="B", spec="S", tech_stack=[])
        manager.add(p)

        with patch("sys.argv", ["selector.py", "--status=idea"]):
            main()
        captured = capsys.readouterr()
        assert "Select Me" in captured.out

    def test_main_no_match(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import RegistryManager
        from selector import main

        RegistryManager(temp_dir)  # Create empty registry

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["selector.py", "--status=idea"]):
                main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "No matching projects found" in captured.err


class TestProjectUtilsCLI:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mock_registry_dir(self, temp_dir: Path):
        with patch("registry.get_projects_dir", return_value=temp_dir):
            yield temp_dir

    def test_main_no_args(self, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc, patch("sys.argv", ["project_utils.py"]):
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    def test_main_init(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main
        from registry import Project

        p = Project.create(title="Init Project", brief="B", spec="S", tech_stack=["Python"])
        data = json.dumps(p.to_dict())

        with patch("sys.argv", ["project_utils.py", "init"]):
            with patch("sys.stdin.read", return_value=data):
                main()
        captured = capsys.readouterr()
        assert "init-project" in captured.out

    def test_main_github(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main

        project_dir = temp_dir / "test-project"
        project_dir.mkdir()
        (project_dir / "test.txt").write_text("test")

        # Mock gh command
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="https://github.com/test/test",
                stderr="",
                returncode=0,
            )
            with patch("sys.argv", ["project_utils.py", "github", str(project_dir)]):
                main()
        captured = capsys.readouterr()
        assert "github.com" in captured.out

    def test_main_github_no_dir(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "github"]):
                main()
        assert exc.value.code == 1

    def test_main_github_fail(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "gh")
            with pytest.raises(SystemExit) as exc:
                with patch("sys.argv", ["project_utils.py", "github", str(temp_dir)]):
                    main()
            assert exc.value.code == 1

    def test_main_blocker(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main

        with patch("sys.argv", ["project_utils.py", "blocker", str(temp_dir)]):
            with patch("sys.stdin.read", return_value="Test blocker"):
                main()
        captured = capsys.readouterr()
        assert "blocker.md" in captured.out

    def test_main_blocker_no_dir(
        self, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "blocker"]):
                main()
        assert exc.value.code == 1

    def test_main_remove_blocker(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import create_blocker, main

        create_blocker(temp_dir, "To remove")

        with patch("sys.argv", ["project_utils.py", "remove-blocker", str(temp_dir)]):
            main()
        captured = capsys.readouterr()
        assert "Removed" in captured.out

    def test_main_remove_blocker_not_found(
        self, temp_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main

        with patch("sys.argv", ["project_utils.py", "remove-blocker", str(temp_dir)]):
            main()
        captured = capsys.readouterr()
        assert "No blocker" in captured.out

    def test_main_remove_blocker_no_dir(self, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "remove-blocker"]):
                main()
        assert exc.value.code == 1

    def test_main_wrap_up(self, temp_dir: Path, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with patch("sys.argv", ["project_utils.py", "wrap-up", str(temp_dir)]):
            with patch("sys.stdin.read", return_value="Summary"):
                main()
        captured = capsys.readouterr()
        assert "wrap-up" in captured.out

    def test_main_wrap_up_no_dir(self, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "wrap-up"]):
                main()
        assert exc.value.code == 1

    def test_main_get_wrap_up(self, temp_dir: Path, capsys: pytest.CaptureFixture) -> None:
        from project_utils import create_wrap_up, main

        create_wrap_up(temp_dir, "Test summary")

        with patch("sys.argv", ["project_utils.py", "get-wrap-up", str(temp_dir)]):
            main()
        captured = capsys.readouterr()
        assert "Test summary" in captured.out

    def test_main_get_wrap_up_not_found(
        self, temp_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "get-wrap-up", str(temp_dir)]):
                main()
        assert exc.value.code == 1

    def test_main_get_wrap_up_no_dir(self, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "get-wrap-up"]):
                main()
        assert exc.value.code == 1

    def test_main_get_blocker(self, temp_dir: Path, capsys: pytest.CaptureFixture) -> None:
        from project_utils import create_blocker, main

        create_blocker(temp_dir, "Test blocker content")

        with patch("sys.argv", ["project_utils.py", "get-blocker", str(temp_dir)]):
            main()
        captured = capsys.readouterr()
        assert "Test blocker content" in captured.out

    def test_main_get_blocker_not_found(
        self, temp_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "get-blocker", str(temp_dir)]):
                main()
        assert exc.value.code == 1

    def test_main_get_blocker_no_dir(self, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "get-blocker"]):
                main()
        assert exc.value.code == 1

    def test_main_slugify(self, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with patch("sys.argv", ["project_utils.py", "slugify", "Test Project"]):
            main()
        captured = capsys.readouterr()
        assert "test-project" in captured.out

    def test_main_slugify_no_title(self, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "slugify"]):
                main()
        assert exc.value.code == 1

    def test_main_unknown_command(self, capsys: pytest.CaptureFixture) -> None:
        from project_utils import main

        with pytest.raises(SystemExit) as exc:
            with patch("sys.argv", ["project_utils.py", "unknown"]):
                main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Unknown command" in captured.err


class TestUnlockProjectCLI:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mock_registry_dir(self, temp_dir: Path):
        with patch("unlock_project.get_registry_dir", return_value=temp_dir):
            yield temp_dir

    def test_main_no_session(self, capsys: pytest.CaptureFixture) -> None:
        from unlock_project import main

        with patch.dict(os.environ, {}, clear=True):
            if "CLAUDE_SESSION_ID" in os.environ:
                del os.environ["CLAUDE_SESSION_ID"]
            main()
        captured = capsys.readouterr()
        assert "No CLAUDE_SESSION_ID" in captured.out

    def test_main_with_session(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from registry import Project, RegistryManager
        from unlock_project import main

        manager = RegistryManager(temp_dir)
        p = Project.create(title="Test", brief="B", spec="S", tech_stack=[])
        manager.add(p)
        manager.lock(p.id, "session-123")

        with patch.dict(os.environ, {"CLAUDE_SESSION_ID": "session-123"}):
            main()
        captured = capsys.readouterr()
        assert "Unlocked 1" in captured.out

    def test_main_no_config(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        from unlock_project import main

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"CLAUDE_SESSION_ID": "session-123"}):
                main()  # Should not raise, just pass

    def test_main_with_error(
        self, temp_dir: Path, mock_registry_dir: Path, capsys: pytest.CaptureFixture
    ) -> None:
        from unlock_project import main

        with patch.dict(os.environ, {"CLAUDE_SESSION_ID": "session-123"}):
            with patch("unlock_project.RegistryManager") as mock:
                mock.side_effect = Exception("Test error")
                main()
        captured = capsys.readouterr()
        assert "Error" in captured.err


class TestCreateGithubRepo:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_create_github_repo_success(self, temp_dir: Path) -> None:
        from project_utils import create_github_repo

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="",
                stderr="https://github.com/test/repo\n",
                returncode=0,
            )
            result = create_github_repo(temp_dir)
            assert result is not None
            assert "github.com" in result

    def test_create_github_repo_failure(self, temp_dir: Path) -> None:
        from project_utils import create_github_repo

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "gh")
            result = create_github_repo(temp_dir)
            assert result is None

    def test_create_github_repo_url_in_view(self, temp_dir: Path) -> None:
        from project_utils import create_github_repo

        # First call (create) has no URL, second call (view) returns URL
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(stdout="Created", stderr="", returncode=0),
                MagicMock(stdout="https://github.com/test/repo2", stderr="", returncode=0),
            ]
            result = create_github_repo(temp_dir)
            assert result == "https://github.com/test/repo2"


class TestInitGitRepoFailure:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_init_git_repo_failure(self, temp_dir: Path) -> None:
        from project_utils import init_git_repo

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")
            result = init_git_repo(temp_dir)
            assert result is False
