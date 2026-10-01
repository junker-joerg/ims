import json
from pathlib import Path
import tomllib
import importlib.util

import pytest

from ims.api.app import APP_VERSION
from ims.release import VERSION, WINDOWS_FILE_VERSION, windows_file_version


ROOT = Path(__file__).resolve().parents[1]
IMS_2X_ALPHA_VERSION = VERSION


def test_ims_2x_version_is_consistent_across_backend_and_frontend():
    pyproject = tomllib.loads(
        (ROOT / "python_port" / "pyproject.toml").read_text(encoding="utf-8")
    )
    package = json.loads(
        (ROOT / "frontend" / "package.json").read_text(encoding="utf-8")
    )
    package_lock = json.loads(
        (ROOT / "frontend" / "package-lock.json").read_text(encoding="utf-8")
    )

    assert APP_VERSION == IMS_2X_ALPHA_VERSION
    assert VERSION == IMS_2X_ALPHA_VERSION
    assert WINDOWS_FILE_VERSION == windows_file_version(VERSION)
    assert pyproject["project"]["version"] == IMS_2X_ALPHA_VERSION
    assert package["version"] == IMS_2X_ALPHA_VERSION
    assert package_lock["version"] == IMS_2X_ALPHA_VERSION
    assert package_lock["packages"][""]["version"] == IMS_2X_ALPHA_VERSION


def release_tool():
    spec = importlib.util.spec_from_file_location("release_metadata", ROOT / "scripts/installer/release_metadata.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def release_fixture(tmp_path):
    for name in ("python_port/ims/release.py", "python_port/pyproject.toml", "frontend/package.json", "frontend/package-lock.json"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    return tmp_path


def test_release_advance_updates_all_mirrors_and_rejects_reuse(tmp_path):
    root = release_fixture(tmp_path)
    tool = release_tool()
    major, minor, patch, _ = map(int, WINDOWS_FILE_VERSION.split("."))
    requested_version = f"{major}.{minor}.{patch + 1}-alpha.0"
    tool.advance_release(root, VERSION, requested_version)
    tool.check_release(root, requested_version)
    assert f'VERSION = "{requested_version}"' in (root / "python_port/ims/release.py").read_text()
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    for requested in (requested_version, VERSION, "bad", "2.0.0-alpha.65535"):
        with pytest.raises(ValueError):
            tool.advance_release(root, requested_version, requested)
        assert all(p.read_bytes() == content for p, content in before.items())


def test_release_check_detects_stale_frontend_before_build(tmp_path):
    root = release_fixture(tmp_path)
    package = root / "frontend/package.json"
    value = json.loads(package.read_text())
    value["version"] = "2.0.0-alpha.1"
    package.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="Release versions differ"):
        release_tool().check_release(root, VERSION)


def test_windows_release_order_and_limits():
    assert windows_file_version("2.0.0-alpha.4") == "2.0.0.4"
    assert windows_file_version("2.0.0") == "2.0.0.65535"
    for invalid in ("2.0-alpha.3", "02.0.0-alpha.3", "2.0.0-alpha.65536", "65536.0.0-alpha.3"):
        with pytest.raises(ValueError):
            windows_file_version(invalid)
