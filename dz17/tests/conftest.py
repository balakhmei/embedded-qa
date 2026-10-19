import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from drivers.relay_controller import RelayController
from drivers.vision_client import VisionClient
from drivers.uart_client import UartClient


@pytest.fixture
def relay():
    controller = RelayController()
    try:
        yield controller
    finally:
        for channel in range(1, 5):
            try:
                controller.off(channel)
            except Exception as exc:
                print(f"WARNING: Failed to release CH{channel}: {exc}")


@pytest.fixture
def vision():
    return VisionClient()


@pytest.fixture
def uart():
    with UartClient() as client:
        yield client


@pytest.fixture
def authenticated_uart(uart):
    from helpers.session_helper import SessionHelper

    SessionHelper(uart).ensure_ready()
    return uart


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    if "vision" not in item.fixturenames:
        return

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = "".join(
        char if char.isalnum() or char in "-_" else "_"
        for char in item.name
    )
    filename = f"{safe_name}_{timestamp}_FAIL.png"

    try:
        vision = item.funcargs.get("vision")
        if vision is None:
            print("WARNING: Vision fixture unavailable; evidence not captured")
            return

        path = vision.capture_evidence(filename)
        print(f"FAIL EVIDENCE: {path}")
    except Exception as exc:
        print(f"WARNING: Failed to capture HIL evidence: {exc}")
