from __future__ import annotations

import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "episodios"
TARGET_DIR = BASE_DIR / "videos"


def main() -> int:
    TARGET_DIR.mkdir(exist_ok=True)

    copied = 0
    linked = 0
    skipped = 0

    for source_file in sorted(SOURCE_DIR.glob("*")):
        if not source_file.is_file():
            continue

        target_file = TARGET_DIR / source_file.name
        if target_file.exists():
            skipped += 1
            continue

        try:
            target_file.hardlink_to(source_file)
            linked += 1
        except OSError:
            shutil.copy2(source_file, target_file)
            copied += 1

    print(
        f"Layout preparado en {TARGET_DIR}\n"
        f"Hardlinks: {linked}\n"
        f"Copias: {copied}\n"
        f"Ya existentes: {skipped}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
