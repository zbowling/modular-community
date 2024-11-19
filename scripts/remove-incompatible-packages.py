import os
import subprocess
import sys
from pathlib import Path
from github import Github
from scripts.common import (
    commit_push_changes,
    eprint,
    load_failed_compatibility,
    configure_git,
)
from datetime import datetime, timedelta
import yaml
import uuid


def main() -> None:
    github_token = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY")
    if not github_token or not github_repository:
        eprint("GITHUB_TOKEN and GITHUB_REPOSITORY environment variables are required.")
        sys.exit(1)

    gh = Github(github_token)
    repo = gh.get_repo(github_repository)

    # Load the failed compatibility data
    failed_compatibility_file = Path("data/failed-compatibility.json")
    failed_compatibility = load_failed_compatibility(failed_compatibility_file)

    # Filter recipes where the failure state is older than four weeks
    four_weeks_ago = datetime.now() - timedelta(weeks=4)
    recipes_to_remove = [
        Path("recipes", recipe)
        for recipe, failure in failed_compatibility.items()
        if datetime.fromisoformat(failure["failed_at"]) < four_weeks_ago
    ]

    configure_git()

    exit_code = 0
    for recipe in recipes_to_remove:
        try:
            # Read the recipe.yaml file
            recipe_yaml_path = recipe / "recipe.yaml"
            if recipe_yaml_path.is_file():
                with recipe_yaml_path.open("r") as file:
                    recipe_data = yaml.safe_load(file)
                    maintainers = recipe_data.get("extra", {}).get("maintainers", [])
            else:
                eprint(f"{recipe_yaml_path} does not exist")
                maintainers = []

            # Prepare the PR body
            body = f"This PR deletes '{recipe.name}' since it failed compatibility testing four weeks ago.\n"
            if maintainers:
                body += f"Tagging maintainers: {' '.join([f'@{user}' for user in maintainers])}"
            else:
                body += "Maintainers couldn't be extracted from recipe.yaml."

            # Create a commit and push it
            hash = uuid.uuid4().hex[:7]
            branch_name = f"delete-recipe-{hash}"
            subprocess.run(["git", "switch", "--create", branch_name], check=True)
            subprocess.run(["git", "rm", "-r", recipe], check=True)
            subprocess.run(
                ["git", "commit", "--message", f"Delete recipe '{recipe.name}'"],
                check=True,
            )
            subprocess.run(
                ["git", "push", "--set-upstream", "origin", branch_name], check=True
            )

            # Create the pull request
            title = f"Delete recipe {recipe.name}"
            pr = repo.create_pull(title=title, body=body, head=branch_name, base="main")
            print(f"Created PR: {pr.html_url}")

            # Remove the failed_at entry for this recipe
            del failed_compatibility[recipe.name]

        except Exception as e:
            # If there's an error, print it and move on to the next recipe
            eprint(f"Error processing {recipe}: {e}")
            exit_code = 1
            continue

    # Save the updated failed compatibility data
    with failed_compatibility_file.open("w") as file:
        yaml.safe_dump(failed_compatibility, file)

    # Commit and push changes to the failed compatibility file
    subprocess.run(["git", "add", failed_compatibility_file], check=True)
    commit_push_changes(f"Update {failed_compatibility_file.name}", "main")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
