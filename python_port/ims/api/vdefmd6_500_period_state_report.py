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
    VDEFMD6_300_PERIOD_STATE_POLICY_ID,
    VDEFMD6_500_PERIOD_END,
    VDEFMD6_500_PERIOD_EXECUTION_ORDER,
    VDEFMD6_500_PERIOD_STATE_POLICY_ID,
    VDEFMD6_VN_AGGREGATE_FILENAMES,
    VDEFMD6_VN_RULE_GROUP_1_FILENAMES,
    VDEFMD6_VN_RULE_GROUP_2_FILENAMES,
    VDEFMD6_VU_AGGREGATE_FILENAMES,
    Vdefmd6PreShockRunResult,
    run_vdefmd6_100_periods,
    run_vdefmd6_300_periods,
    run_vdefmd6_500_periods,
)
from ims.model.agrsich_export import ExportTable


CONTRACT_VERSION = "pr96-v1"
CONTRACT_BASE_SEED = 20260001
DEFAULT_CONTRACT_PATH = Path(
    "tests/fixtures/vdefmd6_500_period_state_contract.json"
)
EXPECTED_EXPORT_FILENAMES = (
    "imsvu014.dat",
    *VDEFMD6_VU_AGGREGATE_FILENAMES,
    *VDEFMD6_VN_RULE_GROUP_1_FILENAMES,
    *VDEFMD6_VN_RULE_GROUP_2_FILENAMES,
    *VDEFMD6_VN_AGGREGATE_FILENAMES,
)
_SOURCE_CONTRACTS = ("pr81-v1", "pr86-v1", "pr92-v1", "pr94-v1")
_BOUNDARIES = {
    "legacy_rows_used_as_generation_input": False,
    "controlled_execution_performed": True,
    "writes_performed": False,
    "scheduler_started": False,
    "simulation_performed": False,
    "historical_comparison_performed": False,
    "full_500_period_legacy_comparison_performed": False,
    "historical_run_identity_claimed": False,
    "historical_rng_equality_claimed": False,
    "historical_full_equality_claimed": False,
    "production_release_approved": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6500PeriodExportTarget:
    filename: str
    period_start: int
    period_end: int
    period_count: int
    prefix_100_period_count: int
    prefix_100_stable: bool
    prefix_300_period_count: int
    prefix_300_stable: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "period_count": self.period_count,
            "prefix_100_period_count": self.prefix_100_period_count,
            "prefix_100_stable": self.prefix_100_stable,
            "prefix_300_period_count": self.prefix_300_period_count,
            "prefix_300_stable": self.prefix_300_stable,
        }


@dataclass(frozen=True, slots=True)
class Vdefmd6500PeriodStateReport:
    repo_root: str
    contract_path: str
    summary: dict[str, object]
    prefix_summaries: dict[str, object]
    targets: tuple[Vdefmd6500PeriodExportTarget, ...]
    source_anchor_count: int
    controlled_execution_performed: bool
    issues: tuple[Vdefmd6PreShockRunIssue, ...]
    mode: str = "vdefmd6_controlled_500_period_state"

    @property
    def state_path_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "500_period_state_ready" if self.state_path_ready else "error",
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "source_contracts": list(_SOURCE_CONTRACTS),
            "base_seed": CONTRACT_BASE_SEED,
            "execution_order": list(VDEFMD6_500_PERIOD_EXECUTION_ORDER),
            "state_policy_id": VDEFMD6_500_PERIOD_STATE_POLICY_ID,
            "summary": dict(self.summary),
            "prefix_summaries": dict(self.prefix_summaries),
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


