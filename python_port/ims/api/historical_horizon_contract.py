from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from ims.api.historical_reference_layer_contract import (
    HistoricalReferenceLayerContractResult,
    HistoricalReferenceLayerTarget,
    build_historical_reference_layer_contract,
)
from ims.model.agrsich_export import (
    INSURER_HEADER,
    POLICYHOLDER_HEADER,
    ExportTable,
)
from ims.model.legacy_calculated_comparison import (
    RequiredCalculatedExport,
    build_calculated_legacy_comparison_plan,
)
from ims.model.legacy_export_identity import canonicalize_legacy_export_selector
from ims.model.legacy_validation_run import (
    LegacyValidationTarget,
    load_legacy_validation_targets_from_fixture,
)


CONTRACT_VERSION = "pr92-v1"
DEFAULT_FIXTURE_PATH = Path("tests/fixtures/legacy_validation_bundle.json")
SUPPORTED_HORIZONS = (100, 300, 500)
EXPECTED_HORIZON_EXPORT_COUNTS = {100: 2, 300: 2, 500: 11}


@dataclass(frozen=True)
class HistoricalHorizonIssue:
    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class HistoricalHorizonReferenceSlice:
    reference_filename: str
    period_start: int
    period_end: int
    row_count: int
    layer_id: str
    coherence_class: str
    allowed_claim: str

    def to_dict(self) -> dict[str, object]:
        return {
            "reference_filename": self.reference_filename,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "row_count": self.row_count,
            "layer_id": self.layer_id,
            "coherence_class": self.coherence_class,
            "allowed_claim": self.allowed_claim,
        }


@dataclass(frozen=True)
class HistoricalHorizonExportContract:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None
    required_horizon: int
    required_period_count: int
    prefix_checkpoints: tuple[int, ...]
    layer_ids: tuple[str, ...]
    horizon_layer_ids: tuple[tuple[int, tuple[str, ...]], ...]
    allowed_claims: tuple[str, ...]
    reference_slices: tuple[HistoricalHorizonReferenceSlice, ...]

    @property
    def identity(self) -> tuple[str, str, str, int | str | None]:
        return (
            self.subject_type,
            self.level,
            self.selector_kind,
            self.selector_value,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "required_horizon": self.required_horizon,
            "required_period_count": self.required_period_count,
            "prefix_checkpoints": list(self.prefix_checkpoints),
            "layer_ids": list(self.layer_ids),
            "horizon_layer_ids": {
                str(horizon): list(layer_ids)
                for horizon, layer_ids in self.horizon_layer_ids
            },
            "allowed_claims": list(self.allowed_claims),
            "reference_target_count": len(self.reference_slices),
            "reference_slices": [item.to_dict() for item in self.reference_slices],
        }


@dataclass(frozen=True)
class HistoricalHorizonContractResult:
    status: str
    root: str
    fixture_path: str
    configured_horizons: tuple[int, ...]
    entries: tuple[HistoricalHorizonExportContract, ...]
    reference_layer_status: str
    reference_layer_gate_decision: str
    issues: tuple[HistoricalHorizonIssue, ...]
    mode: str = "historical_horizon_contract"

    def to_dict(self) -> dict[str, object]:
        horizon_counts = {
            str(horizon): sum(
                entry.required_horizon == horizon for entry in self.entries
            )
            for horizon in self.configured_horizons
        }
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "root": self.root,
            "fixture_path": self.fixture_path,
            "configured_horizons": list(self.configured_horizons),
            "required_export_count": len(self.entries),
            "reference_target_count": sum(
                len(entry.reference_slices) for entry in self.entries
            ),
            "required_period_count": sum(
                entry.required_period_count for entry in self.entries
            ),
            "horizon_export_counts": horizon_counts,
            "prefix_checkpoints": list(self.configured_horizons[:-1]),
            "reference_layer_contract_version": "pr91-v1",
            "reference_layer_status": self.reference_layer_status,
            "reference_layer_gate_decision": self.reference_layer_gate_decision,
            "entries": [entry.to_dict() for entry in self.entries],
            "issues": [issue.to_dict() for issue in self.issues],
            "prefix_validation_available": True,
            "prefix_validation_performed": False,
            "full_window_comparison_performed": False,
            "legacy_bundle_changed": False,
            "writes_performed": False,
            "execution_performed": False,
            "runner_started": False,
            "simulation_performed": False,
            "historical_run_identity_claimed": False,
            "historical_full_equality_claimed": False,
            "production_release_approved": False,
        }


