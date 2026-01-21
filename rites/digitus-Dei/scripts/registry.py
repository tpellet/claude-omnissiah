#!/usr/bin/env python3
"""Registry operations for digitus-Dei project management."""

import fcntl
import json
import os
import sys
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, cast


class Status(str, Enum):
    IDEA = "idea"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    BLOCKED = "blocked"
    ABANDONED = "abandoned"
    COMPLETED = "completed"


@dataclass
class Priority:
    urgency: int = 2
    difficulty: int = 2

    def __post_init__(self) -> None:
        if not 1 <= self.urgency <= 4:
            raise ValueError(f"urgency must be 1-4, got {self.urgency}")
        if not 1 <= self.difficulty <= 4:
            raise ValueError(f"difficulty must be 1-4, got {self.difficulty}")

    def score(self) -> int:
        """Lower score = higher priority (easy + urgent first)."""
        return (5 - self.urgency) + (5 - self.difficulty)


@dataclass
class Project:
    id: str
    title: str
    brief: str
    spec: str
    status: Status
    priority: Priority
    tech_stack: list[str]
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    repo_url: str | None = None
    locked_by: str | None = None
    locked_at: str | None = None
    blocked_reason: str | None = None

    @classmethod
    def create(
        cls,
        title: str,
        brief: str,
        spec: str,
        tech_stack: list[str],
        urgency: int = 2,
        difficulty: int = 2,
    ) -> "Project":
        return cls(
            id=str(uuid.uuid4())[:8],
            title=title,
            brief=brief,
            spec=spec,
            status=Status.IDEA,
            priority=Priority(urgency=urgency, difficulty=difficulty),
            tech_stack=tech_stack,
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        data = data.copy()
        data["status"] = Status(data["status"])
        data["priority"] = Priority(**data["priority"])
        return cls(**data)


@dataclass
class Registry:
    version: str = "1.0.0"
    projects: list[Project] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "projects": [p.to_dict() for p in self.projects],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Registry":
        return cls(
            version=data.get("version", "1.0.0"),
            projects=[Project.from_dict(p) for p in data.get("projects", [])],
        )


class RegistryManager:
    """Manages the project registry file with file locking for concurrency safety."""

    def __init__(self, registry_dir: str | Path) -> None:
        self.registry_dir = Path(registry_dir)
        self.registry_path = self.registry_dir / ".digitus-registry.json"

    def _load(self) -> Registry:
        try:
            with open(self.registry_path) as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    return Registry.from_dict(json.load(f))
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except FileNotFoundError:
            return Registry()

    def _save(self, registry: Registry) -> None:
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        # Atomic write: write to temp file, then rename
        fd, tmp_path = tempfile.mkstemp(dir=self.registry_dir, prefix=".registry-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(registry.to_dict(), f, indent=2)
            Path(tmp_path).rename(self.registry_path)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def add(self, project: Project) -> Project:
        registry = self._load()
        registry.projects.append(project)
        self._save(registry)
        return project

    def get(self, project_id: str) -> Project | None:
        registry = self._load()
        for p in registry.projects:
            if p.id == project_id:
                return p
        return None

    def list(
        self,
        status_filter: list[Status] | None = None,
        unlocked_only: bool = False,
    ) -> list[Project]:
        registry = self._load()
        projects = registry.projects

        if status_filter:
            projects = [p for p in projects if p.status in status_filter]

        if unlocked_only:
            projects = [p for p in projects if p.locked_by is None]

        return projects

    def update(self, project_id: str, **fields: Any) -> Project | None:
        registry = self._load()
        for i, p in enumerate(registry.projects):
            if p.id == project_id:
                data = p.to_dict()
                for key, value in fields.items():
                    if key == "status" and isinstance(value, str):
                        value = Status(value)
                    if key == "priority" and isinstance(value, dict):
                        value = Priority(**value)
                    if key in data:
                        data[key] = (
                            value
                            if not isinstance(value, (Status, Priority))
                            else (value.value if isinstance(value, Status) else asdict(value))
                        )
                registry.projects[i] = Project.from_dict(data)
                self._save(registry)
                return registry.projects[i]
        return None

    def lock(self, project_id: str, worker_id: str) -> Project | None:
        return self.update(
            project_id,
            locked_by=worker_id,
            locked_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def unlock(self, project_id: str) -> Project | None:
        return self.update(project_id, locked_by=None, locked_at=None)

    def unlock_all_by_worker(self, worker_id: str) -> int:
        registry = self._load()
        count = 0
        for p in registry.projects:
            if p.locked_by == worker_id:
                p.locked_by = None
                p.locked_at = None
                count += 1
        if count > 0:
            self._save(registry)
        return count

    def delete(self, project_id: str) -> bool:
        registry = self._load()
        initial_count = len(registry.projects)
        registry.projects = [p for p in registry.projects if p.id != project_id]
        if len(registry.projects) < initial_count:
            self._save(registry)
            return True
        return False


def _read_json_input(args: list[str]) -> dict[str, Any]:
    """Read JSON from --file argument or stdin."""
    for arg in args:
        if arg.startswith("--file="):
            file_path = Path(arg.split("=", 1)[1])
            return cast(dict[str, Any], json.loads(file_path.read_text()))
    return cast(dict[str, Any], json.loads(sys.stdin.read()))


def get_registry_dir() -> Path:
    """Get registry directory from config file.

    This is the hidden directory where the registry file is stored.
    Projects are created in the parent directory (see get_projects_dir).
    """
    config_path = Path.home() / ".claude" / "digitus-Dei.local.md"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config not found: {config_path}\n"
            "Create it with:\n"
            "---\n"
            "registry_dir: /path/to/projects/.digitus-dei\n"
            "---"
        )

    content = config_path.read_text()
    for line in content.split("\n"):
        if line.startswith("registry_dir:"):
            return Path(line.split(":", 1)[1].strip())

    raise ValueError("registry_dir not found in config")


def get_projects_dir() -> Path:
    """Get projects directory (parent of registry_dir).

    Projects are created at the top level to avoid sandbox issues.
    Registry file stays in the hidden .digitus-dei directory.
    """
    return get_registry_dir().parent


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: registry.py <command> [args]")
        print("Commands: add, get, list, update, lock, unlock, unlock-worker, delete")
        sys.exit(1)

    cmd = sys.argv[1]
    manager = RegistryManager(get_registry_dir())

    if cmd == "list":
        status_filter = None
        unlocked_only = False
        for arg in sys.argv[2:]:
            if arg.startswith("--status="):
                statuses = arg.split("=")[1].split(",")
                status_filter = [Status(s) for s in statuses]
            elif arg == "--unlocked":
                unlocked_only = True

        projects = manager.list(status_filter, unlocked_only)
        print(json.dumps([p.to_dict() for p in projects], indent=2))

    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: registry.py get <id>")
            sys.exit(1)
        project = manager.get(sys.argv[2])
        if project:
            print(json.dumps(project.to_dict(), indent=2))
        else:
            print("Project not found", file=sys.stderr)
            sys.exit(1)

    elif cmd == "add":
        data = _read_json_input(sys.argv[2:])
        project = Project.create(**data)
        manager.add(project)
        print(json.dumps(project.to_dict(), indent=2))

    elif cmd == "update":
        if len(sys.argv) < 3:
            print("Usage: registry.py update <id> [--file=path] < json_fields")
            sys.exit(1)
        fields = _read_json_input(sys.argv[3:])
        project = manager.update(sys.argv[2], **fields)
        if project:
            print(json.dumps(project.to_dict(), indent=2))
        else:
            print("Project not found", file=sys.stderr)
            sys.exit(1)

    elif cmd == "lock":
        if len(sys.argv) < 4:
            print("Usage: registry.py lock <id> <worker_id>")
            sys.exit(1)
        project = manager.lock(sys.argv[2], sys.argv[3])
        if project:
            print(json.dumps(project.to_dict(), indent=2))
        else:
            print("Project not found", file=sys.stderr)
            sys.exit(1)

    elif cmd == "unlock":
        if len(sys.argv) < 3:
            print("Usage: registry.py unlock <id>")
            sys.exit(1)
        project = manager.unlock(sys.argv[2])
        if project:
            print(json.dumps(project.to_dict(), indent=2))
        else:
            print("Project not found", file=sys.stderr)
            sys.exit(1)

    elif cmd == "unlock-worker":
        if len(sys.argv) < 3:
            print("Usage: registry.py unlock-worker <worker_id>")
            sys.exit(1)
        count = manager.unlock_all_by_worker(sys.argv[2])
        print(f"Unlocked {count} projects")

    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Usage: registry.py delete <id>")
            sys.exit(1)
        if manager.delete(sys.argv[2]):
            print("Deleted")
        else:
            print("Project not found", file=sys.stderr)
            sys.exit(1)

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
