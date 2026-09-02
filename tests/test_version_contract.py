import json
from pathlib import Path
import tomllib

from ims.api.app import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]
IMS_2X_ALPHA_VERSION = "2.0.0-alpha.1"


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
    assert pyproject["project"]["version"] == IMS_2X_ALPHA_VERSION
    assert package["version"] == IMS_2X_ALPHA_VERSION
    assert package_lock["version"] == IMS_2X_ALPHA_VERSION
    assert package_lock["packages"][""]["version"] == IMS_2X_ALPHA_VERSION
