"""Tests for project_utils module - 100% coverage required."""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from project_utils import (
    create_blocker,
    create_wrap_up,
    get_blocker_content,
    get_latest_wrap_up,
    get_project_dir,
    get_unique_project_dir,
    init_git_repo,
    init_project_dir,
    remove_blocker,
    slugify,
)
from registry import Project


class TestSlugify:
    def test_simple_title(self) -> None:
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self) -> None:
        assert slugify("Test! @#$ Project") == "test-project"

    def test_multiple_spaces(self) -> None:
        assert slugify("Multiple   Spaces   Here") == "multiple-spaces-here"

    def test_leading_trailing_hyphens(self) -> None:
        assert slugify("---Test Project---") == "test-project"

    def test_long_title_truncation(self) -> None:
        long_title = "A" * 100
        result = slugify(long_title)
        assert len(result) <= 50

    def test_mixed_case(self) -> None:
        assert slugify("CamelCaseTitle") == "camelcasetitle"

    def test_numbers(self) -> None:
        assert slugify("Project 123 Test") == "project-123-test"

    def test_underscores(self) -> None:
        assert slugify("test_project_name") == "test-project-name"


class TestInitProjectDir:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def project(self) -> Project:
        return Project.create(
            title="Test Project",
            brief="A test project",
            spec="Full specification here",
            tech_stack=["Python", "Flask"],
            urgency=2,
            difficulty=3,
        )

    def test_creates_directory_structure(self, temp_dir: Path, project: Project) -> None:
        project_dir = init_project_dir(project, temp_dir)

        assert project_dir.exists()
        assert (project_dir / "src").exists()
        assert (project_dir / "tests").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "DESIGN.md").exists()
        assert (project_dir / "CHANGELOG.md").exists()

    def test_readme_content(self, temp_dir: Path, project: Project) -> None:
        project_dir = init_project_dir(project, temp_dir)
        readme = (project_dir / "README.md").read_text()

        assert project.title in readme
        assert project.spec in readme
        assert "Python" in readme
        assert "Flask" in readme
        assert project.brief in readme

    def test_design_md_content(self, temp_dir: Path, project: Project) -> None:
        project_dir = init_project_dir(project, temp_dir)
        design = (project_dir / "DESIGN.md").read_text()

        assert "Design Decisions" in design
        assert project.brief in design

    def test_changelog_content(self, temp_dir: Path, project: Project) -> None:
        project_dir = init_project_dir(project, temp_dir)
        changelog = (project_dir / "CHANGELOG.md").read_text()

        assert "Changelog" in changelog
        assert "Project Created" in changelog

    def test_directory_naming(self, temp_dir: Path, project: Project) -> None:
        project_dir = init_project_dir(project, temp_dir)
        assert project_dir.name == "test-project"


class TestBlocker:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_create_blocker(self, temp_dir: Path) -> None:
        blocker_path = create_blocker(temp_dir, "Database connection failing")

        assert blocker_path.exists()
        content = blocker_path.read_text()
        assert "Database connection failing" in content
        assert "Issue Description" in content

    def test_get_blocker_content(self, temp_dir: Path) -> None:
        create_blocker(temp_dir, "Test blocker reason")
        content = get_blocker_content(temp_dir)

        assert content is not None
        assert "Test blocker reason" in content

    def test_get_blocker_content_none(self, temp_dir: Path) -> None:
        content = get_blocker_content(temp_dir)
        assert content is None

    def test_remove_blocker(self, temp_dir: Path) -> None:
        create_blocker(temp_dir, "To be removed")
        assert (temp_dir / "blocker.md").exists()

        result = remove_blocker(temp_dir)
        assert result is True
        assert not (temp_dir / "blocker.md").exists()

    def test_remove_nonexistent_blocker(self, temp_dir: Path) -> None:
        result = remove_blocker(temp_dir)
        assert result is False


