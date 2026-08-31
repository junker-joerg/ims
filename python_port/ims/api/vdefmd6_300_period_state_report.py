from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.api.vdefmd6_pre_shock_run_report import (
    Vdefmd6PreShockRunIssue,
    validate_vdefmd6_run_source_anchors,
)
from ims.engine.vdefmd6_pre_shock_runner import (
    VDEFMD6_100_PERIOD_STATE_POLICY_ID,
    VDEFMD6_300_PERIOD_END,
    VDEFMD6_300_PERIOD_EXECUTION_ORDER,
    VDEFMD6_300_PERIOD_STATE_POLICY_ID,
    VDEFMD6_VN_AGGREGATE_FILENAMES,
    VDEFMD6_VN_RULE_GROUP_1_FILENAMES,
    VDEFMD6_VN_RULE_GROUP_2_FILENAMES,
    VDEFMD6_VU_AGGREGATE_FILENAMES,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
    run_vdefmd6_300_periods,
)
from ims.model.agrsich_export import ExportTable


CONTRACT_VERSION = "pr94-v1"
CONTRACT_BASE_SEED = 20260001
DEFAULT_CONTRACT_PATH = Path(
    "tests/fixtures/vdefmd6_300_period_state_contract.json"
)
EXPECTED_EXPORT_FILENAMES = (
    "imsvu014.dat",
    *VDEFMD6_VU_AGGREGATE_FILENAMES,
    *VDEFMD6_VN_RULE_GROUP_1_FILENAMES,
    *VDEFMD6_VN_RULE_GROUP_2_FILENAMES,
    *VDEFMD6_VN_AGGREGATE_FILENAMES,
)
_SOURCE_CONTRACTS = ("pr81-v1", "pr86-v1", "pr92-v1", "pr93-v1")
_BOUNDARIES = {
    "legacy_rows_used_as_generation_input": False,
    "controlled_execution_performed": True,
    "writes_performed": False,
    "scheduler_started": False,
    "simulation_performed": False,
    "historical_comparison_performed": False,
    "full_300_period_legacy_comparison_performed": False,
    "historical_run_identity_claimed": False,
    "historical_rng_equality_claimed": False,
    "historical_full_equality_claimed": False,
    "production_release_approved": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6300PeriodExportTarget:
    filename: str
    period_start: int
    period_end: int
    period_count: int
    prefix_period_count: int
    prefix_stable: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "period_count": self.period_count,
            "prefix_period_count": self.prefix_period_count,
            "prefix_stable": self.prefix_stable,
        }


