from typing import Any, TypedDict
import json
from pathlib import Path
import sys


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
