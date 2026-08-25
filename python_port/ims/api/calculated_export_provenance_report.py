from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from ims.model.legacy_calculated_comparison import (
    RequiredCalculatedExport,
    build_calculated_legacy_comparison_plan,
)


REPORT_CONTRACT_VERSION = "pr71-v1"
DEFAULT_FIXTURE_PATH = Path("tests/fixtures/legacy_validation_bundle.json")

_EXPECTED_IDENTITIES: dict[str, tuple[str, str, str, int | str]] = {
    **{
        f"imsvnr{rule_id:02d}.dat": ("policyholder", "II", "rule", rule_id)
        for rule_id in range(1, 7)
    },
    "imsvnsk1.dat": ("policyholder", "IV", "all", "SK1"),
    **{
        f"imsvnvk{class_id}.dat": ("policyholder", "III", "rule_class", class_id)
        for class_id in range(1, 4)
    },
    "imsvu014.dat": ("insurer", "I", "entity", 14),
    "imsvusk1.dat": ("insurer", "IV", "all", "SK1"),
    **{
        f"imsvuvk{class_id}.dat": ("insurer", "III", "rule_class", class_id)
        for class_id in range(1, 4)
    },
}

_VN_RULE_SCOPES = {
    1: "Vrvn01/compulsory",
    2: "Vrvn02/random",
    3: "Vrvn03/preference",
    4: "Vrvn04/search_history",
    5: "Vrvn05/sample_search",
    6: "Vrvn06/best_info",
}

_SOURCE_EVIDENCE_PATHS = (
    Path("IMSDATA.C"),
    Path("IMS.E"),
    Path("python_port/ims/engine/explicit_period_runner.py"),
    Path("python_port/ims/engine/vu_rule_runner.py"),
    Path("python_port/ims/engine/vn_rule_runner.py"),
    Path("python_port/ims/model/agrsich_service.py"),
    Path("python_port/ims/model/agrsich_export.py"),
    Path("tests/fixtures/replay_vu14_period_plan.json"),
    Path("tests/fixtures/replay_vusk1_period_plan.json"),
    Path("tests/fixtures/calculated_vu14_validation_slice.json"),
)

_COMMON_GAPS = (
    "complete_production_population_missing",
    "automatic_historical_rule_dispatch_missing",
    "historical_rng_alignment_unproven",
    "full_window_state_evolution_unproven",
    "independent_calculated_export_missing",
)


@dataclass(frozen=True)
class CalculatedExportProvenanceIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True)
class CalculatedExportProvenanceEntry:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str
    period_start: int
    period_end: int
    required_period_count: int
    target_count: int
    legacy_references: tuple[str, ...]
    state_family: str
    rule_scope: str
    historical_filename_anchor: str
    historical_aggregation_anchor: str
    python_state_runner_anchor: str
    python_aggregation_anchor: str
    python_export_anchor: str
    writer_connected: bool = True
    explicit_runner_connected: bool = True
    explicit_output_evidence_path: str | None = None
    explicit_output_evidence_periods: tuple[int, ...] = ()
    calculated_comparison_slice_path: str | None = None
    calculated_comparison_slice_periods: tuple[int, ...] = ()
    independent_state_evolution: bool = False
    independent_full_window_ready: bool = False
    generation_gap_codes: tuple[str, ...] = _COMMON_GAPS

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "required_period_count": self.required_period_count,
            "target_count": self.target_count,
            "legacy_references": list(self.legacy_references),
            "state_family": self.state_family,
            "rule_scope": self.rule_scope,
            "historical_filename_anchor": self.historical_filename_anchor,
            "historical_aggregation_anchor": self.historical_aggregation_anchor,
            "python_state_runner_anchor": self.python_state_runner_anchor,
            "python_aggregation_anchor": self.python_aggregation_anchor,
            "python_export_anchor": self.python_export_anchor,
            "writer_connected": self.writer_connected,
            "explicit_runner_connected": self.explicit_runner_connected,
            "explicit_output_evidence_path": self.explicit_output_evidence_path,
            "explicit_output_evidence_periods": list(self.explicit_output_evidence_periods),
            "calculated_comparison_slice_path": self.calculated_comparison_slice_path,
            "calculated_comparison_slice_periods": list(
                self.calculated_comparison_slice_periods
            ),
            "independent_state_evolution": self.independent_state_evolution,
            "independent_full_window_ready": self.independent_full_window_ready,
            "generation_gap_codes": list(self.generation_gap_codes),
        }


