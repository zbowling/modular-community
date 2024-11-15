import subprocess
from pathlib import Path
import sys
import json
from datetime import datetime
from typing import Any
import argparse


def load_failed_compatibility(file_path: Path) -> dict[str, Any]:
    if file_path.exists():
        with file_path.open("r") as file:
            return dict(json.load(file))
    return {}


def save_failed_compatibility(file_path: Path, data: dict[str, Any]) -> None:
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w") as file:
        json.dump(data, file, indent=4)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build all recipes.")
    parser.add_argument(
        "--channel", required=True, help="The primary channel to use for building."
    )
    args = parser.parse_args()

    base_dir = Path("recipes")
    variant_config = "variants/variants.yaml"
    failed_compatibility_file = Path("data/failed-compatibility.json")
    primary_channel = args.channel

    # Load existing failed compatibility data
    failed_compatibility = load_failed_compatibility(failed_compatibility_file)

    for recipe_dir in base_dir.iterdir():
        recipe_file = recipe_dir / "recipe.yaml"
        if not recipe_file.is_file():
            print(f"{recipe_dir} doesn't contain recipe.yaml", file=sys.stderr)
            continue

        command = [
            "rattler-build",
            "build",
            "--channel",
            primary_channel,
            "--channel",
            "https://conda.modular.com/max",
            "--channel",
            "conda-forge",
            "--variant-config",
            variant_config,
            "--skip-existing=all",
            "--recipe",
            str(recipe_file),
        ]
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(
                f"Error building recipe in {recipe_dir}: {result.stderr}",
                file=sys.stderr,
            )
            failed_compatibility[recipe_dir.name] = {
                "failed_at": datetime.now().isoformat()
            }
        else:
            print(f"Successfully built recipe in {recipe_dir}")

    # Save updated failed compatibility data
    save_failed_compatibility(failed_compatibility_file, failed_compatibility)


if __name__ == "__main__":
    main()
