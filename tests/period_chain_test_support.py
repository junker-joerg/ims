from copy import deepcopy
import json
from pathlib import Path
import sqlite3

from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_SCHEMA,
)
from ims.strategies import (
    StrategyExecutionScenarioProfileDefinition,
    build_strategy_execution_candidate,
)


ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_INPUT_FIXTURE = (
    ROOT / "tests" / "fixtures" / "strategy_execution_candidate_input_v1.json"
)
CHAIN_INPUT_FIXTURE = (
    ROOT / "tests" / "fixtures" / "strategy_execution_period_chain_input_v1.json"
)
PROFILE_FIXTURE = (
    ROOT
    / "python_port"
    / "ims"
    / "strategies"
    / "profiles"
    / "strategy_execution_candidate_profile_v1.json"
)


def candidate_input(period: int) -> dict[str, object]:
    value = json.loads(CANDIDATE_INPUT_FIXTURE.read_text(encoding="utf-8"))
    value["snapshot_context"]["period"] = period
    if period == 1:
        value["snapshot_context"]["entries"][1]["values"][
            "initial_decisions"
        ] = [
            {"sector_index": 0, "insured": False, "insurer_id": None},
            {"sector_index": 1, "insured": False, "insurer_id": None},
        ]
    value["vu_state_provenance"]["period"] = period
    value["scenario_profile_reference"]["period"] = period
    value["vn_process_input"]["period"] = period
    return value


def profile(
    period: int,
    *,
    run_index: int,
    max_periods: int,
) -> dict[str, object]:
    value = json.loads(PROFILE_FIXTURE.read_text(encoding="utf-8"))
    value["period"] = period
    value["context"]["period"] = period
    value["context"]["run_index"] = run_index
    value["context"]["max_periods"] = max_periods
    value["context"]["rng_seed"] = 1300 + period
    return value


def persist_chain_candidates(
    db_path: Path,
    profile_root: Path,
    *,
    run_index: int = 7,
    max_periods: int = 2,
    run_indices: dict[int, int] | None = None,
) -> list[dict[str, object]]:
    references: list[dict[str, object]] = []
    with sqlite3.connect(db_path) as connection:
        connection.execute(STRATEGY_EXECUTION_CANDIDATE_STORE_SCHEMA)
        for period in range(1, max_periods + 1):
            candidate_run_index = (run_indices or {}).get(period, run_index)
            profile_path = profile_root / f"profile-{period}.json"
            profile_path.write_text(
                json.dumps(
                    profile(
                        period,
                        run_index=candidate_run_index,
                        max_periods=max_periods,
                    ),
                    ensure_ascii=True,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            profile_id = "synthetic-joint-single-period-v1"
            build = build_strategy_execution_candidate(
                candidate_input(period),
                profiles={
                    profile_id: StrategyExecutionScenarioProfileDefinition(
                        profile_id=profile_id,
                        path=profile_path,
                    )
                },
                trusted_profile_root=profile_root,
            )
            assert build.candidate is not None, build.issues
            candidate = build.candidate
            connection.execute(
                """
                INSERT INTO strategy_execution_candidates (
                    candidate_id,
                    candidate_schema_version,
                    draft_id,
                    period,
                    profile_id,
                    profile_content_digest,
                    content_digest,
                    stored_at,
                    candidate_payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.candidate_id,
                    candidate.schema_version,
                    candidate.draft_id,
                    candidate.period,
                    candidate.profile_id,
                    candidate.profile_content_digest,
                    candidate.content_digest,
                    f"2026-09-11T08:{period:02d}:00Z",
                    json.dumps(
                        candidate.to_dict(),
                        ensure_ascii=True,
                        allow_nan=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                ),
            )
            references.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "content_digest": candidate.content_digest,
                    "period": period,
                }
            )
    return references


def chain_input(
    references: list[dict[str, object]],
    *,
    run_index: int = 7,
    max_periods: int = 2,
) -> dict[str, object]:
    value = json.loads(CHAIN_INPUT_FIXTURE.read_text(encoding="utf-8"))
    value["run_index"] = run_index
    value["max_periods"] = max_periods
    value["period_candidates"] = deepcopy(references)
    value["transitions"] = [
        {
            "from_period": period,
            "to_period": period + 1,
            "carry_forward_vu_state": True,
            "carry_forward_vn_state": True,
        }
        for period in range(1, max_periods)
    ]
    return value
