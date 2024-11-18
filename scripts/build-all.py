import subprocess
from pathlib import Path
from datetime import datetime
import argparse
from scripts.common import load_failed_compatibility, save_failed_compatibility, eprint
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Build all recipes.")
    parser.add_argument(
        "--channel", nargs="+", required=True, help="The channels to use for building."
    )
    args = parser.parse_args()

    base_dir = Path("recipes")
    variant_config = "variants/variants.yaml"
    failed_compatibility_file = Path("data/failed-compatibility.json")

    # Load existing failed compatibility data
    failed_compatibility = load_failed_compatibility(failed_compatibility_file)

    exit_code = 0

    for recipe_dir in base_dir.iterdir():
        recipe_file = recipe_dir / "recipe.yaml"
        if not recipe_file.is_file():
            eprint(f"{recipe_dir} doesn't contain recipe.yaml")
            continue

        command = [
            "rattler-build",
            "build",
        ]
        for channel in args.channel:
            command.extend(["--channel", channel])
        command.extend(
            [
                "--channel",
                "conda-forge",
                "--variant-config",
                variant_config,
                "--skip-existing=all",
                "--recipe",
                str(recipe_file),
            ]
        )
        print(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            eprint(f"Error building recipe in {recipe_dir}: {result.stderr}")
            failed_compatibility[recipe_dir.name] = {
                "failed_at": datetime.now().isoformat()
            }
            exit_code = 1
        else:
            print(f"Successfully built recipe {recipe_dir.name}")
            if recipe_dir.name in failed_compatibility:
                del failed_compatibility[recipe_dir.name]
                print(f"Removed {recipe_dir.name} from failed-compatibility.json")

    # Save updated failed compatibility data
    save_failed_compatibility(failed_compatibility_file, failed_compatibility)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
