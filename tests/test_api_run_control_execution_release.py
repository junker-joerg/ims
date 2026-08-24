from pathlib import Path

import pytest
from starlette.testclient import TestClient

from ims.api.app import create_app
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import (
    build_seeded_metadata_repository,
    connect_metadata_db,
)
from ims.api.run_control_execution_release import (
    build_default_execution_release_profiles,
    check_run_control_execution_release,
    parse_run_control_execution_release_payload,
)
from ims.api.run_control_preflight import preflight_run_control
from ims.api.run_control_queue import (
    WorkbenchRunControlQueueRepository,
    get_run_control_queue_entry,
)
from ims.api.run_control_requests import WorkbenchRunControlRequest


REPO_ROOT = Path(__file__).resolve().parent.parent
MIGRATION_DOC = REPO_ROOT / "docs" / "migration" / "run_control_execution_release_check.md"


def _release_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "ims.workbench.metadata.v1",
        "queue_id": "baseline-python-tests",
        "run_id": "baseline-python-tests",
        "scenario_id": "agrsich-reference-window",
        "release_profile_id": "vu14-calculated-diagnostic",
        "idempotency_key": "release-check-001",
        "expected_adapter_mode": "explicit_multi_period_fixture_adapter",
        "explicit_execution_release": True,
        "released_by": "local-reviewer",
        "released_at": "2026-08-24T12:00:00Z",
        "release_reason": "Kontrollierter lokaler Diagnoselauf",
    }
    payload.update(overrides)
    return payload


def _seed_validated_queue(db_path: Path, *, status: str = "validated") -> None:
    build_seeded_metadata_repository(db_path)
    connection = connect_metadata_db(db_path)
    try:
        queue = WorkbenchRunControlQueueRepository(connection)
        queue.enqueue(
            WorkbenchRunControlRequest(
                run_id="baseline-python-tests",
                scenario_id="agrsich-reference-window",
                requested_by="local-user",
                created_at="2026-08-24T11:55:00Z",
                metadata_db=str(db_path),
            ),
            status=status,
        )
    finally:
        connection.close()


def _check_release(db_path: Path, payload: dict[str, object]):
    request = parse_run_control_execution_release_payload(payload)
    queue_entry = get_run_control_queue_entry(request.queue_id, db_path=db_path).entry
    assert queue_entry is not None
    return check_run_control_execution_release(
        request,
        queue_entry=queue_entry,
        preflight=preflight_run_control(request.run_id, db_path),
        profiles=build_default_execution_release_profiles(REPO_ROOT),
        trusted_fixture_root=REPO_ROOT / "tests" / "fixtures",
    )


def test_execution_release_check_accepts_only_ready_local_profile(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    _seed_validated_queue(db_path)

    result = _check_release(db_path, _release_payload())
    payload = result.to_dict()

    assert payload["status"] == "ready"
    assert payload["release_ready"] is True
    assert payload["profile"]["profile_id"] == "vu14-calculated-diagnostic"
    assert payload["request"]["released_by"] == "local-reviewer"
    assert payload["issues"] == []
    assert all(check["passed"] is True for check in payload["checks"])
    assert payload["adapter_start_allowed"] is False
    assert payload["adapter_started"] is False
    assert payload["result_persisted"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    assert payload["automatic_historical_rule_selection_performed"] is False
    assert payload["historical_full_equality_claimed"] is False


@pytest.mark.parametrize("status", ["planned", "blocked", "result_persisted"])
def test_execution_release_check_requires_validated_queue(
    tmp_path: Path,
    status: str,
) -> None:
    db_path = tmp_path / "metadata.sqlite"
    _seed_validated_queue(db_path, status=status)

    result = _check_release(db_path, _release_payload())

    assert result.release_ready is False
    assert "queue status must be validated" in result.issues
    assert result.execution_performed is False


def test_execution_release_check_blocks_unknown_profile_and_carryover(tmp_path: Path) -> None:
    db_path = tmp_path / "metadata.sqlite"
    _seed_validated_queue(db_path)

    unknown = _check_release(
        db_path,
        _release_payload(release_profile_id="browser-selected-profile"),
    )
    carryover = _check_release(
        db_path,
        _release_payload(carry_forward_vu_state=True),
    )

    assert unknown.release_ready is False
    assert "release profile is not known locally" in unknown.issues
    assert carryover.release_ready is False
    assert "VU carryover is not allowed by the release profile" in carryover.issues


@pytest.mark.parametrize("forbidden_field", ["fixture_path", "output_dir", "browser_upload"])
def test_execution_release_payload_rejects_browser_controlled_paths(
    forbidden_field: str,
) -> None:
    with pytest.raises(MetadataImportError, match="rejected fields"):
        parse_run_control_execution_release_payload(
            _release_payload(**{forbidden_field: "C:/free/path"})
        )


def test_execution_release_payload_requires_explicit_release_and_audit_fields() -> None:
    with pytest.raises(MetadataImportError, match="must be true"):
        parse_run_control_execution_release_payload(
            _release_payload(explicit_execution_release=False)
        )

    payload = _release_payload()
    payload.pop("release_reason")
    with pytest.raises(MetadataImportError, match="release_reason"):
        parse_run_control_execution_release_payload(payload)

    with pytest.raises(MetadataImportError, match="released_at.*ending in Z"):
        parse_run_control_execution_release_payload(
            _release_payload(released_at="2026-08-24 12:00")
        )


def test_execution_release_check_endpoint_is_readonly(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "metadata.sqlite"
    _seed_validated_queue(db_path)
    monkeypatch.setenv("IMS_METADATA_DB", str(db_path))
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/run-control/adapter-release-check",
        json=_release_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["release_ready"] is True
    assert payload["adapter_start_allowed"] is False
    assert payload["adapter_started"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False
    queue_entry = get_run_control_queue_entry(
        "baseline-python-tests",
        db_path=db_path,
    ).entry
    assert queue_entry is not None
    assert queue_entry.status == "validated"
    assert queue_entry.execution_performed is False
    assert client.get("/api/run-control/adapter-start-contract").status_code == 200


def test_execution_release_check_endpoint_rejects_non_sqlite_source(tmp_path: Path) -> None:
    client = TestClient(create_app(frontend_dist=tmp_path))

    response = client.post(
        "/api/run-control/adapter-release-check",
        json=_release_payload(),
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["release_ready"] is False
    assert payload["adapter_started"] is False
    assert payload["writes_performed"] is False
    assert payload["execution_performed"] is False
    assert payload["simulation_performed"] is False


def test_execution_release_documentation_keeps_start_boundary_closed() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "Read-only Run-Control-Ausfuehrungsfreigabecheck" in doc
    assert "POST /api/run-control/adapter-release-check" in doc
    assert "`released_by`, `released_at` und `release_reason`" in doc
    assert "`vu14-calculated-diagnostic`" in doc
    assert "serverseitig" in doc and "Fixture" in doc
    assert "`adapter_start_allowed = false`" in doc
    assert "`adapter_started = false`" in doc
    assert "wiederholbar" in doc
    assert "POST /api/run-control/adapter-start" in doc
    assert "behauptet keine\nhistorische Vollgleichheit" in doc
    assert "keine Simulation gestartet" in doc
    assert "PR 63" in doc and "atomare Backend-Start" in doc