class TestWrapUp:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_create_wrap_up(self, temp_dir: Path) -> None:
        wrap_up_path = create_wrap_up(temp_dir, "Work completed on feature X")

        assert wrap_up_path.exists()
        assert wrap_up_path.parent.name == "wrap-up"
        content = wrap_up_path.read_text()
        assert "Work completed on feature X" in content

    def test_wrap_up_directory_created(self, temp_dir: Path) -> None:
        create_wrap_up(temp_dir, "Summary")
        assert (temp_dir / "wrap-up").is_dir()

    def test_get_latest_wrap_up(self, temp_dir: Path) -> None:
        create_wrap_up(temp_dir, "First wrap-up")
        content = get_latest_wrap_up(temp_dir)

        assert content is not None
        assert "First wrap-up" in content

    def test_get_latest_wrap_up_none(self, temp_dir: Path) -> None:
        content = get_latest_wrap_up(temp_dir)
        assert content is None

    def test_get_latest_wrap_up_empty_dir(self, temp_dir: Path) -> None:
        (temp_dir / "wrap-up").mkdir()
        content = get_latest_wrap_up(temp_dir)
        assert content is None


class TestInitGitRepo:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_init_git_repo_success(self, temp_dir: Path) -> None:
        # Create a file so we have something to commit
        (temp_dir / "test.txt").write_text("test")

        result = init_git_repo(temp_dir)

        assert result is True
        assert (temp_dir / ".git").is_dir()
        assert (temp_dir / ".gitignore").exists()

    def test_gitignore_content(self, temp_dir: Path) -> None:
        (temp_dir / "test.txt").write_text("test")
        init_git_repo(temp_dir)

        gitignore = (temp_dir / ".gitignore").read_text()
        assert "__pycache__" in gitignore
        assert ".venv" in gitignore
        assert ".digitus-registry.json" in gitignore


class TestGetProjectDir:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def project(self) -> Project:
        return Project.create(
            title="My Test Project",
            brief="B",
            spec="S",
            tech_stack=[],
        )

    def test_get_project_dir(self, temp_dir: Path, project: Project) -> None:
        result = get_project_dir(project, temp_dir)
        assert result == temp_dir / "my-test-project"

    def test_get_project_dir_existing_base(self, temp_dir: Path, project: Project) -> None:
        (temp_dir / "my-test-project").mkdir()
        result = get_project_dir(project, temp_dir)
        assert result == temp_dir / "my-test-project"

    def test_get_project_dir_numbered_variant(self, temp_dir: Path, project: Project) -> None:
        # Base doesn't exist, but numbered variant does
        (temp_dir / "my-test-project-2").mkdir()
        result = get_project_dir(project, temp_dir)
        assert result == temp_dir / "my-test-project-2"


class TestGetUniqueProjectDir:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_unique_dir_no_collision(self, temp_dir: Path) -> None:
        result = get_unique_project_dir("test-project", temp_dir)
        assert result == temp_dir / "test-project"

    def test_unique_dir_with_collision(self, temp_dir: Path) -> None:
        (temp_dir / "test-project").mkdir()
        result = get_unique_project_dir("test-project", temp_dir)
        assert result == temp_dir / "test-project-2"

    def test_unique_dir_multiple_collisions(self, temp_dir: Path) -> None:
        (temp_dir / "test-project").mkdir()
        (temp_dir / "test-project-2").mkdir()
        (temp_dir / "test-project-3").mkdir()
        result = get_unique_project_dir("test-project", temp_dir)
        assert result == temp_dir / "test-project-4"

    def test_unique_dir_too_many_collisions(self, temp_dir: Path) -> None:
        for i in range(100):
            suffix = "" if i == 0 else f"-{i + 1}"
            (temp_dir / f"test-project{suffix}").mkdir()
        with pytest.raises(ValueError, match="Too many projects"):
            get_unique_project_dir("test-project", temp_dir)


class TestInitProjectDirCollision:
    @pytest.fixture
    def temp_dir(self) -> Path:
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    def test_collision_creates_unique_dir(self, temp_dir: Path) -> None:
        project1 = Project.create(title="Test", brief="B", spec="S", tech_stack=[])
        project2 = Project.create(title="Test!", brief="B", spec="S", tech_stack=[])

        dir1 = init_project_dir(project1, temp_dir)
        dir2 = init_project_dir(project2, temp_dir)

        assert dir1.name == "test"
        assert dir2.name == "test-2"
        assert dir1 != dir2
