"""Curated, tracked resource inventory and dependency license texts."""
from __future__ import annotations

import hashlib
from importlib import metadata
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "build" / "installer-resources"


def main() -> None:
    if STAGE.exists():
        if STAGE.resolve().parent != (ROOT / "build").resolve():
            raise ValueError("Unexpected staging path")
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    inventory = []
    for relative in tracked:
        # Checked-in curated regression references, not incomming/raw archives.
        approved = (relative.startswith("tests/fixtures/") and relative.endswith(".json")) or (
            relative.startswith("tests/references/legacy_agrsich/")
            and relative.lower().endswith((".dat", ".json"))
        ) or (relative.startswith(("docs/handbook/", "docs/migration/")) and relative.endswith(".md"))
        if approved:
            target = STAGE / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
            inventory.append({"path": relative, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    shutil.copytree(ROOT / "frontend/dist", STAGE / "frontend/dist")
    shutil.copyfile(ROOT / "docs/handbook/installer_windows.html", STAGE / "help.html")
    # The existing user guide covers the current functions; old installation PDF
    # is intentionally excluded because it requires a separately installed Python.
    shutil.copyfile(ROOT / "output/pdf/IMS-Bedienungsanleitung.pdf", STAGE / "Bedienungsanleitung.pdf")
    licenses = STAGE / "licenses"
    licenses.mkdir()
    dependencies = []
    requirements = (ROOT / "scripts/installer/requirements-build.txt").read_text().splitlines()
    for line in requirements:
        if "==" not in line:
            continue
        name, expected = line.split("==")
        dist = metadata.distribution(name)
        if dist.version != expected:
            raise ValueError(f"Dependency version mismatch: {name}: {dist.version} != {expected}")
        dependencies.append({"name": name, "version": dist.version,
                             "license": dist.metadata.get("License-Expression") or dist.metadata.get("License")})
        for entry in dist.files or []:
            if any(word in str(entry).lower() for word in ("license", "copying", "notice")):
                source = Path(dist.locate_file(entry))
                if source.is_file():
                    target = licenses / name / str(entry).split(".dist-info/")[-1]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
    # CPython and Tcl/Tk are bundled by the freezer.
    import sys
    for source in [Path(sys.base_prefix) / "LICENSE.txt", *Path(sys.base_prefix).glob("tcl/*/license.terms")]:
        target = licenses / "python-tcl" / source.parent.name / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (STAGE / "resource-inventory.json").write_text(json.dumps({
        "schema_version": 1, "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "curated_reference_files": inventory, "dependencies": dependencies,
        "raw_archives_included": False,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
