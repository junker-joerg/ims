from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Sequence

from ims.engine.context import SimulationContext
from ims.model.agrsich_export import build_agrsich_export_tables
from ims.model.agrsich_service import collect_extended_agrsich_records
from ims.model.entities import BAV
from ims.model.legacy_agrsich_reference import (
    compare_export_record_to_legacy_row,
    extract_legacy_row,
    parse_legacy_insurer_dat,
)
from ims.model.vu_rules import (
    apply_vu_expected_claim_rule_to_insurer,
    vu_expected_claim_rule_parameters_from_mapping,
)
from ims.model.vdefmd6_population import build_vdefmd6_population


SOURCE_BINDING_VERSION = "pr73-v1"
DEFAULT_SOURCE_BINDING_PATH = Path("tests/fixtures/vu14_vdefmd6_source_binding.json")
_EVIDENCED_REQUIREMENTS = (
    "complete_population_origin",
    "initial_state_origin",
    "vu14_rule_schedule_origin",
    "state_transition_origin",
)
_OPEN_REQUIREMENTS = ("rng_stream_origin", "policyholder_claim_origin")


@dataclass(frozen=True)
class VU14SourceBindingIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True)
class VU14SourceBindingReport:
    repo_root: str
    binding_path: str
    model_id: str | None
    target: dict[str, object]
    evidenced_requirement_codes: tuple[str, ...]
    open_requirement_codes: tuple[str, ...]
    source_anchor_count: int
    reference_normalized_sha256: str | None
    period_one_comparison: dict[str, object]
    issues: tuple[VU14SourceBindingIssue, ...]
    status: str
    mode: str = "vu14_vdefmd6_source_binding"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "source_binding_version": SOURCE_BINDING_VERSION,
            "repo_root": self.repo_root,
            "binding_path": self.binding_path,
            "model_id": self.model_id,
            "target": dict(self.target),
            "evidenced_requirement_codes": list(self.evidenced_requirement_codes),
            "evidenced_requirement_count": len(self.evidenced_requirement_codes),
            "open_requirement_codes": list(self.open_requirement_codes),
            "source_anchor_count": self.source_anchor_count,
            "reference_normalized_sha256": self.reference_normalized_sha256,
            "period_one_comparison": dict(self.period_one_comparison),
            "source_binding_ready": not self.issues,
            "independent_period_one_ready": self.period_one_comparison.get("matches") is True,
            "independent_full_window_ready": False,
            "generation_ready": False,
            "production_release_approved": False,
            "writes_performed": False,
            "runner_started": False,
            "simulation_performed": False,
            "historical_full_equality_claimed": False,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vu14_source_binding_report(
    repo_root: Path | str,
    *,
    binding_path: Path | str | None = None,
) -> VU14SourceBindingReport:
    root = Path(repo_root).expanduser().resolve()
    path = _resolve(root, binding_path, DEFAULT_SOURCE_BINDING_PATH)
    issues: list[VU14SourceBindingIssue] = []
    profile = _load_profile(path, issues)

    model = profile.get("model") if isinstance(profile.get("model"), dict) else {}
    vu14 = profile.get("vu14") if isinstance(profile.get("vu14"), dict) else {}
    target = {
        "subject_type": "insurer",
        "level": "I",
        "selector_kind": "entity",
        "selector_value": vu14.get("entity_id"),
        "rule_id": vu14.get("rule_id"),
        "rule_class": vu14.get("rule_class"),
        "export_filename": "imsvu014.dat",
        "period_start": 1,
        "period_end": 100,
    }
    evidenced = _string_tuple(profile.get("evidenced_requirement_codes"))
    open_requirements = _string_tuple(profile.get("open_requirement_codes"))
    _validate_profile(profile, path, evidenced, open_requirements, issues)
    anchor_count = _validate_source_anchors(root, profile.get("source_anchors"), issues)
    reference_normalized_sha256 = _validate_reference(root, profile.get("reference"), issues)
    period_one = _build_period_one_comparison(root, profile, issues)

    return VU14SourceBindingReport(
        repo_root=str(root),
        binding_path=str(path),
        model_id=str(model.get("model_id")) if model.get("model_id") is not None else None,
        target=target,
        evidenced_requirement_codes=evidenced,
        open_requirement_codes=open_requirements,
        source_anchor_count=anchor_count,
        reference_normalized_sha256=reference_normalized_sha256,
        period_one_comparison=period_one,
        issues=tuple(issues),
        status="error" if issues else "source_bound",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vu14_source_binding",
        description="Prueft die read-only Vdefmd6-Quellenbindung fuer VU14.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--binding", type=Path)
    args = parser.parse_args(argv)
    report = build_vu14_source_binding_report(args.repo_root, binding_path=args.binding)
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if report.status == "error" else 0


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[VU14SourceBindingIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        VU14SourceBindingIssue(code=code, message=message, path=str(path) if path else None)
    )


