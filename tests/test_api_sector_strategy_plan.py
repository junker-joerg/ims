import importlib
import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.strategies.sector_strategy_plan import sector_strategy_plan_contract_payload


FIXTURE = Path(__file__).parent / "fixtures" / "sector_strategy_plan_v1.json"


@pytest.mark.parametrize("starlette_fallback", [False, True])
def test_sector_plan_api_validates_without_storage_or_execution(
    monkeypatch, tmp_path, starlette_fallback: bool
) -> None:
    app_module = importlib.import_module("ims.api.app")
    if starlette_fallback:
        monkeypatch.setattr(app_module, "FastAPI", None)
    db_path = tmp_path / "unused.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    runner = importlib.import_module("ims.engine.explicit_period_runner")

    def reject_execution(*args: object, **kwargs: object) -> None:
        raise AssertionError("Der Sektorplan darf keinen Runner starten")

    monkeypatch.setattr(runner, "run_loaded_explicit_period", reject_execution)
    client = TestClient(create_app(frontend_dist=tmp_path))
    contract_endpoint = "/api/strategies/sector-plan-contract"
    validation_endpoint = "/api/strategies/sector-plan-validation"
    plan = json.loads(FIXTURE.read_text(encoding="utf-8"))

    assert client.get(contract_endpoint).json() == sector_strategy_plan_contract_payload()
    assert client.post(validation_endpoint, json=plan).json()["valid"] is True
    plan["assignments"][0]["sector_id"] = "life"
    invalid = client.post(validation_endpoint, json=plan)
    assert invalid.status_code == 200
    assert invalid.json()["valid"] is False
    assert invalid.json()["accepted_assignment_count"] == 0
    malformed = client.post(
        validation_endpoint, content="{", headers={"content-type": "application/json"}
    )
    assert malformed.status_code == 400
    assert malformed.json()["issues"][0]["code"] == "invalid_json"
    assert client.get(validation_endpoint).status_code == 405
    assert client.post(contract_endpoint, json={}).status_code == 405
    assert db_path.exists() is False
