from typing import Any, TypedDict
import json
from pathlib import Path
import sys
import subprocess


class RecipeFailure(TypedDict):
    failed_at: str


def load_failed_compatibility(file_path: Path) -> dict[str, RecipeFailure]:
    if file_path.exists():
        with file_path.open("r") as file:
            return dict(json.load(file))
    return {}


def save_failed_compatibility(file_path: Path, data: dict[str, RecipeFailure]) -> None:
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w") as file:
        json.dump(data, file, indent=4)


def eprint(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


def commit_push_changes(message: str, branch_name: str) -> None:
    """
    Commit and push changes to the specified branch with a given commit message.
    If there are no changes, do nothing.
    """

    # Switch to branch
    subprocess.run(["git", "switch", branch_name])

    # Check if there are changes to commit
    result = subprocess.run(
        ["git", "diff-index", "--quiet", "HEAD"], capture_output=True
    )
    if result.returncode == 0:
        eprint("No changes to commit.")
        return

    # Commit, pull and push the changes
    subprocess.run(["git", "pull", "origin", branch_name], check=True)
    subprocess.run(["git", "commit", "--message", message, "--no-verify"], check=True)
    subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], check=True)