def _load_profile(path: Path, issues: list[VU14SourceBindingIssue]) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _issue(issues, "source_binding_unreadable", str(exc), path)
        return {}
    if not isinstance(value, dict):
        _issue(issues, "source_binding_shape_invalid", "binding must be a JSON object", path)
        return {}
    return value


def _string_tuple(value: object) -> tuple[str, ...]:
    return tuple(str(item) for item in value) if isinstance(value, list) else ()


def _validate_profile(
    profile: dict[str, object],
    path: Path,
    evidenced: tuple[str, ...],
    open_requirements: tuple[str, ...],
    issues: list[VU14SourceBindingIssue],
) -> None:
    if profile.get("schema_version") != SOURCE_BINDING_VERSION:
        _issue(issues, "source_binding_version_mismatch", SOURCE_BINDING_VERSION, path)
    model = profile.get("model") if isinstance(profile.get("model"), dict) else {}
    model_signature = (
        model.get("model_id"),
        model.get("simulation_periods"),
        model.get("insurer_count"),
        model.get("policyholder_count"),
    )
    if model_signature != ("Vdefmd6", 100, 25, 200):
        _issue(issues, "model_identity_mismatch", "expected Vdefmd6 / 100 / 25 / 200", path)
    vu14 = profile.get("vu14") if isinstance(profile.get("vu14"), dict) else {}
    if (
        vu14.get("entity_id"),
        vu14.get("rule_id"),
        vu14.get("rule_class"),
        vu14.get("activation_period"),
        vu14.get("logical_action_time"),
    ) != (14, 6, 2, 1, 1):
        _issue(issues, "vu14_identity_mismatch", "expected VU14 / Vrvu06 / class 2", path)
    if evidenced != _EVIDENCED_REQUIREMENTS or open_requirements != _OPEN_REQUIREMENTS:
        _issue(issues, "requirement_boundary_mismatch", "unexpected evidence boundary", path)


def _validate_source_anchors(
    root: Path,
    value: object,
    issues: list[VU14SourceBindingIssue],
) -> int:
    anchors = value if isinstance(value, list) else []
    valid_count = 0
    cache: dict[Path, str] = {}
    for anchor in anchors:
        if not isinstance(anchor, dict):
            continue
        relative = anchor.get("path")
        needle = anchor.get("needle")
        if not isinstance(relative, str) or not isinstance(needle, str):
            continue
        source_path = (root / relative).resolve()
        try:
            text = cache.setdefault(source_path, source_path.read_text(encoding="latin-1"))
        except OSError as exc:
            _issue(issues, "source_anchor_unreadable", str(exc), source_path)
            continue
        if needle not in text:
            _issue(issues, "source_anchor_missing", needle, source_path)
            continue
        valid_count += 1
    if valid_count != 9:
        _issue(issues, "source_anchor_count_mismatch", f"expected 9, found {valid_count}")
    return valid_count


