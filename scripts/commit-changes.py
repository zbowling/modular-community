import subprocess
import sys
from pathlib import Path
import argparse

from scripts.common import commit_push_changes, configure_git, eprint


def main() -> None:
    parser = argparse.ArgumentParser(description="Commit changes to a specified file.")
    parser.add_argument("file", type=Path, help="The file to commit.")
    args = parser.parse_args()

    if not args.file.exists():
        eprint(f"{args.file} does not exist.")
        sys.exit(1)

    # Configure git
    configure_git()

    # Commit and push changes
    subprocess.run(["git", "add", args.file], check=True)
    commit_push_changes(f"Update {args.file.name}", "main")


if __name__ == "__main__":
    main()