@dataclass(frozen=True)
class CalculatedExportStateFamily:
    name: str
    subject_type: str
    export_count: int
    export_filenames: tuple[str, ...]
    next_slice: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "subject_type": self.subject_type,
            "export_count": self.export_count,
            "export_filenames": list(self.export_filenames),
            "next_slice": self.next_slice,
        }


@dataclass(frozen=True)
class CalculatedExportProvenanceReport:
    repo_root: str
    fixture_path: str
    status: str
    entries: tuple[CalculatedExportProvenanceEntry, ...]
    state_families: tuple[CalculatedExportStateFamily, ...]
    issues: tuple[CalculatedExportProvenanceIssue, ...] = field(default_factory=tuple)
    mode: str = "calculated_export_provenance_report"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "report_contract_version": REPORT_CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "fixture_path": self.fixture_path,
            "required_export_count": len(self.entries),
            "legacy_reference_count": sum(item.target_count for item in self.entries),
            "required_period_count": sum(item.required_period_count for item in self.entries),
            "insurer_export_count": sum(
                item.subject_type == "insurer" for item in self.entries
            ),
            "policyholder_export_count": sum(
                item.subject_type == "policyholder" for item in self.entries
            ),
            "writer_connected_count": sum(item.writer_connected for item in self.entries),
            "explicit_runner_connected_count": sum(
                item.explicit_runner_connected for item in self.entries
            ),
            "explicit_output_evidence_count": sum(
                bool(item.explicit_output_evidence_path) for item in self.entries
            ),
            "calculated_comparison_slice_count": sum(
                bool(item.calculated_comparison_slice_path) for item in self.entries
            ),
            "independent_full_window_ready_count": sum(
                item.independent_full_window_ready for item in self.entries
            ),
            "shared_generation_gap_codes": list(_COMMON_GAPS),
            "entries": [item.to_dict() for item in self.entries],
            "state_families": [item.to_dict() for item in self.state_families],
            "issues": [item.to_dict() for item in self.issues],
            "production_release_approved": False,
            "writes_performed": False,
            "execution_performed": False,
            "runner_started": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_full_equality_claimed": False,
        }


