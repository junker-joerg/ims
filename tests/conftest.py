from pathlib import Path
import sys

import pytest


TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
PYTHON_PORT_DIR = (REPO_ROOT / "python_port").resolve()

if str(PYTHON_PORT_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_PORT_DIR))


@pytest.fixture
def minimal_scenario_path() -> Path:
    return TESTS_DIR / "fixtures" / "minimal_scenario.json"
