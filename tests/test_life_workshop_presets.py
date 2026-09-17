import importlib

import pytest
from starlette.testclient import TestClient

from ims.accounting.life_period_chain import run_life_policy_period_chain
from ims.api.app import create_app
from ims.api.life_workshop_presets import (
    LIFE_WORKSHOP_PRESETS_VERSION,
    life_workshop_presets_payload,
)


def test_curated_cases_are_valid_deterministic_and_share_opening() -> None:
    payload = life_workshop_presets_payload()
    assert payload["schema_version"] == LIFE_WORKSHOP_PRESETS_VERSION
    assert [case["id"] for case in payload["cases"]] == ["death", "new_business", "capital"]
    baselines = []
    for case in payload["cases"]:
        baseline = run_life_policy_period_chain(case["baseline"]).to_dict()
        variant = run_life_policy_period_chain(case["variant"]).to_dict()
        assert baseline["valid"] and variant["valid"]
        assert baseline["requested_period_count"] == variant["requested_period_count"] == 2
        assert case["baseline"]["opening"] == case["variant"]["opening"]
        assert baseline["rows"][0]["opening_policies"] == variant["rows"][0]["opening_policies"]
        assert baseline["rows"] != variant["rows"]
        assert variant == run_life_policy_period_chain(case["variant"]).to_dict()
        assert variant["historical_full_equality_claim"] is False
        baselines.append(baseline)
    assert baselines[0] == baselines[1] == baselines[2]
    assert payload == life_workshop_presets_payload()

    variants = {
        case["id"]: run_life_policy_period_chain(case["variant"]).to_dict()["rows"]
        for case in payload["cases"]
    }
    assert variants["death"][0]["death_benefits_paid"] == "65.0000"
    assert variants["death"][0]["closing_active_policies"] == 1
    assert variants["new_business"][0]["premiums_collected"] == "20.0000"
    assert variants["new_business"][0]["closing_active_policies"] == 3
    assert variants["capital"][0]["closing_equity"] == "61.0000"


@pytest.mark.parametrize("fallback", [False, True])
def test_presets_endpoint_is_read_only_and_previewable(monkeypatch, tmp_path, fallback: bool) -> None:
    module = importlib.import_module("ims.api.app")
    if fallback:
        monkeypatch.setattr(module, "FastAPI", None)
    db_path = tmp_path / "unused.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))
    response = client.get("/api/accounting/life-period-chain/presets")
    assert response.status_code == 200
    assert response.json() == life_workshop_presets_payload()
    assert response.json()["historical_mapping_status"] == "unresolved"
    assert client.post("/api/accounting/life-period-chain/presets", json={}).status_code == 405
    for case in response.json()["cases"]:
        assert client.post("/api/accounting/life-period-chain/preview", json=case["variant"]).status_code == 200
    assert db_path.exists() is False
