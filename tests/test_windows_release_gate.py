from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GATE_SCRIPT = REPO_ROOT / "scripts" / "workbench" / "test-release-gate.ps1"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "windows-release-gate.yml"
PLAN = REPO_ROOT / "docs" / "plans" / "windows_release_gate_plan.md"


def test_windows_release_gate_workflow_uses_locked_windows_toolchain() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert WORKFLOW.is_file()
    assert "runs-on: windows-latest" in workflow
    assert 'python-version: "3.12"' in workflow
    assert 'node-version: "22"' in workflow
    assert 'python -m pip install -e ".\\python_port[dev]"' in workflow
    assert "npm.cmd ci --prefix .\\frontend" in workflow
    assert ".\\scripts\\workbench\\test-release-gate.ps1" in workflow
    assert "contents: read" in workflow
    assert "timeout-minutes: 30" in workflow


def test_windows_release_gate_runs_existing_checks_in_order() -> None:
    script = GATE_SCRIPT.read_text(encoding="utf-8")
    expected_steps = [
        "python -m pytest -q",
        "npm.cmd run build --prefix .\\frontend",
        "python -m ims.api.production_release_corpus_report",
        "python -m ims.api.workbench_bundle_build",
        "python -m ims.api.workbench_bundle_smoke",
        "python -m ims.api.workbench_portable_staging",
        "python -m ims.api.workbench_portable_staging_smoke",
        "python -m ims.api.workbench_portable_readiness",
        "python -m ims.api.workbench_release_smoke",
        'Join-Path $portableRoot "check-workbench.cmd"',
    ]

    assert GATE_SCRIPT.is_file()
    positions = [script.index(step) for step in expected_steps]
    assert positions == sorted(positions)
    assert "--basetemp $pytestTempRoot" in script
    assert '-o "cache_dir=$pytestCacheRoot"' in script


def test_windows_release_gate_freezes_conservative_report_boundary() -> None:
    script = GATE_SCRIPT.read_text(encoding="utf-8")

    assert '$report.status -ne "blocked"' in script
    assert '$report.release_decision -ne "blocked_calculated_core_validation"' in script
    assert "$report.reference_count -ne 19" in script
    assert "$report.covered_periods -ne 6300" in script
    assert "$report.missing_calculated_export_count -ne 15" in script
    assert "$report.production_release_approved -ne $false" in script
    assert "$report.simulation_performed -ne $false" in script
    assert "$report.historical_full_equality_claimed -ne $false" in script
    assert "production_release_approved = $false" in script


def test_windows_release_gate_keeps_runtime_and_cleanup_boundaries() -> None:
    script = GATE_SCRIPT.read_text(encoding="utf-8")

    assert "if ([string]::IsNullOrWhiteSpace($RepoRoot))" in script
    assert 'Join-Path $PSScriptRoot "..\\.."' in script
    assert '"ims-pr70-" + [guid]::NewGuid()' in script
    assert "work root must be empty" in script
    assert 'StartsWith("ims-pr70-"' in script
    assert '$pytestTempRoot = Join-Path $resolvedWorkRoot "pytest-temp"' in script
    assert '$pytestCacheRoot = Join-Path $resolvedWorkRoot "pytest-cache"' in script
    assert "Remove-Item -LiteralPath $resolvedPath -Recurse -Force" in script
    assert "ims.api.controlled_execution_adapter" not in script
    assert "ims.api.run_control_browser_demo_smoke" not in script
    assert "ims.engine.simulation" not in script
    assert "uvicorn" not in script


def test_windows_release_gate_plan_scopes_ci_without_fachlogik() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert PLAN.is_file()
    assert "Windows-Freigabegate fuer PR 70" in plan
    assert "GitHub Actions auf `windows-latest`" in plan
    assert "Python 3.12" in plan
    assert "Node.js 22" in plan
    assert "15 fehlende berechnete Exporte" in plan
    assert "kein Adapter-, Runner- oder Queue-Start" in plan
    assert "keine Simulation als Produktlauf" in plan
    assert "keine neue Fachlogik" in plan
    assert "keine historische Vollgleichheitsbehauptung" in plan
