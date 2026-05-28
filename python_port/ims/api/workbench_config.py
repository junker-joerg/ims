from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_WORKBENCH_HOST = "127.0.0.1"
DEFAULT_WORKBENCH_PORT = 8000
DEFAULT_FRONTEND_DIST = "frontend/dist"
DEFAULT_METADATA_DB: str | None = None
WORKBENCH_CONFIG_FIELDS = frozenset({"host", "port", "frontend_dist", "metadata_db"})


class WorkbenchConfigError(ValueError):
    pass


@dataclass(frozen=True)
class WorkbenchLocalConfig:
    host: str = DEFAULT_WORKBENCH_HOST
    port: int = DEFAULT_WORKBENCH_PORT
    frontend_dist: str = DEFAULT_FRONTEND_DIST
    metadata_db: str | None = DEFAULT_METADATA_DB

    def to_dict(self) -> dict[str, object]:
        return {
            "host": self.host,
            "port": self.port,
            "frontend_dist": self.frontend_dist,
            "metadata_db": self.metadata_db,
        }


def load_workbench_config(path: Path | str | None = None) -> WorkbenchLocalConfig:
    if path is None:
        return WorkbenchLocalConfig()

    config_path = Path(path).expanduser().resolve()
    if not config_path.is_file():
        raise WorkbenchConfigError(f"workbench config does not exist: {config_path}")

    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkbenchConfigError(f"workbench config is not valid JSON: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise WorkbenchConfigError("workbench config must be a JSON object")

    unknown_fields = sorted(set(payload) - WORKBENCH_CONFIG_FIELDS)
    if unknown_fields:
        raise WorkbenchConfigError(f"unknown workbench config field: {unknown_fields[0]}")

    return _config_from_mapping(payload)


def _config_from_mapping(payload: dict[str, Any]) -> WorkbenchLocalConfig:
    host = _text_field(payload.get("host", DEFAULT_WORKBENCH_HOST), "host")
    port = _port_field(payload.get("port", DEFAULT_WORKBENCH_PORT))
    frontend_dist = _text_field(payload.get("frontend_dist", DEFAULT_FRONTEND_DIST), "frontend_dist")
    metadata_db = payload.get("metadata_db", DEFAULT_METADATA_DB)
    if metadata_db is not None:
        metadata_db = _text_field(metadata_db, "metadata_db")
    return WorkbenchLocalConfig(
        host=host,
        port=port,
        frontend_dist=frontend_dist,
        metadata_db=metadata_db,
    )


def _text_field(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorkbenchConfigError(f"workbench config field {field_name} must be a non-empty string")
    return value


def _port_field(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise WorkbenchConfigError("workbench config field port must be an integer")
    if value < 1 or value > 65535:
        raise WorkbenchConfigError("workbench config field port must be between 1 and 65535")
    return value