def _validate_reference(
    root: Path,
    value: object,
    issues: list[VU14SourceBindingIssue],
) -> str | None:
    reference = value if isinstance(value, dict) else {}
    relative = reference.get("path")
    if not isinstance(relative, str):
        _issue(issues, "reference_path_missing", "reference path is required")
        return None
    path = (root / relative).resolve()
    try:
        normalized = "\n".join(
            " ".join(line.split()) for line in path.read_text(encoding="ascii").splitlines()
        ) + "\n"
        digest = hashlib.sha256(normalized.encode("ascii")).hexdigest()
        table = parse_legacy_insurer_dat(path)
    except (OSError, ValueError) as exc:
        _issue(issues, "reference_unreadable", str(exc), path)
        return None
    if digest != reference.get("normalized_sha256"):
        _issue(issues, "reference_hash_mismatch", digest, path)
    periods = [row.global_period for row in table.rows]
    if periods != list(range(1, 101)):
        _issue(issues, "reference_period_window_mismatch", "expected periods 1-100", path)
    return digest


def _build_period_one_comparison(
    root: Path,
    profile: dict[str, object],
    issues: list[VU14SourceBindingIssue],
) -> dict[str, object]:
    vu14 = profile.get("vu14") if isinstance(profile.get("vu14"), dict) else {}
    state = vu14.get("initial_state") if isinstance(vu14.get("initial_state"), dict) else {}
    parameters = vu14.get("parameters") if isinstance(vu14.get("parameters"), dict) else {}
    bav_data = profile.get("bav") if isinstance(profile.get("bav"), dict) else {}
    reference = profile.get("reference") if isinstance(profile.get("reference"), dict) else {}
    try:
        population = build_vdefmd6_population()
        insurer = next(item for item in population.insurers if item.entity_id == 14)
        actual_state = (
            insurer.premiums_current_sector,
            insurer.advertising_current_sector,
            insurer.reserves_current,
            insurer.policyholders_current_sector,
            insurer.claims_count_current,
            insurer.claims_sum_current,
        )
        expected_state = (
            [float(item) for item in state["premiums_current_sector"]],
            [float(item) for item in state["advertising_current_sector"]],
            [float(item) for item in state["reserves_current"]],
            [float(item) for item in state["policyholders_current_sector"]],
            [int(item) for item in state["claims_count_current"]],
            [float(item) for item in state["claims_sum_current"]],
        )
        if actual_state != expected_state:
            raise ValueError("VU14 population state differs from source binding")
        apply_vu_expected_claim_rule_to_insurer(
            insurer,
            vu_expected_claim_rule_parameters_from_mapping(parameters),
            period=1,
            interest_rate=float(bav_data["interest_rate"]),
            change_shock=False,
        )
        context = SimulationContext(period=1, max_periods=100, run_index=0)
        records = collect_extended_agrsich_records(context, BAV(entity_id=1), [insurer], [])
        table = next(
            item
            for item in build_agrsich_export_tables(context, records)
            if item.spec.filename == "imsvu014.dat"
        )
        reference_path = (root / str(reference["path"])).resolve()
        legacy_row = extract_legacy_row(parse_legacy_insurer_dat(reference_path), 1)
        if legacy_row is None:
            raise ValueError("VU14 reference period 1 missing")
        comparison = compare_export_record_to_legacy_row(table, legacy_row)
    except (KeyError, TypeError, ValueError, StopIteration) as exc:
        _issue(issues, "period_one_probe_failed", str(exc))
        return {"period": 1, "matches": False, "matched_field_count": 0}
    matched = sum(field.matches for field in comparison.field_comparisons)
    return {
        "period": 1,
        "export_filename": table.spec.filename,
        "matches": comparison.matches,
        "matched_field_count": matched,
        "compared_field_count": len(comparison.field_comparisons),
        "state_origin": "Vdefmd6_initialization",
        "legacy_read_after_generation": True,
    }


if __name__ == "__main__":
    raise SystemExit(main())