def build_vdefmd6_500_period_state_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
    baseline_100_result: Vdefmd6PreShockRunResult | None = None,
    baseline_300_result: Vdefmd6PreShockRunResult | None = None,
    extended_result: Vdefmd6PreShockRunResult | None = None,
) -> Vdefmd6500PeriodStateReport:
    root = Path(repo_root).expanduser().resolve()
    contract_file = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    issues: list[Vdefmd6PreShockRunIssue] = []
    contract = _load_contract(contract_file, issues)
    controlled_execution = (
        baseline_100_result is None
        or baseline_300_result is None
        or extended_result is None
    )
    baseline_100 = baseline_100_result or _run_100(issues)
    baseline_300 = baseline_300_result or _run_300(issues)
    extended = extended_result or _run_500(issues)
    targets = _validate_export_prefixes(
        baseline_100,
        baseline_300,
        extended,
        issues,
    )
    summary = _build_summary(extended)
    prefix_summaries = _build_prefix_summaries(
        baseline_100,
        baseline_300,
        extended,
        targets,
    )
    anchor_count = _validate_contract(
        root,
        contract_file,
        contract,
        summary,
        prefix_summaries,
        issues,
    )
    return Vdefmd6500PeriodStateReport(
        repo_root=str(root),
        contract_path=str(contract_file),
        summary=summary,
        prefix_summaries=prefix_summaries,
        targets=targets,
        source_anchor_count=anchor_count,
        controlled_execution_performed=controlled_execution,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_500_period_state_report",
        description=(
            "Prueft den kontrollierten modernen Vdefmd6-Zustand bis Periode "
            "500 und die unveraenderten Prefixe 1-100 sowie 1-300."
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_500_period_state_report(
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


def _run_100(
    issues: list[Vdefmd6PreShockRunIssue],
) -> Vdefmd6PreShockRunResult | None:
    try:
        return run_vdefmd6_100_periods(base_seed=CONTRACT_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "baseline_100_run_failed", str(error))
        return None


def _run_300(
    issues: list[Vdefmd6PreShockRunIssue],
) -> Vdefmd6PreShockRunResult | None:
    try:
        return run_vdefmd6_300_periods(base_seed=CONTRACT_BASE_SEED)
    except (TypeError, ValueError, StopIteration) as error:
        _issue(issues, "baseline_300_run_failed", str(error))
        return None


def _run_500(
    issues: list[Vdefmd6PreShockRunIssue],
) -> Vdefmd6PreShockRunResult | None:
    try:
        return run_vdefmd6_500_periods(base_seed=CONTRACT_BASE_SEED)
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


def _build_prefix_summaries(
    baseline_100: Vdefmd6PreShockRunResult | None,
    baseline_300: Vdefmd6PreShockRunResult | None,
    extended: Vdefmd6PreShockRunResult | None,
    targets: Sequence[Vdefmd6500PeriodExportTarget],
) -> dict[str, object]:
    state_100_stable = bool(
        baseline_100 is not None
        and extended is not None
        and baseline_100.period_results == extended.period_results[:99]
    )
    state_300_stable = bool(
        baseline_300 is not None
        and extended is not None
        and baseline_300.period_results == extended.period_results[:299]
    )
    return {
        "periods_1_100": {
            "period_start": 1,
            "period_end": 100,
            "state_transition_count": 99,
            "state_prefix_stable": state_100_stable,
            "export_count": len(targets),
            "export_period_count": sum(
                target.prefix_100_period_count for target in targets
            ),
            "export_prefix_stable": bool(
                len(targets) == len(EXPECTED_EXPORT_FILENAMES)
                and all(target.prefix_100_stable for target in targets)
            ),
        },
        "periods_1_300": {
            "period_start": 1,
            "period_end": 300,
            "state_transition_count": 299,
            "state_prefix_stable": state_300_stable,
            "export_count": len(targets),
            "export_period_count": sum(
                target.prefix_300_period_count for target in targets
            ),
            "export_prefix_stable": bool(
                len(targets) == len(EXPECTED_EXPORT_FILENAMES)
                and all(target.prefix_300_stable for target in targets)
            ),
        },
    }


def _validate_export_prefixes(
    baseline_100: Vdefmd6PreShockRunResult | None,
    baseline_300: Vdefmd6PreShockRunResult | None,
    extended: Vdefmd6PreShockRunResult | None,
    issues: list[Vdefmd6PreShockRunIssue],
) -> tuple[Vdefmd6500PeriodExportTarget, ...]:
    if baseline_100 is None or baseline_300 is None or extended is None:
        return ()
    _validate_run_boundaries(baseline_100, baseline_300, extended, issues)
    tables_100 = _tables_by_filename(_all_tables(baseline_100))
    tables_300 = _tables_by_filename(_all_tables(baseline_300))
    tables_500 = _tables_by_filename(_all_tables(extended))
    expected = set(EXPECTED_EXPORT_FILENAMES)
    _validate_target_set("baseline_100", tables_100, expected, issues)
    _validate_target_set("baseline_300", tables_300, expected, issues)
    _validate_target_set("extended", tables_500, expected, issues)

    targets: list[Vdefmd6500PeriodExportTarget] = []
    for filename in EXPECTED_EXPORT_FILENAMES:
        grouped = (
            tables_100.get(filename, ()),
            tables_300.get(filename, ()),
            tables_500.get(filename, ()),
        )
        if any(len(tables) != 1 for tables in grouped):
            continue
        table_100 = grouped[0][0]
        table_300 = grouped[1][0]
        table_500 = grouped[2][0]
        _validate_periods(table_100, 100, "baseline_100", filename, issues)
        _validate_periods(
            table_300,
            VDEFMD6_300_PERIOD_END,
            "baseline_300",
            filename,
            issues,
        )
        periods_500 = _validate_periods(
            table_500,
            VDEFMD6_500_PERIOD_END,
            "extended",
            filename,
            issues,
        )
        prefix_100_stable = _table_prefix_stable(table_100, table_500, 100)
        prefix_300_stable = _table_prefix_stable(
            table_300,
            table_500,
            VDEFMD6_300_PERIOD_END,
        )
        if not prefix_100_stable:
            _issue(
                issues,
                "export_100_prefix_mismatch",
                "extended export changed the exact period 1-100 prefix",
                Path(filename),
            )
        if not prefix_300_stable:
            _issue(
                issues,
                "export_300_prefix_mismatch",
                "extended export changed the exact period 1-300 prefix",
                Path(filename),
            )
        targets.append(
            Vdefmd6500PeriodExportTarget(
                filename=filename,
                period_start=periods_500[0] if periods_500 else 0,
                period_end=periods_500[-1] if periods_500 else 0,
                period_count=len(periods_500),
                prefix_100_period_count=min(len(table_100.rows), 100),
                prefix_100_stable=prefix_100_stable,
                prefix_300_period_count=min(
                    len(table_300.rows),
                    VDEFMD6_300_PERIOD_END,
                ),
                prefix_300_stable=prefix_300_stable,
            )
        )
    return tuple(targets)


def _validate_run_boundaries(
    baseline_100: Vdefmd6PreShockRunResult,
    baseline_300: Vdefmd6PreShockRunResult,
    extended: Vdefmd6PreShockRunResult,
    issues: list[Vdefmd6PreShockRunIssue],
) -> None:
    if any(
        result.base_seed != CONTRACT_BASE_SEED
        for result in (baseline_100, baseline_300, extended)
    ):
        _issue(issues, "base_seed_mismatch", "controlled base seed differs")
    expected_runs = (
        (
            "baseline_100",
            baseline_100,
            100,
            VDEFMD6_100_PERIOD_STATE_POLICY_ID,
        ),
        (
            "baseline_300",
            baseline_300,
            VDEFMD6_300_PERIOD_END,
            VDEFMD6_300_PERIOD_STATE_POLICY_ID,
        ),
        (
            "extended",
            extended,
            VDEFMD6_500_PERIOD_END,
            VDEFMD6_500_PERIOD_STATE_POLICY_ID,
        ),
    )
    for name, result, horizon, policy_id in expected_runs:
        if result.max_periods != horizon:
            _issue(issues, f"{name}_horizon_mismatch", f"{name} horizon differs")
        if result.state_policy_id != policy_id:
            _issue(
                issues,
                f"{name}_state_policy_mismatch",
                f"{name} state policy differs",
            )
        if tuple(item.period for item in result.period_results) != tuple(
            range(2, horizon + 1)
        ):
            _issue(
                issues,
                f"{name}_transition_boundary_mismatch",
                f"{name} transition periods differ",
            )
        if _crosses_closed_boundary(result):
            _issue(
                issues,
                "execution_boundary_violation",
                f"{name} run crossed a closed execution or historical claim boundary",
            )
    if extended.execution_order != VDEFMD6_500_PERIOD_EXECUTION_ORDER:
        _issue(issues, "extended_execution_order_mismatch", "execution order differs")
    if baseline_100.period_results != extended.period_results[:99]:
        _issue(issues, "state_100_prefix_mismatch", "period 2-100 state changed")
    if baseline_300.period_results != extended.period_results[:299]:
        _issue(issues, "state_300_prefix_mismatch", "period 2-300 state changed")


def _crosses_closed_boundary(result: Vdefmd6PreShockRunResult) -> bool:
    return bool(
        result.legacy_rows_used_as_generation_input
        or result.writes_performed
        or result.scheduler_started
        or result.simulation_performed
        or result.historical_same_slot_order_claimed
        or result.historical_rng_equality_claimed
        or result.historical_full_equality_claimed
    )


def _validate_periods(
    table: ExportTable,
    period_end: int,
    name: str,
    filename: str,
    issues: list[Vdefmd6PreShockRunIssue],
) -> list[int]:
    periods = _periods(table)
    if periods != list(range(1, period_end + 1)):
        _issue(
            issues,
            f"{name}_period_boundary_mismatch",
            f"{name} export must contain periods 1 through {period_end}",
            Path(filename),
        )
    return periods


def _table_prefix_stable(
    baseline: ExportTable,
    extended: ExportTable,
    period_count: int,
) -> bool:
    return bool(
        baseline.spec == extended.spec
        and baseline.header == extended.header
        and baseline.rows == extended.rows[:period_count]
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
    prefix_summaries: dict[str, object],
    issues: list[Vdefmd6PreShockRunIssue],
) -> int:
    expected = {
        "schema_version": CONTRACT_VERSION,
        "model_id": "Vdefmd6",
        "scope": (
            "controlled_modern_periods_1_500_with_stable_1_100_and_1_300_prefixes"
        ),
        "base_seed": CONTRACT_BASE_SEED,
        "execution_order": list(VDEFMD6_500_PERIOD_EXECUTION_ORDER),
        "state_policy_id": VDEFMD6_500_PERIOD_STATE_POLICY_ID,
        "expected": summary,
        "prefixes": prefix_summaries,
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
