from __future__ import annotations

import argparse
import ast
import csv
import io
from collections import Counter
from pathlib import Path


SCHEMA_VERSION = "ims.module-inventory.v1"
BASELINE_TAG = "ims-legacy-baseline-2026-09-01"
BASELINE_COMMIT = "2e92637c22c97e920ffa7ffaca02ecdf48be3311"


def _module_name(path: Path, python_root: Path) -> str:
    relative = path.relative_to(python_root).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _owner(module: str, path: str) -> str:
    stem = Path(path).stem
    if not module.startswith("ims"):
        return "dormant_scaffold"
    if stem.startswith(("legacy_", "historical_", "vdefmd6_", "vu14_")):
        return "legacy_validation"
    if stem.startswith(("replay_", "explicit_legacy_", "core_validation_")):
        return "legacy_validation"
    if module.startswith("ims.api"):
        return "workbench"
    if module.startswith("ims.engine"):
        return "simulation_core"
    if module.startswith("ims.model"):
        return "market_domain"
    if module.startswith("ims.io"):
        return "scenario_io"
    if module.startswith("ims.analysis"):
        return "analysis"
    return "package_root"


def _role(path: str) -> str:
    stem = Path(path).stem
    for marker in ("contract", "report", "delivery", "smoke", "runner", "plan", "writer"):
        if marker in stem:
            return marker
    if stem in {"__init__", "app"}:
        return "package_marker" if stem == "__init__" else "web_app"
    if "rule" in stem:
        return "rule"
    if "metadata" in stem or "queue" in stem:
        return "workbench_state"
    return "runtime"


def _target_package(owner: str) -> str | None:
    return {
        "legacy_validation": "ims.legacy",
        "workbench": "ims.workbench",
        "simulation_core": "ims.simulation",
        "market_domain": "ims.domain",
        "scenario_io": "ims.io",
        "analysis": "ims.reporting",
        "package_root": "ims",
    }.get(owner)


def _decision(owner: str, role: str, lines: int, path: str) -> str:
    if owner == "dormant_scaffold":
        return "retire_after_import_check"
    if owner == "legacy_validation":
        return "freeze_then_move"
    if lines >= 1000 or path.endswith("/api/app.py"):
        return "review_split"
    if owner == "workbench" and role in {"contract", "report", "delivery", "smoke", "plan"}:
        return "review_configured_merge"
    return "keep"


def build_inventory(repo_root: Path) -> dict[str, object]:
    python_root = repo_root / "python_port"
    source_paths = sorted(python_root.rglob("*.py"))
    module_paths = {_module_name(path, python_root): path for path in source_paths}
    importer_paths = source_paths + sorted((repo_root / "tests").rglob("*.py"))
    imported_by: dict[str, list[str]] = {module: [] for module in module_paths}

    for importer in importer_paths:
        relative_importer = importer.relative_to(repo_root).as_posix()
        for imported in _imports(importer):
            if imported in imported_by:
                imported_by[imported].append(relative_importer)

    entries: list[dict[str, object]] = []
    for module, path in sorted(module_paths.items(), key=lambda item: item[1].as_posix()):
        relative = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8")
        lines = len(text.splitlines())
        owner = _owner(module, relative)
        role = _role(relative)
        dependencies = sorted(name for name in _imports(path) if name in module_paths)
        importers = sorted(set(imported_by[module]))
        runtime_importers = [item for item in importers if item.startswith("python_port/")]
        test_importers = [item for item in importers if item.startswith("tests/")]
        decision = _decision(owner, role, lines, relative)
        risk = "high" if lines >= 800 or len(importers) >= 12 else "medium" if importers else "low"
        entries.append(
            {
                "path": relative,
                "module": module,
                "installed_package": module == "ims" or module.startswith("ims."),
                "owner": owner,
                "role": role,
                "lines": lines,
                "direct_internal_dependencies": dependencies,
                "runtime_importers": runtime_importers,
                "test_importers": test_importers,
                "decision": decision,
                "target_package": _target_package(owner),
                "change_risk": risk,
            }
        )

    area_counts: Counter[str] = Counter()
    area_lines: Counter[str] = Counter()
    decision_counts: Counter[str] = Counter()
    for entry in entries:
        path_parts = str(entry["path"]).split("/")
        area = "/".join(path_parts[:3]) if path_parts[1] == "ims" else "/".join(path_parts[:2])
        area_counts[area] += 1
        area_lines[area] += int(entry["lines"])
        decision_counts[str(entry["decision"])] += 1

    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_date": "2026-09-02",
        "baseline_tag": BASELINE_TAG,
        "baseline_commit": BASELINE_COMMIT,
        "scope": "python_port/**/*.py",
        "classification_is_planning_only": True,
        "summary": {
            "file_count": len(entries),
            "installed_package_file_count": sum(bool(entry["installed_package"]) for entry in entries),
            "line_count": sum(int(entry["lines"]) for entry in entries),
            "files_by_area": dict(sorted(area_counts.items())),
            "lines_by_area": dict(sorted(area_lines.items())),
            "files_by_decision": dict(sorted(decision_counts.items())),
        },
        "entries": entries,
    }


def render_inventory_csv(payload: dict[str, object]) -> str:
    fields = (
        "path",
        "module",
        "installed_package",
        "owner",
        "role",
        "lines",
        "direct_internal_dependencies",
        "runtime_importers",
        "test_importers",
        "decision",
        "target_package",
        "change_risk",
    )
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for source_entry in payload["entries"]:
        entry = dict(source_entry)
        for field in (
            "direct_internal_dependencies",
            "runtime_importers",
            "test_importers",
        ):
            entry[field] = "|".join(entry[field])
        entry["installed_package"] = str(entry["installed_package"]).lower()
        entry["target_package"] = entry["target_package"] or ""
        writer.writerow(entry)
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the PR103 IMS Python module inventory.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()

    payload = build_inventory(args.root.resolve())
    rendered = render_inventory_csv(payload)
    if args.check:
        expected = args.check.read_text(encoding="utf-8")
        if rendered != expected:
            print(f"module inventory differs: {args.check}")
            return 1
        print(f"module inventory is current: {args.check}")
        return 0
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
        print(args.out)
        return 0
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
