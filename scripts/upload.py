import subprocess
import sys
from pathlib import Path
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload .conda files to a specified channel."
    )
    parser.add_argument(
        "--channel", required=True, help="The channel to upload the .conda files to."
    )
    args = parser.parse_args()

    channel = args.channel
    exit_code = 0

    for conda_file in Path("output").glob("**/*.conda"):
        command = [
            "rattler-build",
            "upload",
            "prefix",
            "--channel",
            channel,
            str(conda_file),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error uploading {conda_file}: {result.stderr}", file=sys.stderr)
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
