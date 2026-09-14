from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Sequence

from ims.api.app import create_app
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
    persist_strategy_execution_candidate,
)
from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
)
from ims.api.strategy_execution_period_chain_effect_probe import (
    StrategyExecutionPeriodChainEffectProbeRunner,
)
from ims.api.strategy_execution_period_chain_store import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
    persist_strategy_execution_period_chain,
)
from ims.strategies.execution_candidate_build import (
    StrategyExecutionScenarioProfileDefinition,
    build_strategy_execution_candidate,
)


STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_HOSTS = frozenset(
    {"127.0.0.1", "localhost", "::1"}
)
_ROOT = Path(__file__).resolve().parents[3]
STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_CANDIDATE_FIXTURE = (
    _ROOT / "tests" / "fixtures" / "strategy_execution_candidate_input_v1.json"
)
STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_CHAIN_FIXTURE = (
    _ROOT
    / "tests"
    / "fixtures"
    / "strategy_execution_period_chain_input_v1.json"
)
STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_PROFILE_FIXTURE = (
    _ROOT
    / "python_port"
    / "ims"
    / "strategies"
    / "profiles"
    / "strategy_execution_candidate_profile_v1.json"
)
_SMOKE_RUN_INDEX = 7
_SMOKE_MAX_PERIODS = 2


