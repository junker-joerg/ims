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
