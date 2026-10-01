"""Validate release mirrors or advance all delivery versions together."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python_port"))
from ims.release import VERSION, windows_file_version


def check_release(root: Path, version: str) -> None:
    pyproject = tomllib.loads((root / "python_port/pyproject.toml").read_text(encoding="utf-8"))
    package = json.loads((root / "frontend/package.json").read_text(encoding="utf-8"))
    lock = json.loads((root / "frontend/package-lock.json").read_text(encoding="utf-8"))
    mirrors = (pyproject["project"]["version"], package["version"], lock["version"], lock["packages"][""]["version"])
    if any(value != version for value in mirrors):
        raise ValueError("Release versions differ; use release_metadata.py --set-version VERSION")


def advance_release(root: Path, current: str, requested: str) -> None:
    old = tuple(map(int, windows_file_version(current).split(".")))
    new = tuple(map(int, windows_file_version(requested).split(".")))
    if new <= old:
        raise ValueError("A new delivery needs a strictly greater, unused release number")
    check_release(root, current)
    source_path = root / "python_port/ims/release.py"
    source, count = re.subn(r'^VERSION = "[^"]+"$', f'VERSION = "{requested}"', source_path.read_text(encoding="utf-8"), flags=re.M)
    if count != 1:
        raise ValueError("Expected exactly one authoritative VERSION declaration")
    project_path = root / "python_port/pyproject.toml"
    project, count = re.subn(r'^version = "[^"]+"$', f'version = "{requested}"', project_path.read_text(encoding="utf-8"), flags=re.M)
    if count != 1:
        raise ValueError("Expected exactly one project version")
    package_path, lock_path = root / "frontend/package.json", root / "frontend/package-lock.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    package["version"] = lock["version"] = lock["packages"][""]["version"] = requested
    source_path.write_text(source, encoding="utf-8")
    project_path.write_text(project, encoding="utf-8")
    package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-version", help="Advance all versions; never reuse or decrease a release")
    args = parser.parse_args()
    version = VERSION
    if args.set_version:
        advance_release(ROOT, VERSION, args.set_version)
        version = args.set_version
    check_release(ROOT, version)
    print(json.dumps({"version": version, "file_version": windows_file_version(version),
                      "artifact": f"IMS-Setup-{version}-win-x64.exe"}))


if __name__ == "__main__":
    main()
