import json
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Modify JSON file to add a new broken repo."
    )
    parser.add_argument("file_path", type=Path, help="Path to the JSON file")
    args = parser.parse_args()

    try:
        with args.file_path.open("r") as file:
            data = json.load(file)
    except Exception as e:
        print(f"Couldn't parse {args.file_path} as json: {e}")
        data = {"broken_repos": []}

    data["broken_repos"].append("new_repo")

    with args.file_path.open("w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    main()
