from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.controlled_execution_adapter_contract import (
    ControlledExecutionAdapterContract,
    build_controlled_execution_adapter_contract,
)
from ims.engine.explicit_period_plan import run_explicit_multi_period_from_plan_fixture
from ims.engine.explicit_period_runner import (
    build_explicit_multi_period_execution_summary,
    run_explicit_multi_period_from_fixture,
)


EXPLICIT_PLAN_FIXTURE_KIND = "explicit_vu_vn_period_plan_fixture"
EXPLICIT_MULTI_PERIOD_FIXTURE_KIND = "explicit_multi_period_fixture"


@dataclass(frozen=True)
class ControlledExecutionAdapterResult:
    status: str
    mode: str
    adapter_mode: str
    fixture_path: str
    fixture_kind: str
    explicit_execution_release: bool
    requested_carry_forward_vu_state: bool
    requested_carry_forward_vn_state: bool
    summary: dict[str, object]
    contract: ControlledExecutionAdapterContract
    http_enabled: bool = False
    ui_enabled: bool = False
    queue_worker_enabled: bool = False
    writes_enabled: bool = False
    writes_performed: bool = False
    execution_performed: bool = True
    simulation_performed: bool = False
    automatic_historical_rule_selection_performed: bool = False
    historical_full_equality_claimed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "adapter_mode": self.adapter_mode,
            "fixture_path": self.fixture_path,
            "fixture_kind": self.fixture_kind,
            "explicit_execution_release": self.explicit_execution_release,
            "requested_carry_forward_vu_state": self.requested_carry_forward_vu_state,
            "requested_carry_forward_vn_state": self.requested_carry_forward_vn_state,
            "summary": dict(self.summary),
            "contract": self.contract.to_dict(),
            "http_enabled": self.http_enabled,
            "ui_enabled": self.ui_enabled,
            "queue_worker_enabled": self.queue_worker_enabled,
            "writes_enabled": self.writes_enabled,
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
            "simulation_performed": self.simulation_performed,
            "automatic_historical_rule_selection_performed": (
                self.automatic_historical_rule_selection_performed
            ),
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
        }


def run_controlled_execution_adapter(
    fixture_path: str | Path,
    *,
    adapter_mode: str = "explicit_multi_period_fixture_adapter",
    explicit_execution_release: bool = False,
    carry_forward_vu_state: bool = False,
    carry_forward_vn_state: bool = False,
) -> ControlledExecutionAdapterResult:
    contract = build_controlled_execution_adapter_contract()
    if adapter_mode != contract.adapter_mode:
        raise ValueError(f"unsupported controlled execution adapter_mode: {adapter_mode}")
    if not explicit_execution_release:
        raise ValueError("explicit_execution_release is required for the local adapter")

    resolved_fixture_path = Path(fixture_path).resolve()
    fixture_kind = detect_controlled_execution_fixture_kind(resolved_fixture_path)
    if fixture_kind not in contract.accepted_fixture_kinds:
        raise ValueError(f"unsupported controlled execution fixture kind: {fixture_kind}")

    if fixture_kind == EXPLICIT_PLAN_FIXTURE_KIND:
        result = run_explicit_multi_period_from_plan_fixture(resolved_fixture_path)
    else:
        result = run_explicit_multi_period_from_fixture(
            resolved_fixture_path,
            carry_forward_vu_state=carry_forward_vu_state,
            carry_forward_vn_state=carry_forward_vn_state,
        )

    summary = build_explicit_multi_period_execution_summary(result).to_dict()
    _validate_summary_shape(summary, contract)
    return ControlledExecutionAdapterResult(
        status="ok",
        mode="controlled_execution_adapter",
        adapter_mode=adapter_mode,
        fixture_path=str(resolved_fixture_path),
        fixture_kind=fixture_kind,
        explicit_execution_release=True,
        requested_carry_forward_vu_state=carry_forward_vu_state,
        requested_carry_forward_vn_state=carry_forward_vn_state,
        summary=summary,
        contract=contract,
        writes_performed=bool(summary["writes_performed"]),
        execution_performed=bool(summary["execution_performed"]),
        simulation_performed=bool(summary["simulation_performed"]),
        automatic_historical_rule_selection_performed=bool(
            summary["automatic_historical_rule_selection_performed"]
        ),
    )


def detect_controlled_execution_fixture_kind(path: str | Path) -> str:
    with Path(path).resolve().open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("controlled execution fixture must be a JSON object")
    if isinstance(payload.get("periods"), list):
        return EXPLICIT_MULTI_PERIOD_FIXTURE_KIND
    if isinstance(payload.get("base_snapshot"), dict) and isinstance(payload.get("period_updates"), list):
        return EXPLICIT_PLAN_FIXTURE_KIND
    raise ValueError("controlled execution fixture must contain periods or base_snapshot plus period_updates")


def _validate_summary_shape(
    summary: dict[str, object],
    contract: ControlledExecutionAdapterContract,
) -> None:
    summary_fields = tuple(summary.keys())
    if summary_fields != contract.expected_summary_fields:
        raise ValueError("controlled execution summary does not match the expected contract shape")
    if summary["simulation_performed"] is not False:
        raise ValueError("controlled execution adapter must not report simulation_performed=true")
    if summary["automatic_historical_rule_selection_performed"] is not False:
        raise ValueError("controlled execution adapter must not use automatic historical rule selection")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = run_controlled_execution_adapter(
        args.fixture,
        adapter_mode=args.adapter_mode,
        explicit_execution_release=args.explicit_execution_release,
        carry_forward_vu_state=args.carry_forward_vu_state,
        carry_forward_vn_state=args.carry_forward_vn_state,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fuehrt einen explizit freigegebenen lokalen IMS-Fixture-Adapter aus."
    )
    parser.add_argument("--fixture", required=True, help="Pfad zu einem expliziten VU/VN-Fixture.")
    parser.add_argument(
        "--adapter-mode",
        default="explicit_multi_period_fixture_adapter",
        help="Muss dem kontrollierten Adaptervertrag entsprechen.",
    )
    parser.add_argument(
        "--explicit-execution-release",
        action="store_true",
        required=True,
        help="Explizite lokale Freigabe; ohne dieses Flag startet der Adapter nicht.",
    )
    parser.add_argument(
        "--carry-forward-vu-state",
        action="store_true",
        help="Optionaler VU-State-Carryover fuer einfache Mehrperiodenfixtures.",
    )
    parser.add_argument(
        "--carry-forward-vn-state",
        action="store_true",
        help="Optionaler VN-State-Carryover fuer einfache Mehrperiodenfixtures.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
