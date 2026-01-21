#!/usr/bin/env python3
"""Unlock projects when session ends - used by SessionEnd hook."""

import os
import sys
from pathlib import Path

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from registry import RegistryManager, get_registry_dir


def main() -> None:
    """Unlock all projects locked by the current session."""
    session_id = os.environ.get("CLAUDE_SESSION_ID")
    if not session_id:
        print("No CLAUDE_SESSION_ID found, nothing to unlock")
        return

    try:
        manager = RegistryManager(get_registry_dir())
        count = manager.unlock_all_by_worker(session_id)
        if count > 0:
            print(f"Unlocked {count} project(s) for session {session_id}")
    except FileNotFoundError:
        pass  # No config file = plugin not initialized, nothing to unlock
    except Exception as e:
        print(f"Error unlocking projects: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
