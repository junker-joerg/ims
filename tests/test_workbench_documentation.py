from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
WORKBENCH_DOC = REPO_ROOT / "docs" / "migration" / "workbench_shell.md"


def test_readme_documents_local_workbench_start_commands():
    readme = README.read_text(encoding="utf-8")

    assert "python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist" in readme
    assert "python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000" in readme
    assert "npm.cmd run build" in readme
    assert "keine HTTP-/UI-Schreibpfade" in readme


def test_workbench_doc_groups_local_cli_boundaries():
    doc = WORKBENCH_DOC.read_text(encoding="utf-8")

    assert "## Lokale CLI-Grenzen" in doc
    assert "python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist" in doc
    assert "python -m ims.api.metadata_import_cli check .\\metadata_import.json" in doc
    assert "python -m ims.api.metadata_import_cli preview .\\metadata_import.json" in doc
    assert "python -m ims.api.metadata_import_cli snapshot --db .\\.ims_workbench\\metadata.sqlite" in doc
    assert "python -m ims.api.metadata_import_cli import .\\metadata_import.json --db .\\.ims_workbench\\metadata.sqlite" in doc


def test_workbench_doc_keeps_modernization_boundaries_conservative():
    doc = WORKBENCH_DOC.read_text(encoding="utf-8")

    assert "uvicorn" in doc
    assert "immutable=1" not in doc
    assert "Vollgleichheit" in doc
    assert "Keines dieser Kommandos startet eine Simulation" in doc
