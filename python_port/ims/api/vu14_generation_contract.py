from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.api.calculated_export_provenance_report import (
    build_calculated_export_provenance_report,
)


CONTRACT_VERSION = "pr72-v1"
DEFAULT_CONTRACT_PATH = Path("tests/fixtures/vu14_100_period_generation_contract.json")
DEFAULT_BUNDLE_PATH = Path("tests/fixtures/legacy_validation_bundle.json")
DEFAULT_SLICE_PATH = Path("tests/fixtures/replay_vu14_period_plan.json")

_TARGET = {
    "subject_type": "insurer",
    "level": "I",
    "selector_kind": "entity",
    "selector_value": 14,
    "export_filename": "imsvu014.dat",
    "legacy_reference": "VU14L1.DAT",
    "period_start": 1,
    "period_end": 100,
    "period_count": 100,
}
_OUTPUT_FIELDS = (
    "premiums_current_sector",
    "advertising_current_sector",
    "reserves_current",
    "policyholders_current_sector",
    "claims_count_current",
    "claims_sum_current",
)
_REQUIREMENT_CODES = (
    "complete_population_origin",
    "initial_state_origin",
    "vu14_rule_schedule_origin",
    "rng_stream_origin",
    "state_transition_origin",
    "policyholder_claim_origin",
)
_DIRECT_OUTPUT_FIELDS = (
    "premiums_current",
    "advertising_current",
    "reserves_current",
    "policyholders_current",
    "claims_count_current",
    "claims_sum_current",
)
_FORBIDDEN_INPUT_KINDS = (
    "legacy_export_rows",
    "calculated_export_echo",
    "period_by_period_output_state_updates",
)
_ACCEPTANCE = {
    "independent_state_evolution_required": True,
    "complete_period_window_required": True,
    "historical_rng_equality_required": False,
    "historical_full_equality_claim_allowed": False,
}
_SOURCE_PATHS = (
    Path("IMSDATA.C"),
    Path("IMS.E"),
    Path("python_port/ims/engine/replay_plan.py"),
    Path("python_port/ims/engine/vu_rule_runner.py"),
    Path("python_port/ims/model/agrsich_service.py"),
    Path("python_port/ims/model/agrsich_export.py"),
    DEFAULT_SLICE_PATH,
    Path("tests/references/legacy_agrsich/VU14L1.DAT"),
)
_BLOCKERS = (
    "complete_population_origin_missing",
    "vu14_rule_schedule_origin_missing",
    "rng_stream_origin_missing",
    "independent_state_evolution_missing",
    "independent_100_period_export_missing",
)


@dataclass(frozen=True)
class VU14GenerationContractIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True)
class VU14GenerationContractReport:
    repo_root: str
    contract_path: str
    bundle_path: str
    input_requirements: tuple[dict[str, object], ...]
    existing_slice: dict[str, object]
    source_evidence_paths: tuple[str, ...]
    status: str
    issues: tuple[VU14GenerationContractIssue, ...]
    mode: str = "vu14_100_period_generation_contract"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "bundle_path": self.bundle_path,
            "target": dict(_TARGET),
            "required_period_count": 100,
            "required_output_fields": list(_OUTPUT_FIELDS),
            "input_requirement_count": len(self.input_requirements),
            "currently_evidenced_input_requirement_count": 0,
            "input_requirements": [dict(item) for item in self.input_requirements],
            "forbidden_input_kinds": list(_FORBIDDEN_INPUT_KINDS),
            "existing_slice": dict(self.existing_slice),
            "source_evidence_paths": list(self.source_evidence_paths),
            "source_evidence_count": len(self.source_evidence_paths),
            "generation_blocker_codes": list(_BLOCKERS),
            "contract_ready": not self.issues,
            "generation_ready": False,
            "independent_full_window_ready": False,
            "production_release_approved": False,
            "writes_performed": False,
            "execution_performed": False,
            "runner_started": False,
            "simulation_performed": False,
            "automatic_historical_rule_selection_performed": False,
            "historical_full_equality_claimed": False,
            "issues": [item.to_dict() for item in self.issues],
        }


def build_vu14_generation_contract_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
    bundle_path: Path | str | None = None,
    slice_path: Path | str | None = None,
) -> VU14GenerationContractReport:
    root = Path(repo_root).expanduser().resolve()
    contract_file = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    bundle_file = _resolve(root, bundle_path, DEFAULT_BUNDLE_PATH)
    slice_file = _resolve(root, slice_path, DEFAULT_SLICE_PATH)
    issues: list[VU14GenerationContractIssue] = []

    contract = _load_json_object(contract_file, "contract", issues)
    requirements = _validate_contract(contract, contract_file, issues)
    _validate_bundle_target(root, bundle_file, issues)
    source_paths = _source_evidence(root, issues)
    existing_slice = _slice_evidence(slice_file, issues)

    return VU14GenerationContractReport(
        repo_root=str(root),
        contract_path=str(contract_file),
        bundle_path=str(bundle_file),
        input_requirements=requirements,
        existing_slice=existing_slice,
        source_evidence_paths=source_paths,
        status="error" if issues else "prepared",
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vu14_generation_contract",
        description="Prueft den read-only VU14-Erzeugungsvertrag fuer Perioden 1-100.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--slice", type=Path)
    args = parser.parse_args(argv)
    report = build_vu14_generation_contract_report(
        args.repo_root,
        contract_path=args.contract,
        bundle_path=args.bundle,
        slice_path=args.slice,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if report.status == "error" else 0


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[VU14GenerationContractIssue],
    code: str,
    message: str,
    path: Path,
) -> None:
    issues.append(VU14GenerationContractIssue(code=code, message=message, path=str(path)))


