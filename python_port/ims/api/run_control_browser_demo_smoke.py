from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Sequence

from ims.api.app import create_app
from ims.api.controlled_execution_adapter import (
    EXPLICIT_MULTI_PERIOD_FIXTURE_KIND,
    ControlledExecutionAdapterResult,
)
from ims.api.controlled_execution_adapter_contract import (
    build_controlled_execution_adapter_contract,
)
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import (
    build_seeded_metadata_repository,
    connect_metadata_db,
)
from ims.api.run_control_queue import WorkbenchRunControlQueueRepository
from ims.api.run_control_requests import WorkbenchRunControlRequest


BROWSER_DEMO_SMOKE_QUEUE_ID = "baseline-python-tests"
BROWSER_DEMO_SMOKE_SCENARIO_ID = "agrsich-reference-window"
BROWSER_DEMO_SMOKE_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def create_browser_demo_smoke_app(
    *,
    db_path: str | Path,
    frontend_dist: str | Path,
    adapter_calls: list[dict[str, object]] | None = None,
) -> Any:
    resolved_db_path = Path(db_path).expanduser().resolve()
    resolved_frontend_dist = Path(frontend_dist).expanduser().resolve()
    if resolved_db_path.exists():
        raise MetadataImportError(
            f"browser demo smoke requires a fresh metadata database: {resolved_db_path}"
        )
    if not (resolved_frontend_dist / "index.html").is_file():
        raise MetadataImportError(
            f"browser demo smoke requires a built frontend: {resolved_frontend_dist}"
        )

    resolved_db_path.parent.mkdir(parents=True, exist_ok=True)
    repository = build_seeded_metadata_repository(resolved_db_path)
    connection = connect_metadata_db(resolved_db_path)
    try:
        WorkbenchRunControlQueueRepository(connection).enqueue(
            WorkbenchRunControlRequest(
                run_id=BROWSER_DEMO_SMOKE_QUEUE_ID,
                scenario_id=BROWSER_DEMO_SMOKE_SCENARIO_ID,
                requested_by="pr66-browser-smoke",
                created_at="2026-08-25T00:00:00Z",
                metadata_db=str(resolved_db_path),
            ),
            status="validated",
        )
    finally:
        connection.close()

    observed_calls = adapter_calls if adapter_calls is not None else []

    def controlled_smoke_adapter(
        fixture_path: str | Path,
        *,
        adapter_mode: str,
        explicit_execution_release: bool,
        carry_forward_vu_state: bool,
        carry_forward_vn_state: bool,
    ) -> ControlledExecutionAdapterResult:
        if adapter_mode != "explicit_multi_period_fixture_adapter":
            raise ValueError(f"unexpected browser smoke adapter mode: {adapter_mode}")
        if not explicit_execution_release:
            raise ValueError("browser smoke adapter requires explicit execution release")
        if carry_forward_vu_state or carry_forward_vn_state:
            raise ValueError("browser smoke adapter refuses carryover")

        resolved_fixture_path = Path(fixture_path).resolve()
        observed_calls.append(
            {
                "fixture_path": str(resolved_fixture_path),
                "adapter_mode": adapter_mode,
                "explicit_execution_release": explicit_execution_release,
                "carry_forward_vu_state": carry_forward_vu_state,
                "carry_forward_vn_state": carry_forward_vn_state,
            }
        )
        return ControlledExecutionAdapterResult(
            status="ok",
            mode="controlled_execution_adapter",
            adapter_mode=adapter_mode,
            fixture_path=str(resolved_fixture_path),
            fixture_kind=EXPLICIT_MULTI_PERIOD_FIXTURE_KIND,
            explicit_execution_release=True,
            requested_carry_forward_vu_state=False,
            requested_carry_forward_vn_state=False,
            summary=_synthetic_execution_summary(),
            contract=build_controlled_execution_adapter_contract(),
        )

    return create_app(
        frontend_dist=resolved_frontend_dist,
        metadata_repository=repository,
        adapter_runner=controlled_smoke_adapter,
    )


def require_browser_demo_smoke_host(host: str) -> str:
    normalized_host = host.strip().lower()
    if normalized_host not in BROWSER_DEMO_SMOKE_HOSTS:
        raise MetadataImportError(
            "browser demo smoke server must use a loopback host: "
            + ", ".join(sorted(BROWSER_DEMO_SMOKE_HOSTS))
        )
    return normalized_host


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    host = require_browser_demo_smoke_host(args.host)
    app = create_browser_demo_smoke_app(
        db_path=args.db,
        frontend_dist=args.frontend_dist,
    )

    import uvicorn

    uvicorn.run(app, host=host, port=args.port)
    return 0


def _synthetic_execution_summary() -> dict[str, object]:
    return {
        "mode": "explicit_multi_period_execution_summary",
        "period_count": 1,
        "processed_local_periods": [1],
        "processed_global_periods": [1],
        "total_vu_rule_applications": 0,
        "total_vn_insurance_rule_applications": 0,
        "total_vn_settlement_applications": 0,
        "total_vn_damage_settlement_applications": 0,
        "carryover_count": 0,
        "vu_carryover_count": 0,
        "vn_carryover_count": 0,
        "written_file_count": 0,
        "legacy_comparison_performed": False,
        "legacy_comparison_matches": None,
        "legacy_report_written_file_count": 0,
        "writes_performed": False,
        "execution_performed": True,
        "automatic_historical_rule_selection_performed": False,
        "simulation_performed": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Startet den isolierten PR66-Browser-Smoke mit injiziertem Fake-Adapter."
        )
    )
    parser.add_argument("--db", required=True, help="Frische SQLite-Datei fuer den Smoke.")
    parser.add_argument(
        "--frontend-dist",
        required=True,
        help="Pfad zum gebauten Workbench-Frontend.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8011)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