@dataclass(frozen=True)
class LayeredExportTableSnapshot:
    horizon: int
    layer_ids: tuple[str, ...]
    table: ExportTable


@dataclass(frozen=True)
class HistoricalPrefixValidationResult:
    status: str
    snapshot_count: int
    comparison_count: int
    compared_row_count: int
    one_hundred_prefix_comparison_count: int
    issues: tuple[HistoricalHorizonIssue, ...]
    mode: str = "historical_horizon_prefix_validation"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "snapshot_count": self.snapshot_count,
            "comparison_count": self.comparison_count,
            "compared_row_count": self.compared_row_count,
            "one_hundred_prefix_comparison_count": (
                self.one_hundred_prefix_comparison_count
            ),
            "prefix_stable": self.status == "ok",
            "issues": [issue.to_dict() for issue in self.issues],
            "comparison_is_exact": True,
            "tolerance_applied": False,
            "writes_performed": False,
            "execution_performed": False,
            "runner_started": False,
            "simulation_performed": False,
            "historical_full_equality_claimed": False,
        }


def build_historical_horizon_contract(
    root: Path | str = ".",
    *,
    fixture_path: Path | str = DEFAULT_FIXTURE_PATH,
    configured_horizons: Sequence[int] = SUPPORTED_HORIZONS,
) -> HistoricalHorizonContractResult:
    resolved_root = Path(root).expanduser().resolve()
    resolved_fixture = _resolve_path(resolved_root, fixture_path)
    horizons = tuple(configured_horizons)
    issues: list[HistoricalHorizonIssue] = []
    _validate_horizons(horizons, issues)

    layer_contract = build_historical_reference_layer_contract(root=resolved_root)
    if (
        layer_contract.status == "error"
        or layer_contract.gate_decision != "go_separate_reference_tests"
    ):
        issues.append(
            HistoricalHorizonIssue(
                code="reference_layer_gate_closed",
                path="pr91-v1",
                message=(
                    "PR91 reference layers must allow separate reference tests "
                    "before a horizon contract can be built"
                ),
            )
        )

    try:
        plan = build_calculated_legacy_comparison_plan(resolved_fixture)
        targets = load_legacy_validation_targets_from_fixture(resolved_fixture)
    except (OSError, UnicodeError, ValueError) as error:
        issues.append(
            HistoricalHorizonIssue(
                code="legacy_bundle_invalid",
                path=str(resolved_fixture),
                message=f"legacy validation bundle is invalid: {error}",
            )
        )
        return _contract_result(
            resolved_root,
            resolved_fixture,
            horizons,
            (),
            layer_contract,
            issues,
        )

    layer_targets = {
        target.reference_filename: target for target in layer_contract.targets
    }
    entries = tuple(
        _build_export_contract(
            required,
            targets,
            layer_targets,
            horizons,
            issues,
        )
        for required in plan.required_exports
    )
    _validate_complete_contract(entries, plan.target_count, issues)
    return _contract_result(
        resolved_root,
        resolved_fixture,
        horizons,
        entries,
        layer_contract,
        issues,
    )