def build_calculated_export_provenance_report(
    repo_root: Path | str,
    *,
    fixture_path: Path | str | None = None,
) -> CalculatedExportProvenanceReport:
    root = Path(repo_root).expanduser().resolve()
    fixture = _resolve_path(root, fixture_path, DEFAULT_FIXTURE_PATH)
    plan = build_calculated_legacy_comparison_plan(fixture)
    issues = _source_evidence_issues(root)
    entries: list[CalculatedExportProvenanceEntry] = []

    for required in plan.required_exports:
        expected = _EXPECTED_IDENTITIES.get(required.filename)
        actual = (
            required.subject_type,
            required.level,
            required.selector_kind,
            required.selector_value,
        )
        if expected != actual:
            issues.append(
                CalculatedExportProvenanceIssue(
                    code="required_export_identity_unmapped",
                    message=f"unexpected calculated export identity: {required.filename} {actual}",
                    path=str(fixture),
                )
            )
            continue
        entries.append(_build_entry(root, required))

    missing_identities = sorted(set(_EXPECTED_IDENTITIES) - {item.filename for item in entries})
    if missing_identities:
        issues.append(
            CalculatedExportProvenanceIssue(
                code="required_export_identity_missing",
                message=f"required export identities are missing: {missing_identities}",
                path=str(fixture),
            )
        )
    if plan.target_count != 19 or plan.target_period_count != 6300:
        issues.append(
            CalculatedExportProvenanceIssue(
                code="core_corpus_contract_drift",
                message=(
                    "expected 19 reference targets and 6300 target periods, got "
                    f"{plan.target_count} and {plan.target_period_count}"
                ),
                path=str(fixture),
            )
        )

    ordered_entries = tuple(sorted(entries, key=lambda item: item.filename))
    return CalculatedExportProvenanceReport(
        repo_root=str(root),
        fixture_path=str(fixture),
        status="error" if issues else "mapped",
        entries=ordered_entries,
        state_families=_build_state_families(ordered_entries),
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.calculated_export_provenance_report",
        description="Kartiert die 15 berechneten Kernexporte rein lesend.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--fixture", type=Path)
    args = parser.parse_args(argv)
    result = build_calculated_export_provenance_report(
        args.repo_root,
        fixture_path=args.fixture,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _resolve_path(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    if not path.is_absolute():
        path = root / path
    return path.expanduser().resolve()


def _source_evidence_issues(root: Path) -> list[CalculatedExportProvenanceIssue]:
    return [
        CalculatedExportProvenanceIssue(
            code="source_evidence_missing",
            message=f"required PR71 source evidence is missing: {relative_path}",
            path=str((root / relative_path).resolve()),
        )
        for relative_path in _SOURCE_EVIDENCE_PATHS
        if not (root / relative_path).is_file()
    ]


def _build_entry(
    root: Path,
    required: RequiredCalculatedExport,
) -> CalculatedExportProvenanceEntry:
    state_family = f"{required.subject_type}_state"
    rule_scope, filename_anchor, aggregation_anchor, state_runner = _path_anchors(required)
    explicit_path, explicit_periods, comparison_path, comparison_periods = _slice_evidence(
        root,
        required.filename,
    )
    return CalculatedExportProvenanceEntry(
        filename=required.filename,
        subject_type=required.subject_type,
        level=required.level,
        selector_kind=required.selector_kind,
        selector_value=required.selector_value,
        period_start=required.periods[0],
        period_end=required.periods[-1],
        required_period_count=len(required.periods),
        target_count=required.target_count,
        legacy_references=tuple(path.name for path in required.legacy_paths),
        state_family=state_family,
        rule_scope=rule_scope,
        historical_filename_anchor=filename_anchor,
        historical_aggregation_anchor=aggregation_anchor,
        python_state_runner_anchor=state_runner,
        python_aggregation_anchor=(
            "ims.model.agrsich_service.collect_extended_agrsich_records"
        ),
        python_export_anchor="ims.model.agrsich_export.build_agrsich_export_tables",
        explicit_output_evidence_path=explicit_path,
        explicit_output_evidence_periods=explicit_periods,
        calculated_comparison_slice_path=comparison_path,
        calculated_comparison_slice_periods=comparison_periods,
        generation_gap_codes=_COMMON_GAPS + (f"{state_family}_path_not_closed",),
    )


def _path_anchors(
    required: RequiredCalculatedExport,
) -> tuple[str, str, str, str]:
    if required.subject_type == "insurer":
        state_runner = "ims.engine.vu_rule_runner.run_loaded_vu_foreign_info_period"
        if required.level == "I":
            return "insurer_entity_14", "IMSDATA.C:94", "IMS.E:408", state_runner
        if required.level == "III":
            return "insurer_rule_class", "IMSDATA.C:112", "IMS.E:504", state_runner
        return "insurer_all_SK1", "IMSDATA.C:116", "IMS.E:559", state_runner

    state_runner = "ims.engine.vn_rule_runner.run_loaded_vn_settlement_period"
    if required.level == "II":
        rule_id = int(required.selector_value)
        return _VN_RULE_SCOPES[rule_id], "IMSDATA.C:181", "IMS.E:657", state_runner
    if required.level == "III":
        return "policyholder_rule_class", "IMSDATA.C:187", "IMS.E:752", state_runner
    return "policyholder_all_SK1", "IMSDATA.C:191", "IMS.E:848", state_runner


def _slice_evidence(
    root: Path,
    filename: str,
) -> tuple[str | None, tuple[int, ...], str | None, tuple[int, ...]]:
    if filename == "imsvu014.dat":
        return (
            str((root / "tests/fixtures/replay_vu14_period_plan.json").resolve()),
            (1, 2, 3, 4),
            str((root / "tests/fixtures/calculated_vu14_validation_slice.json").resolve()),
            (1, 2, 3, 4),
        )
    if filename == "imsvusk1.dat":
        return (
            str((root / "tests/fixtures/replay_vusk1_period_plan.json").resolve()),
            (101, 102, 103, 104),
            None,
            (),
        )
    return None, (), None, ()


def _build_state_families(
    entries: tuple[CalculatedExportProvenanceEntry, ...],
) -> tuple[CalculatedExportStateFamily, ...]:
    insurer_files = tuple(item.filename for item in entries if item.subject_type == "insurer")
    policyholder_files = tuple(
        item.filename for item in entries if item.subject_type == "policyholder"
    )
    return (
        CalculatedExportStateFamily(
            name="insurer_state",
            subject_type="insurer",
            export_count=len(insurer_files),
            export_filenames=insurer_files,
            next_slice="imsvu014.dat periods 1-100",
        ),
        CalculatedExportStateFamily(
            name="policyholder_state",
            subject_type="policyholder",
            export_count=len(policyholder_files),
            export_filenames=policyholder_files,
            next_slice="imsvnr01.dat periods 1-300 after insurer-state closure",
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
