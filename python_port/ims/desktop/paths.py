from __future__ import annotations

import os
from pathlib import Path
import sys


def resource_root() -> Path:
    """Repository in development, immutable resources in a frozen bundle."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "resources"
    return Path(__file__).resolve().parents[3]


def user_root(override: Path | None = None) -> Path:
    if override is not None:
        result = override.expanduser().resolve()
    else:
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            raise RuntimeError("Windows-Benutzerablage LOCALAPPDATA fehlt.")
        result = Path(local) / "IMS" / "Workbench"
    application = (Path(sys.executable).parent if getattr(sys, 'frozen', False)
                   else resource_root()).resolve()
    if result.is_relative_to(application):
        raise ValueError("Nutzerdaten müssen außerhalb der Anwendungsdateien liegen.")
    result.mkdir(parents=True, exist_ok=True)
    return result