def validate_historical_horizon_prefixes(
    contract: HistoricalHorizonContractResult,
    snapshots: Sequence[LayeredExportTableSnapshot],
) -> HistoricalPrefixValidationResult:
    issues: list[HistoricalHorizonIssue] = []
    if contract.status != "ready":
        issues.append(
            HistoricalHorizonIssue(
                code="horizon_contract_not_ready",
                path=contract.fixture_path,
                message="prefix validation requires a ready horizon contract",
            )
        )
    entries = {entry.filename: entry for entry in contract.entries}
    indexed: dict[tuple[str, int], LayeredExportTableSnapshot] = {}
    valid_keys: set[tuple[str, int]] = set()
    for snapshot in snapshots:
        filename = snapshot.table.spec.filename.lower()
        key = (filename, snapshot.horizon)
        if key in indexed:
            issues.append(
                HistoricalHorizonIssue(
                    code="snapshot_duplicate",
                    path=_snapshot_label(*key),
                    message="horizon snapshots must be unique by export and horizon",
                )
            )
            continue
        indexed[key] = snapshot
        entry = entries.get(filename)
        if entry is None:
            issues.append(
                HistoricalHorizonIssue(
                    code="snapshot_export_unexpected",
                    path=_snapshot_label(*key),
                    message="snapshot export is not part of the PR92 horizon contract",
                )
            )
            continue
        if _validate_snapshot(contract, entry, snapshot, issues):
            valid_keys.add(key)

    comparison_count = 0
    compared_row_count = 0
    one_hundred_count = 0
    minimum_horizon = min(contract.configured_horizons, default=0)
    extended_snapshot_count = sum(
        snapshot.horizon > minimum_horizon for snapshot in snapshots
    )
    for key in sorted(valid_keys):
        filename, horizon = key
        entry = entries[filename]
        if horizon <= minimum_horizon:
            continue
        for checkpoint in entry.prefix_checkpoints:
            if checkpoint >= horizon:
                continue
            lower_key = (filename, checkpoint)
            lower = indexed.get(lower_key)
            if lower_key not in valid_keys or lower is None:
                issues.append(
                    HistoricalHorizonIssue(
                        code="prefix_checkpoint_missing",
                        path=_snapshot_label(filename, horizon),
                        message=f"required prefix snapshot is missing: {checkpoint}",
                    )
                )
                continue
            comparison_count += 1
            compared_row_count += checkpoint
            if checkpoint == 100:
                one_hundred_count += 1
            higher = indexed[key]
            mismatch_period = _first_prefix_mismatch(lower.table, higher.table)
            if mismatch_period is not None:
                issues.append(
                    HistoricalHorizonIssue(
                        code="prefix_row_mismatch",
                        path=_snapshot_label(filename, horizon),
                        message=(
                            f"snapshot differs from the {checkpoint}-period prefix "
                            f"at period {mismatch_period}"
                        ),
                    )
                )
    if not extended_snapshot_count:
        issues.append(
            HistoricalHorizonIssue(
                code="extended_snapshot_missing",
                path=contract.fixture_path,
                message="prefix validation requires at least one extended snapshot",
            )
        )
    return HistoricalPrefixValidationResult(
        status="error" if issues else "ok",
        snapshot_count=len(snapshots),
        comparison_count=comparison_count,
        compared_row_count=compared_row_count,
        one_hundred_prefix_comparison_count=one_hundred_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_historical_horizon_contract(
        args.root,
        fixture_path=args.fixture,
        configured_horizons=args.horizons,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _build_export_contract(
    required: RequiredCalculatedExport,
    targets: Sequence[LegacyValidationTarget],
    layer_targets: dict[str, HistoricalReferenceLayerTarget],
    horizons: tuple[int, ...],
    issues: list[HistoricalHorizonIssue],
) -> HistoricalHorizonExportContract:
    required_horizon = required.periods[-1] if required.periods else 0
    if required.periods != list(range(1, required_horizon + 1)):
        issues.append(
            HistoricalHorizonIssue(
                code="export_periods_not_contiguous",
                path=required.filename,
                message="required export periods must be contiguous from 1",
            )
        )
    if required_horizon not in horizons:
        issues.append(
            HistoricalHorizonIssue(
                code="required_horizon_not_configured",
                path=required.filename,
                message=f"required horizon is not configured: {required_horizon}",
            )
        )
    matching_targets = [
        target
        for target in targets
        if target.export_filename == required.filename
        and target.subject_type == required.subject_type
        and target.level == required.level
        and target.selector_kind == required.selector_kind
        and target.selector_value == required.selector_value
    ]
    slices = tuple(
        sorted(
            (
                _build_reference_slice(target, layer_targets, issues)
                for target in matching_targets
            ),
            key=lambda item: (item.period_start, item.period_end, item.reference_filename),
        )
    )
    snapshot_horizons = tuple(
        horizon for horizon in horizons if horizon <= required_horizon
    )
    return HistoricalHorizonExportContract(
        filename=required.filename,
        subject_type=required.subject_type,
        level=required.level,
        selector_kind=required.selector_kind,
        selector_value=required.selector_value,
        required_horizon=required_horizon,
        required_period_count=len(required.periods),
        prefix_checkpoints=tuple(
            horizon for horizon in horizons if horizon < required_horizon
        ),
        layer_ids=_ordered_unique(item.layer_id for item in slices),
        horizon_layer_ids=tuple(
            (
                horizon,
                _ordered_unique(
                    item.layer_id
                    for item in slices
                    if item.period_start <= horizon
                ),
            )
            for horizon in snapshot_horizons
        ),
        allowed_claims=_ordered_unique(item.allowed_claim for item in slices),
        reference_slices=slices,
    )


def _build_reference_slice(
    target: LegacyValidationTarget,
    layer_targets: dict[str, HistoricalReferenceLayerTarget],
    issues: list[HistoricalHorizonIssue],
) -> HistoricalHorizonReferenceSlice:
    filename = target.legacy_path.name
    layer_target = layer_targets.get(filename)
    if layer_target is None:
        issues.append(
            HistoricalHorizonIssue(
                code="reference_layer_missing",
                path=filename,
                message="legacy target has no PR91 reference layer binding",
            )
        )
        return HistoricalHorizonReferenceSlice(
            reference_filename=filename,
            period_start=min(target.periods),
            period_end=max(target.periods),
            row_count=len(target.periods),
            layer_id="missing",
            coherence_class="unresolved",
            allowed_claim="none",
        )
    expected_identity = (
        target.subject_type,
        target.level,
        target.selector_kind,
        target.selector_value,
    )
    actual_identity = (
        layer_target.subject_type,
        layer_target.level,
        layer_target.selector_kind,
        layer_target.selector_value,
    )
    if expected_identity != actual_identity:
        issues.append(
            HistoricalHorizonIssue(
                code="reference_identity_mismatch",
                path=filename,
                message="legacy target identity differs from its PR91 layer binding",
            )
        )
    if not target.periods or target.periods != list(
        range(min(target.periods), max(target.periods) + 1)
    ):
        issues.append(
            HistoricalHorizonIssue(
                code="reference_slice_not_contiguous",
                path=filename,
                message="legacy reference slice must contain contiguous periods",
            )
        )
    return HistoricalHorizonReferenceSlice(
        reference_filename=filename,
        period_start=min(target.periods),
        period_end=max(target.periods),
        row_count=len(target.periods),
        layer_id=layer_target.layer_id,
        coherence_class=layer_target.coherence_class,
        allowed_claim=layer_target.allowed_claim,
    )


def _validate_horizons(
    horizons: tuple[int, ...],
    issues: list[HistoricalHorizonIssue],
) -> None:
    if not horizons or horizons != tuple(sorted(set(horizons))):
        issues.append(
            HistoricalHorizonIssue(
                code="configured_horizons_invalid",
                path="configured_horizons",
                message="configured horizons must be non-empty, unique and sorted",
            )
        )
    unexpected = tuple(horizon for horizon in horizons if horizon not in SUPPORTED_HORIZONS)
    if unexpected:
        issues.append(
            HistoricalHorizonIssue(
                code="configured_horizon_unsupported",
                path="configured_horizons",
                message=f"unsupported horizon values: {unexpected}",
            )
        )


def _validate_complete_contract(
    entries: tuple[HistoricalHorizonExportContract, ...],
    target_count: int,
    issues: list[HistoricalHorizonIssue],
) -> None:
    filenames = [entry.filename for entry in entries]
    if len(entries) != 15 or len(set(filenames)) != 15:
        issues.append(
            HistoricalHorizonIssue(
                code="export_contract_count_mismatch",
                path="legacy_validation_bundle.json",
                message="horizon contract requires 15 unique export identities",
            )
        )
    if target_count != 19 or sum(len(entry.reference_slices) for entry in entries) != 19:
        issues.append(
            HistoricalHorizonIssue(
                code="reference_target_count_mismatch",
                path="legacy_validation_bundle.json",
                message="horizon contract requires 19 reference targets",
            )
        )
    if sum(entry.required_period_count for entry in entries) != 6300:
        issues.append(
            HistoricalHorizonIssue(
                code="required_period_count_mismatch",
                path="legacy_validation_bundle.json",
                message="horizon contract requires 6300 target periods",
            )
        )
    counts = {
        horizon: sum(entry.required_horizon == horizon for entry in entries)
        for horizon in SUPPORTED_HORIZONS
    }
    if counts != EXPECTED_HORIZON_EXPORT_COUNTS:
        issues.append(
            HistoricalHorizonIssue(
                code="horizon_distribution_mismatch",
                path="legacy_validation_bundle.json",
                message=f"unexpected horizon export distribution: {counts}",
            )
        )


def _validate_snapshot(
    contract: HistoricalHorizonContractResult,
    entry: HistoricalHorizonExportContract,
    snapshot: LayeredExportTableSnapshot,
    issues: list[HistoricalHorizonIssue],
) -> bool:
    label = _snapshot_label(entry.filename, snapshot.horizon)
    valid = True
    allowed_horizons = {
        *entry.prefix_checkpoints,
        entry.required_horizon,
    }
    if (
        snapshot.horizon not in contract.configured_horizons
        or snapshot.horizon not in allowed_horizons
    ):
        issues.append(
            HistoricalHorizonIssue(
                code="snapshot_horizon_invalid",
                path=label,
                message="snapshot horizon is not allowed for this export",
            )
        )
        valid = False
    actual_identity = (
        snapshot.table.spec.subject_type,
        snapshot.table.spec.level,
        snapshot.table.spec.selector_kind,
        canonicalize_legacy_export_selector(
            snapshot.table.spec.level,
            snapshot.table.spec.selector_kind,
            snapshot.table.spec.selector_value,
        ),
    )
    if actual_identity != entry.identity:
        issues.append(
            HistoricalHorizonIssue(
                code="snapshot_identity_mismatch",
                path=label,
                message="snapshot export identity differs from the horizon contract",
            )
        )
        valid = False
    expected_layer_ids = dict(entry.horizon_layer_ids).get(snapshot.horizon, ())
    if snapshot.layer_ids != expected_layer_ids:
        issues.append(
            HistoricalHorizonIssue(
                code="snapshot_layer_ids_mismatch",
                path=label,
                message="snapshot must carry the exact PR91 layer IDs",
            )
        )
        valid = False
    expected_header = (
        INSURER_HEADER if entry.subject_type == "insurer" else POLICYHOLDER_HEADER
    )
    if snapshot.table.header != expected_header:
        issues.append(
            HistoricalHorizonIssue(
                code="snapshot_header_mismatch",
                path=label,
                message="snapshot header differs from the export subject contract",
            )
        )
        valid = False
    periods = []
    for row in snapshot.table.rows:
        try:
            periods.append(int(row.values[0]))
        except (IndexError, TypeError, ValueError):
            periods.append(-1)
    if periods != list(range(1, snapshot.horizon + 1)):
        issues.append(
            HistoricalHorizonIssue(
                code="snapshot_period_boundary_mismatch",
                path=label,
                message="snapshot periods must be contiguous from 1 to its horizon",
            )
        )
        valid = False
    return valid


def _first_prefix_mismatch(lower: ExportTable, higher: ExportTable) -> int | None:
    for index, lower_row in enumerate(lower.rows):
        if lower_row.values != higher.rows[index].values:
            return index + 1
    return None


def _contract_result(
    root: Path,
    fixture: Path,
    horizons: tuple[int, ...],
    entries: tuple[HistoricalHorizonExportContract, ...],
    layer_contract: HistoricalReferenceLayerContractResult,
    issues: list[HistoricalHorizonIssue],
) -> HistoricalHorizonContractResult:
    return HistoricalHorizonContractResult(
        status="error" if issues else "ready",
        root=str(root),
        fixture_path=str(fixture),
        configured_horizons=horizons,
        entries=entries,
        reference_layer_status=layer_contract.status,
        reference_layer_gate_decision=layer_contract.gate_decision,
        issues=tuple(issues),
    )


def _ordered_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _snapshot_label(filename: str, horizon: int) -> str:
    return f"{filename}@{horizon}"


def _resolve_path(root: Path, path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_horizon_contract",
        description=(
            "Prueft den read-only Horizontvertrag 100/300/500 ohne Tabellen "
            "zu berechnen oder eine Simulation zu starten."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument(
        "--horizons",
        type=int,
        nargs="+",
        default=list(SUPPORTED_HORIZONS),
        help="Geordnete technische Horizontgrenzen.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
