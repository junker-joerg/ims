import csv
import importlib
from io import BytesIO, StringIO
import json

import pytest
from openpyxl import load_workbook
from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.seminar import MAX_INPUT_BYTES
from ims.accounting.management_case import digest


@pytest.mark.parametrize("fallback", [False, True])
def test_modern_hundred_and_complete_sources_export_roundtrip_demo_are_pure(monkeypatch, tmp_path, fallback):
    module = importlib.import_module("ims.api.app")
    if fallback: monkeypatch.setattr(module, "FastAPI", None)
    db = tmp_path / "not-created.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db))
    client = TestClient(create_app(frontend_dist=tmp_path))
    base = "/api/seminar"
    assert client.get(base + "/contract").json()["regulatory_metrics_enabled"] is False
    preset = client.post(base + "/workshop-case", json={"case_id": "price", "period_count": 100}).json()
    source = preset["source_input"]
    response = client.post(base + "/calculate", json=source)
    assert response.status_code == 200
    result, etag = response.json(), response.headers["etag"]
    assert etag == '"' + result["content_digest"] + '"'
    for extension in ("json", "csv", "xlsx"):
        exported = client.post(base + f"/export.{extension}", json=source, headers={"If-Match": etag})
        assert exported.status_code == 200 and exported.headers["etag"] == etag
        if extension == "json": assert exported.json() == result
        elif extension == "csv":
            rows = list(csv.DictReader(StringIO(exported.content.decode("utf-8-sig"))))
            assert len(rows) == 1000 and rows[-1]["closing_equity"] == "87325.7633"
        else:
            book = load_workbook(BytesIO(exported.content), data_only=False)
            assert book["Entscheidungskette"].max_row == 801
            chunks = [row[1].value for row in book["Herkunft"] if row[0].value == "source_input_json_chunk"]
            assert json.loads("".join(chunks)) == source
            assert book["Herkunft"]["B1"].value == result["content_digest"]
    assert client.post(base + "/export.json", json=source).status_code == 412
    export_input = {"title": preset["title"], "sources": {"modern": source, **preset["companion_sources"]}}
    assert client.post(base + "/bundle.json", json=export_input).status_code == 412
    exported = client.post(base + "/bundle.json", json=export_input, headers={"If-Match": etag})
    assert exported.status_code == 200
    bundle = exported.json()
    imported = client.post(base + "/import-bundle", json=bundle)
    assert imported.status_code == 200
    demo = imported.json()
    assert demo["demo_mode"] == "read_only_fresh_calculation"
    assert demo["results"]["modern"] == result
    assert demo["results"]["guided"]["candidate_count"] == 107
    assert demo["results"]["ict"]["period_count"] == 100
    assert demo["writes_performed"] is False and not db.exists()
    assert bundle["capital_assumptions"]["reference_date"] == "2026-10-01"
    assert bundle["capital_assumptions"]["exposures"]["motor_assets"] == {"amount": "1000", "rate": "0.1"}
    # Simulate JavaScript JSON.parse/stringify: 1.0 becomes 1, strings stay exact.
    transported = json.loads(json.dumps(bundle), parse_float=lambda text: int(float(text)) if float(text).is_integer() else float(text))
    assert digest(transported) == digest(bundle)
    # A self-consistent new hash must not silently change the curated contract.
    changed = json.loads(json.dumps(bundle))
    changed["capital_assumptions"]["operational_loss"] = "999"
    changed["bundle_digest"] = digest({k: v for k, v in changed.items() if k != "bundle_digest"})
    rejected = client.post(base + "/import-bundle", json=changed)
    assert rejected.status_code == 422 and rejected.json()["results"] == {} and not db.exists()
    bundle["sources"]["guided"]["period_contexts"][-1]["period"] = 99
    bundle["bundle_digest"] = digest({k: v for k, v in bundle.items() if k != "bundle_digest"})
    bad = client.post(base + "/import-bundle", json=bundle)
    assert bad.status_code == 422 and bad.json()["results"] == {} and not db.exists()
    for path in ("workshop-case", "calculate", "import-bundle", "bundle.json"):
        for content in (b"{", b" " * (MAX_INPUT_BYTES + 1)):
            invalid = client.post(base + "/" + path, content=content)
            assert invalid.status_code == 422 and invalid.json()["content_digest"] is None


def test_late_corrupted_bundle_is_recalculated_and_never_trusted(tmp_path):
    client = TestClient(create_app(frontend_dist=tmp_path))
    invalid = client.post("/api/seminar/workshop-case", json={"case_id": [], "period_count": 100})
    assert invalid.status_code == 422


def test_curated_sources_and_offline_help_are_available_without_writes(monkeypatch, tmp_path):
    db = tmp_path / "not-created.sqlite"
    monkeypatch.setenv("IMS_METADATA_DB", str(db))
    client = TestClient(create_app(frontend_dist=tmp_path))
    for case_id in ("price", "inflation", "capital"):
        response = client.get(f"/api/seminar/bundles/{case_id}.json")
        assert response.status_code == 200
        bundle = response.json()
        assert bundle["bundle_digest"] == digest({k: v for k, v in bundle.items() if k != "bundle_digest"})
        assert len(bundle["sources"]["modern"]["market_periods"]) == 100
        assert len(bundle["sources"]["guided"]["period_contexts"]) == 100
        assert bundle["capital_assumptions"]["exposures"]["motor_assets"]["amount"] == ("5000" if case_id == "capital" else "1000")
    assert client.get("/api/seminar/bundles/unknown.json").status_code == 404
    help_page = client.get("/api/seminar/handbook/seminar_ap3.html")
    assert help_page.status_code == 200 and "Managementseminar mit AP3" in help_page.text
    assert "SCR, MCR" in help_page.text
    assert not db.exists()