@dataclass(frozen=True, slots=True)
class Vdefmd6300PeriodStateReport:
    repo_root: str
    contract_path: str
    summary: dict[str, object]
    prefix_summary: dict[str, object]
    targets: tuple[Vdefmd6300PeriodExportTarget, ...]
    source_anchor_count: int
    controlled_execution_performed: bool
    issues: tuple[Vdefmd6PreShockRunIssue, ...]
    mode: str = "vdefmd6_controlled_300_period_state"

    @property
    def state_path_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "300_period_state_ready" if self.state_path_ready else "error",
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "source_contracts": list(_SOURCE_CONTRACTS),
            "base_seed": CONTRACT_BASE_SEED,
            "execution_order": list(VDEFMD6_300_PERIOD_EXECUTION_ORDER),
            "state_policy_id": VDEFMD6_300_PERIOD_STATE_POLICY_ID,
            "summary": dict(self.summary),
            "prefix_summary": dict(self.prefix_summary),
            "targets": [target.to_dict() for target in self.targets],
            "source_anchor_count": self.source_anchor_count,
            **{
                **_BOUNDARIES,
                "controlled_execution_performed": (
                    self.controlled_execution_performed
                ),
            },
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_300_period_state_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
    baseline_result: Vdefmd6PreShockRunResult | None = None,
    extended_result: Vdefmd6PreShockRunResult | None = None,
) -> Vdefmd6300PeriodStateReport:
    root = Path(repo_root).expanduser().resolve()
    contract_file = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    issues: list[Vdefmd6PreShockRunIssue] = []
    contract = _load_contract(contract_file, issues)
    controlled_execution = baseline_result is None or extended_result is None
    baseline = baseline_result or _run_baseline(issues)
    extended = extended_result or _run_extended(issues)
    targets = _validate_export_prefixes(baseline, extended, issues)
    summary = _build_summary(extended)
    prefix_summary = _build_prefix_summary(baseline, extended, targets)
    anchor_count = _validate_contract(
        root,
        contract_file,
        contract,
        summary,
        prefix_summary,
        issues,
    )
    return Vdefmd6300PeriodStateReport(
        repo_root=str(root),
        contract_path=str(contract_file),
        summary=summary,
        prefix_summary=prefix_summary,
        targets=targets,
        source_anchor_count=anchor_count,
        controlled_execution_performed=controlled_execution,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_300_period_state_report",
        description=(
            "Prueft den kontrollierten modernen Vdefmd6-Zustand bis Periode "
            "300 und den unveraenderten Prefix 1-100."
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_300_period_state_report(
        args.repo_root,
        contract_path=args.contract,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.state_path_ready else 1


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _load_contract(
    path: Path,
    issues: list[Vdefmd6PreShockRunIssue],
) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        _issue(issues, "contract_unreadable", str(error), path)
        return {}
    if not isinstance(payload, dict):
        _issue(issues, "contract_shape_invalid", "contract must be an object", path)
        return {}
    return payload


def _run_baseline(
    issues: list[Vdefmd6PreShockRunIssue],
) -> Vdefmd6PreShockRunResult | None:
    try:
        return run_vdefmd6_100_periods(base_seed=CONTRACT_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "baseline_run_failed", str(error))
        return None


def _run_extended(
    issues: list[Vdefmd6PreShockRunIssue],
) -> Vdefmd6PreShockRunResult | None:
    try:
        return run_vdefmd6_300_periods(base_seed=CONTRACT_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "extended_run_failed", str(error))
        return None


def _build_summary(
    result: Vdefmd6PreShockRunResult | None,
) -> dict[str, object]:
    if result is None:
        return {}
    tables = _all_tables(result)
    return {
        "max_periods": result.max_periods,
        "transition_period_start": (
            result.period_results[0].period if result.period_results else None
        ),
        "transition_period_end": (
            result.period_results[-1].period if result.period_results else None
        ),
        "transition_period_count": len(result.period_results),
        "export_count": len(tables),
        "export_period_count": sum(len(table.rows) for table in tables),
        "total_vu_rule_applications": result.total_vu_rule_applications,
        "total_vn_insurance_rule_applications": (
            result.total_vn_insurance_rule_applications
        ),
        "total_vn_damage_settlement_applications": (
            result.total_vn_damage_settlement_applications
        ),
        "total_uniform_value_count": result.total_uniform_value_count,
        "total_normal_value_count": result.total_normal_value_count,
        "total_information_cost": result.total_information_cost,
        "total_information_cost_policyholders": (
            result.total_information_cost_policyholders
        ),
    }


def _build_prefix_summary(
    baseline: Vdefmd6PreShockRunResult | None,
    extended: Vdefmd6PreShockRunResult | None,
    targets: Sequence[Vdefmd6300PeriodExportTarget],
) -> dict[str, object]:
    state_stable = bool(
        baseline is not None
        and extended is not None
        and baseline.period_results == extended.period_results[:99]
    )
    return {
        "period_start": 1,
        "period_end": 100,
        "state_transition_count": 99,
        "state_prefix_stable": state_stable,
        "export_count": len(targets),
        "export_period_count": sum(target.prefix_period_count for target in targets),
        "export_prefix_stable": bool(
            len(targets) == len(EXPECTED_EXPORT_FILENAMES)
            and all(target.prefix_stable for target in targets)
        ),
    }


def _validate_export_prefixes(
    baseline: Vdefmd6PreShockRunResult | None,
    extended: Vdefmd6PreShockRunResult | None,
    issues: list[Vdefmd6PreShockRunIssue],
) -> tuple[Vdefmd6300PeriodExportTarget, ...]:
    if baseline is None or extended is None:
        return ()
    _validate_run_boundaries(baseline, extended, issues)
    baseline_by_filename = _tables_by_filename(_all_tables(baseline))
    extended_by_filename = _tables_by_filename(_all_tables(extended))
    expected = set(EXPECTED_EXPORT_FILENAMES)
    _validate_target_set("baseline", baseline_by_filename, expected, issues)
    _validate_target_set("extended", extended_by_filename, expected, issues)

    targets: list[Vdefmd6300PeriodExportTarget] = []
    for filename in EXPECTED_EXPORT_FILENAMES:
        baseline_tables = baseline_by_filename.get(filename, ())
        extended_tables = extended_by_filename.get(filename, ())
        if len(baseline_tables) != 1 or len(extended_tables) != 1:
            continue
        baseline_table = baseline_tables[0]
        extended_table = extended_tables[0]
        baseline_periods = _periods(baseline_table)
        extended_periods = _periods(extended_table)
        if baseline_periods != list(range(1, 101)):
            _issue(
                issues,
                "baseline_period_boundary_mismatch",
                "baseline export must contain periods 1 through 100",
                Path(filename),
            )
        if extended_periods != list(range(1, VDEFMD6_300_PERIOD_END + 1)):
            _issue(
                issues,
                "extended_period_boundary_mismatch",
                "extended export must contain periods 1 through 300",
                Path(filename),
            )
        prefix_stable = bool(
            baseline_table.spec == extended_table.spec
            and baseline_table.header == extended_table.header
            and baseline_table.rows == extended_table.rows[:100]
        )
        if not prefix_stable:
            _issue(
                issues,
                "export_prefix_mismatch",
                "extended export changed the exact period 1-100 prefix",
                Path(filename),
            )
        targets.append(
            Vdefmd6300PeriodExportTarget(
                filename=filename,
                period_start=extended_periods[0] if extended_periods else 0,
                period_end=extended_periods[-1] if extended_periods else 0,
                period_count=len(extended_periods),
                prefix_period_count=min(len(baseline_table.rows), 100),
                prefix_stable=prefix_stable,
            )
        )
    return tuple(targets)


def _validate_run_boundaries(
    baseline: Vdefmd6PreShockRunResult,
    extended: Vdefmd6PreShockRunResult,
    issues: list[Vdefmd6PreShockRunIssue],
) -> None:
    if baseline.base_seed != CONTRACT_BASE_SEED or extended.base_seed != CONTRACT_BASE_SEED:
        _issue(issues, "base_seed_mismatch", "controlled base seed differs")
    if baseline.max_periods != 100:
        _issue(issues, "baseline_horizon_mismatch", "baseline horizon must be 100")
    if extended.max_periods != VDEFMD6_300_PERIOD_END:
        _issue(issues, "extended_horizon_mismatch", "extended horizon must be 300")
    if baseline.state_policy_id != VDEFMD6_100_PERIOD_STATE_POLICY_ID:
        _issue(issues, "baseline_state_policy_mismatch", "baseline state policy differs")
    if extended.state_policy_id != VDEFMD6_300_PERIOD_STATE_POLICY_ID:
        _issue(issues, "extended_state_policy_mismatch", "extended state policy differs")
    if extended.execution_order != VDEFMD6_300_PERIOD_EXECUTION_ORDER:
        _issue(issues, "extended_execution_order_mismatch", "execution order differs")
    if tuple(item.period for item in baseline.period_results) != tuple(range(2, 101)):
        _issue(issues, "baseline_transition_boundary_mismatch", "baseline periods differ")
    if tuple(item.period for item in extended.period_results) != tuple(range(2, 301)):
        _issue(issues, "extended_transition_boundary_mismatch", "extended periods differ")
    if baseline.period_results != extended.period_results[:99]:
        _issue(issues, "state_prefix_mismatch", "period 2-100 state results changed")
    for name, result in (("baseline", baseline), ("extended", extended)):
        if (
            result.legacy_rows_used_as_generation_input
            or result.writes_performed
            or result.scheduler_started
            or result.simulation_performed
            or result.historical_same_slot_order_claimed
            or result.historical_rng_equality_claimed
            or result.historical_full_equality_claimed
        ):
            _issue(
                issues,
                "execution_boundary_violation",
                f"{name} run crossed a closed execution or historical claim boundary",
            )


def _all_tables(result: Vdefmd6PreShockRunResult) -> tuple[ExportTable, ...]:
    return (
        result.vu14_export_table,
        *result.vu_aggregate_export_tables,
        *result.vn_rule_group_1_export_tables,
        *result.vn_rule_group_2_export_tables,
        *result.vn_aggregate_export_tables,
    )


def _tables_by_filename(
    tables: Sequence[ExportTable],
) -> dict[str, tuple[ExportTable, ...]]:
    grouped: dict[str, list[ExportTable]] = {}
    for table in tables:
        grouped.setdefault(table.spec.filename.lower(), []).append(table)
    return {filename: tuple(items) for filename, items in grouped.items()}


def _validate_target_set(
    name: str,
    tables: dict[str, tuple[ExportTable, ...]],
    expected: set[str],
    issues: list[Vdefmd6PreShockRunIssue],
) -> None:
    actual = set(tables)
    if actual != expected or any(len(items) != 1 for items in tables.values()):
        _issue(
            issues,
            f"{name}_export_set_mismatch",
            f"{name} export set must contain each of the 15 targets exactly once",
        )


def _periods(table: ExportTable) -> list[int]:
    periods: list[int] = []
    for row in table.rows:
        try:
            periods.append(int(row.values[0]))
        except (IndexError, TypeError, ValueError):
            periods.append(-1)
    return periods


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    prefix_summary: dict[str, object],
    issues: list[Vdefmd6PreShockRunIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": "controlled_modern_periods_1_300_with_stable_1_100_prefix",
        "base_seed": CONTRACT_BASE_SEED,
        "execution_order": list(VDEFMD6_300_PERIOD_EXECUTION_ORDER),
        "state_policy_id": VDEFMD6_300_PERIOD_STATE_POLICY_ID,
        "expected": summary,
        "prefix": prefix_summary,
        "export_filenames": list(EXPECTED_EXPORT_FILENAMES),
        "source_contracts": list(_SOURCE_CONTRACTS),
        "boundaries": _BOUNDARIES,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            _issue(issues, f"{key}_mismatch", f"contract field differs: {key}", path)
    return validate_vdefmd6_run_source_anchors(root, contract, issues)


def _issue(
    issues: list[Vdefmd6PreShockRunIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        Vdefmd6PreShockRunIssue(
            code=code,
            message=message,
            path=str(path) if path is not None else None,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
