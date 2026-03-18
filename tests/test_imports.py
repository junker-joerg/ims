"""Basic import tests for the IMS Python port scaffold."""

import importlib


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


def test_modules_are_importable() -> None:
    for module_name in MODULES:
        assert importlib.import_module(module_name) is not None
