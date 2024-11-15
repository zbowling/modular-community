import os
import zipfile
from pathlib import Path
from github import Github
import sys
from github import Auth

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
WORKFLOW_FILENAME = os.getenv("WORKFLOW_FILENAME")
ARTIFACT_NAME = os.getenv("ARTIFACT_NAME")
ARTIFACT_FILENAME = os.getenv("ARTIFACT_FILENAME")


def main():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo("modular/modular-community")

    # List workflows
    workflows = repo.get_workflows()
    workflow = next((w for w in workflows if WORKFLOW_FILENAME in w.path), None)

    if not workflow:
        print("No workflow found")
        return

    # List workflow runs
    runs = workflow.get_runs(status="success")
    runs = list(runs)
    if not runs:
        print("No runs found")
        return

    # List artifacts
    run_id = runs[0].id
    artifacts = repo.get_workflow_run(run_id).get_artifacts()
    artifact = next((a for a in artifacts if a.name == ARTIFACT_NAME), None)

    if artifact:
        # Download artifact
        artifact_data = artifact.download()
        with open(ARTIFACT_FILENAME, "wb") as f:
            f.write(artifact_data.content)

        # Unzip artifact
        with zipfile.ZipFile(ARTIFACT_FILENAME, "r") as zip_ref:
            zip_ref.extractall(Path(ARTIFACT_FILENAME).parent)

        print("Artifact downloaded successfully")
    else:
        print("No artifact found")
        sys.exit(1)


if __name__ == "__main__":
    main()
