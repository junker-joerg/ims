"""Import smoke tests for the IMS Python scaffold."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "python_port"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODULES = [
    "ims",
    "ims.model",
    "ims.model.entities",
    "ims.engine",
    "ims.engine.context",
    "ims.engine.scheduler",
    "ims.io",
    "ims.analysis",
]


def test_scaffold_modules_are_importable() -> None:
    for module_name in MODULES:
        assert importlib.import_module(module_name) is not None
