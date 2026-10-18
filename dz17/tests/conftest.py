import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from drivers.relay_controller import RelayController
from drivers.vision_client import VisionClient


@pytest.fixture
def relay():
    return RelayController()


@pytest.fixture
def vision():
    return VisionClient()
