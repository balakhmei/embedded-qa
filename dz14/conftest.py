import os

import pytest

from drivers.device_driver import DeviceDriver, find_device_port


@pytest.fixture
def device():
    port = find_device_port()

    driver = DeviceDriver(port)
    driver.open()

    try:
        yield driver
    finally:
        driver.close()


@pytest.fixture
def wifi_ssid():
    ssid = os.getenv("TEST_WIFI_SSID")
    assert ssid is not None, "TEST_WIFI_SSID is not set"
    return ssid


@pytest.fixture
def wifi_password():
    password = os.getenv("TEST_WIFI_PASSWORD")
    assert password is not None, "TEST_WIFI_PASSWORD is not set"
    return password