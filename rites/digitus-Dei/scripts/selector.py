#!/usr/bin/env python3
"""Eisenhower-weighted random project selection for digitus-Dei."""

import json
import random
import sys

from registry import Project, RegistryManager, Status, get_registry_dir


def weighted_random_select(projects: list[Project]) -> Project | None:
    """Select a project using priority score as weight.

    Higher priority score = higher weight = more likely to be selected.
    Score formula: (5 - urgency) + (5 - difficulty)
    Range: 2 (hard+not urgent) to 8 (easy+urgent)

    Easy + urgent projects have the highest scores and highest selection probability.
    """
    if not projects:
        return None

    if len(projects) == 1:
        return projects[0]

    # Use score directly as weight - higher score = higher priority = more likely
    weights = [p.priority.score() for p in projects]
    return random.choices(projects, weights=weights, k=1)[0]


def select(
    status_filter: list[Status],
    unlocked_only: bool = True,
) -> Project | None:
    """Select a random project matching criteria, weighted by Eisenhower priority."""
    manager = RegistryManager(get_registry_dir())
    projects = manager.list(status_filter=status_filter, unlocked_only=unlocked_only)
    return weighted_random_select(projects)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: selector.py --status=idea,in_progress [--unlocked]")
        sys.exit(1)

    status_filter: list[Status] = []
    unlocked_only = False

    for arg in sys.argv[1:]:
        if arg.startswith("--status="):
            statuses = arg.split("=")[1].split(",")
            status_filter = [Status(s.strip()) for s in statuses]
        elif arg == "--unlocked":
            unlocked_only = True

    if not status_filter:
        print("Error: --status is required", file=sys.stderr)
        sys.exit(1)

    project = select(status_filter, unlocked_only)

    if project:
        print(json.dumps(project.to_dict(), indent=2))
    else:
        print("No matching projects found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
