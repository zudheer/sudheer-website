#!/usr/bin/env python3
"""
Reads scripts/resume_source.txt (first non-comment line = path to your
current resume PDF) and publishes it to assets/files/Sudheer-K-Resume.pdf —
the file the site's "Download Resume" buttons link to.

Usage:
    python scripts/update_resume.py
"""

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SITE_ROOT = SCRIPT_DIR.parent
SOURCE_FILE = SCRIPT_DIR / "resume_source.txt"
DEST_PATH = SITE_ROOT / "assets" / "files" / "Sudheer-K-Resume.pdf"


def read_source_path() -> Path:
    if not SOURCE_FILE.exists():
        sys.exit(f"Not found: {SOURCE_FILE}")

    for raw in SOURCE_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            return Path(line.strip('"'))

    sys.exit(f"No path found in {SOURCE_FILE.relative_to(SITE_ROOT)} — fill in the resume PDF path.")


def main() -> None:
    source_path = read_source_path()

    if not source_path.exists():
        sys.exit(f"Source file not found: {source_path}")
    if source_path.suffix.lower() != ".pdf":
        sys.exit(f"Expected a .pdf file, got: {source_path}")

    DEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, DEST_PATH)

    size_kb = DEST_PATH.stat().st_size // 1024
    print(f"Updated {DEST_PATH.relative_to(SITE_ROOT)} ({size_kb} KB)")
    print(f"Source:  {source_path}")


if __name__ == "__main__":
    main()
