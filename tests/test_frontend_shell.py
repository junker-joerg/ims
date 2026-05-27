import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"


def test_frontend_workbench_entrypoints_are_declared():
    package_json = json.loads((FRONTEND_DIR / "package.json").read_text(encoding="utf-8"))

    assert package_json["scripts"]["build"] == "tsc -b && vite build --configLoader runner"
    assert package_json["dependencies"]["react"]
    assert package_json["dependencies"]["react-dom"]
    assert package_json["devDependencies"]["vite"]


def test_frontend_lockfile_is_committed_for_repeatable_builds():
    lockfile = json.loads((FRONTEND_DIR / "package-lock.json").read_text(encoding="utf-8"))

    assert lockfile["name"] == "ims-workbench-frontend"
    assert lockfile["lockfileVersion"] == 3


def test_frontend_shell_sources_exist():
    assert (FRONTEND_DIR / "index.html").is_file()
    assert (FRONTEND_DIR / "src" / "main.tsx").is_file()
    assert (FRONTEND_DIR / "src" / "styles.css").is_file()


def test_frontend_shell_declares_detail_metadata_contract():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "/api/scenarios/${encodeURIComponent(selectedScenarioId)}" in source
    assert "/api/runs/${encodeURIComponent(selectedRunId)}" in source
    assert "Metadaten-Detail" in source
    assert "Detaildaten nicht erreichbar" in source


def test_frontend_shell_declares_readonly_import_preview():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Importvorschau" in source
    assert "schema_version" in source
    assert "execution_enabled" in source
    assert "Browser schreibt keine Metadaten" in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_metadata_source_status():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "/api/metadata/source" in source
    assert "Metadatenquelle" in source
    assert "storage_kind" in source
    assert "writes_enabled" in source


def test_frontend_shell_declares_readonly_operations_diagnosis():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Betriebsdiagnose" in source
    assert "/api/health" in source
    assert "/api/version" in source
    assert "/api/metadata/source" in source
    assert "/api/metadata/capabilities" in source
    assert "lokal per CLI" in source
    assert 'type="file"' not in source


def test_frontend_shell_declares_readonly_run_overview():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "const selectRun = (run: RunMetadata)" in source
    assert "setSelectedRunId(run.id)" in source
    assert "setSelectedScenarioId(run.scenario_id)" in source
    assert "Run-Uebersicht" in source
    assert "run-overview-row" in source
    assert "period_window" in source
    assert "scenario_id" in source
    assert "execution_enabled" in source
    assert "gesperrt" in source
    assert "startRun" not in source


def test_frontend_shell_declares_readonly_scenario_overview():
    source = (FRONTEND_DIR / "src" / "main.tsx").read_text(encoding="utf-8")

    assert "Szenario-Uebersicht" in source
    assert "scenario-overview-row" in source
    assert "domain_scope" in source
    assert "updated_at" in source
    assert "validation.scope" in source
    assert "executionLabel" in source
    assert "startScenario" not in source
