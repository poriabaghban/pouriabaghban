#!/usr/bin/env python3
"""
Create a secure zip of the project as 'gadid.zip'.

Excludes common sensitive files/directories: virtualenvs, .git, database files, media, and caches.

Run from the project root: python create_secure_zip.py
"""
import zipfile
import os
from pathlib import Path
import fnmatch

ROOT = Path(__file__).resolve().parent
ZIP_NAME = ROOT / 'gadid.zip'

# Patterns and directories to exclude from the archive
EXCLUDE_DIRS = {
    'env',
    '.git',
    'package_root',
    'media',
    '__pycache__',
    'staticfiles',
}

EXCLUDE_FILES = {
    'db.sqlite3',
}

EXCLUDE_PATTERNS = [
    '*.pyc',
    '*.sqlite3',
    '*.db',
]


def should_exclude(path: Path) -> bool:
    # Exclude by name
    parts = set(path.resolve().parts)
    if parts & EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_FILES:
        return True
    for pat in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(path.name, pat):
            return True
    return False


def main():
    if ZIP_NAME.exists():
        print(f"Removing existing archive: {ZIP_NAME}")
        ZIP_NAME.unlink()

    total = 0
    skipped = 0
    with zipfile.ZipFile(ZIP_NAME, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            # avoid descending into excluded directories
            # mutate dirnames in-place
            dirnames[:] = [d for d in dirnames if not should_exclude(Path(dirpath) / d)]

            for fname in filenames:
                fpath = Path(dirpath) / fname
                rel = fpath.relative_to(ROOT)
                if should_exclude(fpath):
                    skipped += 1
                    continue
                # skip the generated zip itself if present
                if rel.name == ZIP_NAME.name:
                    skipped += 1
                    continue
                zf.write(fpath, arcname=str(rel))
                total += 1

    print(f"Archive created: {ZIP_NAME} (files added: {total}, skipped: {skipped})")


if __name__ == '__main__':
    main()
