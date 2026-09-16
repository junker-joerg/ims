from copy import deepcopy
from pathlib import Path

from fastapi.testclient import TestClient

from ims.api.app import create_app
from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe_start import (
    get_strategy_execution_five_period_effect_probe_result,
)
from ims.api.strategy_execution_period_chain_store import (
    STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
    persist_strategy_execution_period_chain,
)
from tests.test_strategy_execution_period_chain_extended_probe import _input


def prepare_hundred_browser_smoke(root: Path) -> tuple[Path, dict, list[dict]]:
    """Fresh local 5+100 evidence; used by API and manual browser acceptance."""

    root.mkdir(parents=True, exist_ok=True)
    db_path, payload = _input(root, 100)
    baseline_id = payload["five_period_baseline"]["chain_id"]
    baseline = get_strategy_execution_five_period_effect_probe_result(
        baseline_id, db_path=db_path
    ).record
    assert baseline is not None
    five_input = baseline.request_payload["effect_probe_request"]["period_chain_input"]
    five = build_strategy_execution_period_chain(five_input, db_path=db_path).chain
    assert five is not None and five.chain_id == baseline_id
    _store(db_path, five_input, five, "2026-09-16T08:00:00Z")

    first_input = payload["period_chain_input"]
    first = build_strategy_execution_period_chain(first_input, db_path=db_path).chain
    assert first is not None
    _store(db_path, first_input, first, "2026-09-16T08:01:00Z")

    second_input = deepcopy(first_input)
    second_input["transitions"][5]["carry_forward_vu_state"] = False
    second = build_strategy_execution_period_chain(second_input, db_path=db_path).chain
    assert second is not None and second.chain_id != first.chain_id
    _store(db_path, second_input, second, "2026-09-16T08:02:00Z")
    return db_path, payload, [first.to_dict(), second.to_dict()]


def _store(db_path: Path, value: dict, chain, timestamp: str) -> None:
    stored = persist_strategy_execution_period_chain(
        {
            "schema_version": STRATEGY_EXECUTION_PERIOD_CHAIN_STORE_REQUEST_VERSION,
            "period_chain_input": value,
            "expected_chain_id": chain.chain_id,
            "expected_content_digest": chain.content_digest,
            "stored_at": timestamp,
            "explicit_storage_release": True,
        },
        db_path=db_path,
    )
    assert stored.record is not None


def test_hundred_browser_sources_allow_only_verified_chains_and_prefix(tmp_path, monkeypatch):
    db_path, payload, chains = prepare_hundred_browser_smoke(tmp_path / "smoke")
    before = db_path.read_bytes()
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))

    overview = client.get("/api/strategies/execution-period-chains")
    assert overview.status_code == 200
    entries = overview.json()["period_chains"]
    assert len(entries) == 4
    assert sorted(item["period_count"] for item in entries) == [2, 5, 100, 100]
    hundred = [item for item in entries if item["period_count"] == 100]
    assert len(hundred) == 2
    assert all(item["digest_verified"] for item in hundred)
    five = next(item for item in entries if item["period_count"] == 5)
    baseline = client.get(
        "/api/run-control/strategy-period-chain-five-period-effect-probe-result/"
        + five["chain_id"]
    )
    assert baseline.status_code == 200
    assert baseline.json()["result_available"] is True
    for chain in chains:
        detail = client.get(
            "/api/strategies/execution-period-chains/" + chain["identity"]["chain_id"]
        )
        assert detail.status_code == 200
        assert detail.json()["record"]["period_chain_input"]["max_periods"] == 100
    assert payload["five_period_baseline"]["chain_id"] == five["chain_id"]
    assert db_path.read_bytes() == before
