import subprocess
import sys
from pathlib import Path
import argparse

from scripts.common import eprint


def main() -> None:
    parser = argparse.ArgumentParser(description="Commit changes to a specified file.")
    parser.add_argument("file", type=Path, help="The file to commit.")
    args = parser.parse_args()

    if not args.file.exists():
        eprint(f"{args.file} does not exist.")
        sys.exit(1)

    # Configure git
    subprocess.run(
        ["git", "config", "--global", "user.name", "github-actions[bot]"], check=True
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

    # Add the file to the staging area
    subprocess.run(["git", "add", str(args.file)], check=True)

    # Check if there are changes to commit
    result = subprocess.run(
        ["git", "diff-index", "--quiet", "HEAD"], capture_output=True
    )
    if result.returncode == 0:
        print("No changes to commit.")
        sys.exit(0)

    # Commit and push the changes
    subprocess.run(["git", "commit", "-m", f"Update {args.file.name}"], check=True)
    subprocess.run(["git", "push"], check=True)


if __name__ == "__main__":
    main()
