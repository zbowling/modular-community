import os
import subprocess
import sys
from pathlib import Path
from github import Github
from .common import load_failed_compatibility
from datetime import datetime, timedelta
import yaml


def main() -> None:
    github_token = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY")
    if not github_token or not github_repository:
        print(
            "GITHUB_TOKEN and GITHUB_REPOSITORY environment variables are required.",
            file=sys.stderr,
        )
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

    for recipe in recipes_to_remove:
        branch_name = f"delete-{recipe.name.replace('_', '-')}"
        subprocess.run(["git", "switch", "--create", branch_name], check=True)
        subprocess.run(["git", "rm", "-r", recipe], check=True)
        subprocess.run(["git", "commit", "--message", f"Delete {recipe}"], check=True)
        subprocess.run(["git", "push"], check=True)

        # Read the recipe.yaml file
        recipe_yaml_path = recipe / "recipe.yaml"
        if recipe_yaml_path.is_file():
            with recipe_yaml_path.open("r") as file:
                recipe_data = yaml.safe_load(file)
                maintainers = recipe_data.get("extra", {}).get("maintainers", [])
        else:
            maintainers = []

        # Prepare the PR body
        body = f"This PR deletes '{recipe}' since it failed compatibility testing four weeks ago. "
        if maintainers:
            body += (
                f"Tagging maintainers: {' '.join([f'@{user}' for user in maintainers])}"
            )
        else:
            body += "Maintainers couldn't be extracted from recipe.yaml."

        title = f"Delete {recipe}"
        pr = repo.create_pull(title=title, body=body, head=branch_name, base="main")
        print(f"Created PR: {pr.html_url}")


if __name__ == "__main__":
    main()