def create_strategy_period_chain_browser_smoke_app(
    *,
    db_path: str | Path,
    frontend_dist: str | Path,
    period_chain_effect_probe_runner: (
        StrategyExecutionPeriodChainEffectProbeRunner | None
    ) = None,
) -> Any:
    """Baut eine frische lokale PR141-Abnahmeinstanz fuer Periode 1 und 2."""

    resolved_db_path = Path(db_path).expanduser().resolve()
    resolved_frontend_dist = Path(frontend_dist).expanduser().resolve()
    profile_root = resolved_db_path.parent / (
        f"{resolved_db_path.stem}-strategy-profiles"
    )
    if resolved_db_path.exists():
        raise MetadataImportError(
            "strategy period chain browser smoke requires a fresh metadata "
            f"database: {resolved_db_path}"
        )
    if profile_root.exists():
        raise MetadataImportError(
            "strategy period chain browser smoke requires a fresh profile "
            f"directory: {profile_root}"
        )
    if not (resolved_frontend_dist / "index.html").is_file():
        raise MetadataImportError(
            "strategy period chain browser smoke requires a built frontend: "
            f"{resolved_frontend_dist}"
        )

    candidate_fixture = _load_fixture(
        STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_CANDIDATE_FIXTURE,
        label="candidate",
    )
    chain_fixture = _load_fixture(
        STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_CHAIN_FIXTURE,
        label="period chain",
    )
    profile_fixture = _load_fixture(
        STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_PROFILE_FIXTURE,
        label="scenario profile",
    )

    resolved_db_path.parent.mkdir(parents=True, exist_ok=True)
    profile_root.mkdir()
    repository = build_seeded_metadata_repository(resolved_db_path)
    references: list[dict[str, object]] = []

    for period in range(1, _SMOKE_MAX_PERIODS + 1):
        candidate_input = _candidate_input_for_period(candidate_fixture, period)
        profile_value = _profile_for_period(profile_fixture, period)
        profile_path = profile_root / f"period-{period}.json"
        profile_path.write_text(
            json.dumps(
                profile_value,
                ensure_ascii=True,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        profile_id = str(profile_value["profile_id"])
        profiles = {
            profile_id: StrategyExecutionScenarioProfileDefinition(
                profile_id=profile_id,
                path=profile_path,
            )
        }
        build = build_strategy_execution_candidate(
            candidate_input,
            profiles=profiles,
            trusted_profile_root=profile_root,
        )
        if not build.build_complete or build.candidate is None:
            issue_codes = ", ".join(issue.code for issue in build.issues)
            raise MetadataImportError(
                "strategy period chain browser smoke candidate cannot be built"
                + (f": {issue_codes}" if issue_codes else "")
            )
        candidate = build.candidate
        stored = persist_strategy_execution_candidate(
            {
                "schema_version": (
                    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION
                ),
                "candidate_input": candidate_input,
                "expected_candidate_id": candidate.candidate_id,
                "expected_content_digest": candidate.content_digest,
                "stored_at": f"2026-09-14T09:0{period}:00+02:00",
                "explicit_storage_release": True,
            },
            db_path=resolved_db_path,
            profiles=profiles,
            trusted_profile_root=profile_root,
        )
        references.append(
            {
                "candidate_id": stored.record.candidate_id,
                "content_digest": stored.record.content_digest,
                "period": period,
            }
        )

    chain_input = deepcopy(chain_fixture)
    chain_input["run_index"] = _SMOKE_RUN_INDEX
    chain_input["max_periods"] = _SMOKE_MAX_PERIODS
    chain_input["period_candidates"] = references
    chain_input["transitions"] = [
        {
            "from_period": 1,
            "to_period": 2,
            "carry_forward_vu_state": True,
            "carry_forward_vn_state": True,
        }
    ]
    chain_build = build_strategy_execution_period_chain(
        chain_input,
        db_path=resolved_db_path,
    )
    if not chain_build.build_complete or chain_build.chain is None:
        issue_codes = ", ".join(issue.code for issue in chain_build.issues)
        raise MetadataImportError(
            "strategy period chain browser smoke chain cannot be built"
            + (f": {issue_codes}" if issue_codes else "")
        )
    chain = chain_build.chain
    persist_strategy_execution_period_chain(
        {
            "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
            "period_chain_input": chain_input,
            "expected_chain_id": chain.chain_id,
            "expected_content_digest": chain.content_digest,
            "stored_at": "2026-09-14T09:03:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=resolved_db_path,
    )

    return create_app(
        frontend_dist=resolved_frontend_dist,
        metadata_repository=repository,
        period_chain_effect_probe_runner=period_chain_effect_probe_runner,
    )


def require_strategy_period_chain_browser_smoke_host(host: str) -> str:
    normalized_host = host.strip().lower()
    if normalized_host not in STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_HOSTS:
        raise MetadataImportError(
            "strategy period chain browser smoke server must use a loopback host: "
            + ", ".join(sorted(STRATEGY_PERIOD_CHAIN_BROWSER_SMOKE_HOSTS))
        )
    return normalized_host


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    host = require_strategy_period_chain_browser_smoke_host(args.host)
    app = create_strategy_period_chain_browser_smoke_app(
        db_path=args.db,
        frontend_dist=args.frontend_dist,
    )

    import uvicorn

    uvicorn.run(app, host=host, port=args.port)
    return 0


def _candidate_input_for_period(
    fixture: dict[str, object],
    period: int,
) -> dict[str, object]:
    value = deepcopy(fixture)
    snapshot_context = value["snapshot_context"]
    assert isinstance(snapshot_context, dict)
    snapshot_context["period"] = period
    entries = snapshot_context["entries"]
    assert isinstance(entries, list)
    vn_entry = entries[1]
    assert isinstance(vn_entry, dict)
    vn_values = vn_entry["values"]
    assert isinstance(vn_values, dict)
    if period == 1:
        vn_values["initial_decisions"] = [
            {"sector_index": 0, "insured": False, "insurer_id": None},
            {"sector_index": 1, "insured": False, "insurer_id": None},
        ]
    provenance = value["vu_state_provenance"]
    reference = value["scenario_profile_reference"]
    process_input = value["vn_process_input"]
    assert isinstance(provenance, dict)
    assert isinstance(reference, dict)
    assert isinstance(process_input, dict)
    provenance["period"] = period
    reference["period"] = period
    process_input["period"] = period
    return value


def _profile_for_period(
    fixture: dict[str, object],
    period: int,
) -> dict[str, object]:
    value = deepcopy(fixture)
    value["period"] = period
    context = value["context"]
    assert isinstance(context, dict)
    context["period"] = period
    context["run_index"] = _SMOKE_RUN_INDEX
    context["max_periods"] = _SMOKE_MAX_PERIODS
    context["rng_seed"] = 1400 + period
    return value


def _load_fixture(path: Path, *, label: str) -> dict[str, object]:
    if not path.is_file():
        raise MetadataImportError(
            f"strategy period chain browser smoke {label} fixture is missing: {path}"
        )
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MetadataImportError(
            "strategy period chain browser smoke "
            f"{label} fixture is unreadable: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise MetadataImportError(
            f"strategy period chain browser smoke {label} fixture must be an object"
        )
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Startet den isolierten PR141-Browser-Smoke fuer die "
            "Zwei-Perioden-Wirkungsprobe."
        )
    )
    parser.add_argument("--db", required=True, help="Frische SQLite-Datei.")
    parser.add_argument(
        "--frontend-dist",
        required=True,
        help="Pfad zum gebauten Workbench-Frontend.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8013)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