def _load_json_object(
    path: Path,
    label: str,
    issues: list[VU14GenerationContractIssue],
) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _issue(issues, f"{label}_unreadable", f"{label} JSON cannot be read: {exc}", path)
        return {}
    if not isinstance(value, dict):
        _issue(issues, f"{label}_shape_invalid", f"{label} JSON must be an object", path)
        return {}
    return value


def _validate_contract(
    contract: dict[str, object],
    path: Path,
    issues: list[VU14GenerationContractIssue],
) -> tuple[dict[str, object], ...]:
    if contract.get("schema_version") != CONTRACT_VERSION:
        _issue(issues, "contract_version_mismatch", f"expected {CONTRACT_VERSION}", path)
    if contract.get("target") != _TARGET:
        _issue(
            issues,
            "target_period_contract_mismatch",
            "target must be insurer/I/entity=14 for periods 1-100",
            path,
        )
    if tuple(contract.get("required_output_fields", ())) != _OUTPUT_FIELDS:
        _issue(issues, "required_output_fields_mismatch", "six output fields required", path)

    raw_requirements = contract.get("input_requirements")
    items = raw_requirements if isinstance(raw_requirements, list) else []
    requirements: list[dict[str, object]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        fields = item.get("fields")
        requirements.append(
            {
                "code": str(item.get("code", "")),
                "fields": [str(field) for field in fields] if isinstance(fields, list) else [],
                "origin_required": item.get("origin_required") is True,
                "currently_evidenced": False,
            }
        )
    if tuple(item["code"] for item in requirements) != _REQUIREMENT_CODES:
        _issue(issues, "input_requirement_set_mismatch", "six input groups required", path)
    if any(not item["origin_required"] or not item["fields"] for item in requirements):
        _issue(
            issues,
            "input_origin_requirement_missing",
            "every input group requires a non-empty origin declaration",
            path,
        )

    reference = contract.get("reference_boundary")
    reference = reference if isinstance(reference, dict) else {}
    if reference.get("comparison_only_after_generation") is not True:
        _issue(issues, "reference_comparison_boundary_missing", "compare only after generation", path)
    if tuple(reference.get("forbidden_input_kinds", ())) != _FORBIDDEN_INPUT_KINDS:
        _issue(issues, "forbidden_input_boundary_mismatch", "output echoes must be forbidden", path)
    if contract.get("acceptance") != _ACCEPTANCE:
        _issue(issues, "acceptance_boundary_mismatch", "conservative acceptance flags required", path)
    return tuple(requirements)


def _validate_bundle_target(
    root: Path,
    bundle_path: Path,
    issues: list[VU14GenerationContractIssue],
) -> None:
    try:
        provenance = build_calculated_export_provenance_report(root, fixture_path=bundle_path)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        _issue(issues, "core_bundle_unreadable", f"cannot establish VU14 target: {exc}", bundle_path)
        return
    entry = next((item for item in provenance.entries if item.filename == "imsvu014.dat"), None)
    actual = (
        entry.subject_type,
        entry.level,
        entry.selector_kind,
        entry.selector_value,
        entry.period_start,
        entry.period_end,
        entry.required_period_count,
    ) if entry is not None else None
    if provenance.status == "error" or actual != ("insurer", "I", "entity", 14, 1, 100, 100):
        _issue(issues, "core_bundle_target_mismatch", f"unexpected VU14 target: {actual}", bundle_path)


def _source_evidence(
    root: Path,
    issues: list[VU14GenerationContractIssue],
) -> tuple[str, ...]:
    found: list[str] = []
    for relative in _SOURCE_PATHS:
        path = (root / relative).resolve()
        if path.is_file():
            found.append(str(path))
        else:
            _issue(issues, "source_evidence_missing", f"missing source evidence: {relative}", path)
    return tuple(found)


def _slice_evidence(
    path: Path,
    issues: list[VU14GenerationContractIssue],
) -> dict[str, object]:
    payload = _load_json_object(path, "slice", issues)
    updates = payload.get("period_updates")
    updates = updates if isinstance(updates, list) else []
    periods: list[int] = []
    direct_fields: set[str] = set()
    for update in updates:
        if not isinstance(update, dict):
            continue
        context = update.get("context")
        if isinstance(context, dict) and isinstance(context.get("period"), int):
            periods.append(context["period"])
        insurers = update.get("insurers")
        if not isinstance(insurers, list):
            continue
        for insurer in insurers:
            if isinstance(insurer, dict) and insurer.get("entity_id") == 14:
                direct_fields.update(set(insurer) & set(_DIRECT_OUTPUT_FIELDS))
    ordered_fields = tuple(field for field in _DIRECT_OUTPUT_FIELDS if field in direct_fields)
    if periods != [1, 2, 3, 4]:
        _issue(issues, "existing_slice_period_drift", "slice must remain periods 1-4", path)
    if ordered_fields != _DIRECT_OUTPUT_FIELDS:
        _issue(issues, "existing_slice_shape_drift", "slice output update shape changed", path)
    return {
        "fixture_path": str(path),
        "periods": periods,
        "period_count": len(periods),
        "direct_output_update_fields": list(ordered_fields),
        "output_projection_connected": bool(periods and ordered_fields),
        "independent_state_evolution": False,
        "acceptable_as_generation_input": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
