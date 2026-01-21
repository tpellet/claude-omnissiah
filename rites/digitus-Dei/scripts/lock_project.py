#!/usr/bin/env python3
"""Lock project when session starts - used by SessionStart hook."""

import os
import sys
from pathlib import Path

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from registry import RegistryManager, get_registry_dir


def main() -> None:
    """Lock project for the current session if DIGITUS_PROJECT_ID is set."""
    project_id = os.environ.get("DIGITUS_PROJECT_ID")
    session_id = os.environ.get("CLAUDE_SESSION_ID")

    if not project_id:
        return  # Not a digitus-spawned session

    if not session_id:
        print("Warning: DIGITUS_PROJECT_ID set but no CLAUDE_SESSION_ID", file=sys.stderr)
        return

    try:
        manager = RegistryManager(get_registry_dir())
        project = manager.lock(project_id, session_id)
        if project:
            print(f"Locked project {project_id} for session {session_id}")
    except FileNotFoundError:
        pass  # No config file = plugin not initialized
    except Exception as e:
        print(f"Error locking project: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
