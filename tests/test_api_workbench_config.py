import json

import pytest

from ims.api.workbench_config import WorkbenchConfigError, WorkbenchLocalConfig, load_workbench_config


def test_workbench_config_uses_defaults_without_file():
    config = load_workbench_config()

    assert config == WorkbenchLocalConfig(
        host="127.0.0.1",
        port=8000,
        frontend_dist="frontend/dist",
        metadata_db=None,
    )
    assert config.to_dict() == {
        "host": "127.0.0.1",
        "port": 8000,
        "frontend_dist": "frontend/dist",
        "metadata_db": None,
    }


def test_workbench_config_reads_explicit_json(tmp_path):
    config_path = tmp_path / "workbench.local.json"
    config_path.write_text(
        json.dumps(
            {
                "host": "127.0.0.1",
                "port": 8010,
                "frontend_dist": "custom/dist",
                "metadata_db": ".ims_workbench/metadata.sqlite",
            }
        ),
        encoding="utf-8",
    )

    config = load_workbench_config(config_path)

    assert config.host == "127.0.0.1"
    assert config.port == 8010
    assert config.frontend_dist == "custom/dist"
    assert config.metadata_db == ".ims_workbench/metadata.sqlite"


def test_workbench_config_rejects_invalid_port(tmp_path):
    config_path = tmp_path / "workbench.local.json"
    config_path.write_text(json.dumps({"port": 70000}), encoding="utf-8")

    with pytest.raises(WorkbenchConfigError, match="port"):
        load_workbench_config(config_path)


def test_workbench_config_rejects_missing_explicit_file(tmp_path):
    config_path = tmp_path / "missing.json"

    with pytest.raises(WorkbenchConfigError, match="does not exist"):
        load_workbench_config(config_path)

    assert config_path.exists() is False


def test_workbench_config_rejects_unknown_fields(tmp_path):
    config_path = tmp_path / "workbench.local.json"
    config_path.write_text(json.dumps({"unknown": True}), encoding="utf-8")

    with pytest.raises(WorkbenchConfigError, match="unknown"):
        load_workbench_config(config_path)
