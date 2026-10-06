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
        ) or (relative.startswith(("docs/handbook/", "docs/migration/")) and relative.endswith(".md")) or (
            relative.startswith(("docs/handbook/images/ap3_", "docs/handbook/images/ap4_", "docs/handbook/images/ap5_", "docs/handbook/images/ap6_", "docs/handbook/images/ap7_", "docs/handbook/images/ap8_")) and relative.endswith(".png")
        ) or (relative.startswith("docs/handbook/images/ap8_core_") and relative.endswith(".svg")) or relative in ("docs/handbook/rechenkern.html", "docs/handbook/eingabeinventar.html", "docs/handbook/eingabeinventar.json", "docs/handbook/eingabeinventar_ui.json", "docs/handbook/seminar_ap3.html", "docs/handbook/management_ap4.html", "docs/handbook/market_ap5.html", "docs/handbook/market_ap6.html", "docs/handbook/market_ap7.html", "docs/handbook/market_ap8.html") or (
            relative.startswith("seminar_cases/") and relative.endswith(".json")
        )
        if approved:
            target = STAGE / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
            inventory.append({"path": relative, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    shutil.copytree(ROOT / "frontend/dist", STAGE / "frontend/dist")
    shutil.copyfile(ROOT / "docs/handbook/installer_windows.html", STAGE / "help.html")
    # PR178a PDF is a historical model guide. Current AP3 instructions and real
    # figures are in the staged seminar HTML/Markdown; obsolete installation PDF
    # is excluded because it requires a separately installed Python.
    shutil.copyfile(ROOT / "output/pdf/IMS-Bedienungsanleitung.pdf", STAGE / "Bedienungsanleitung.pdf")
    licenses = STAGE / "licenses"
    licenses.mkdir()
    dependencies = []
    npm_lock = json.loads((ROOT / 'frontend/package-lock.json').read_text())
    for relative, package in npm_lock['packages'].items():
        if not relative.startswith('node_modules/') or package.get('dev', False):
            continue
        name = relative.removeprefix('node_modules/')
        dependencies.append({'name': 'npm:' + name, 'version': package['version'],
                             'license': package.get('license')})
        for source in (ROOT / 'frontend' / relative).glob('*'):
            if source.is_file() and any(word in source.name.lower() for word in ('license', 'notice', 'copying')):
                target = licenses / 'npm' / name / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
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
        "tracked_resources": inventory, "dependencies": dependencies,
        "resource_files": [{"path": path.relative_to(STAGE).as_posix(),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                           for path in sorted(STAGE.rglob('*')) if path.is_file()],
        "raw_archives_included": False,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
