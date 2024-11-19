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


def configure_git() -> None:
    """
    Configures the global Git user name and email for the current environment.

    This function sets the global Git configuration for the user name and email
    to be used by Git commands. It is typically used in automated environments
    such as CI/CD pipelines to ensure that Git operations are performed with a
    consistent identity.

    The user name is set to "github-actions[bot]" and the email is set to
    "github-actions[bot]@users.noreply.github.com".

    Raises:
        subprocess.CalledProcessError: If any of the subprocess calls fail.
    """
    subprocess.run(
        ["git", "config", "--global", "user.name", "github-actions[bot]"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "config",
            "--global",
            "user.email",
            "github-actions[bot]@users.noreply.github.com",
        ],
        check=True,
    )


def commit_push_changes(message: str, branch_name: str) -> None:
    """
    Commit and push changes to the specified branch with a given commit message.
    If there are no changes, do nothing.
    """
    # Check if there are changes to commit
    result = subprocess.run(
        ["git", "diff-index", "--quiet", "HEAD"], capture_output=True
    )
    if result.returncode == 0:
        eprint("No changes to commit.")
        return

    # Commit and push the changes
    subprocess.run(["git", "commit", "--message", message], check=True)
    subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], check=True)
