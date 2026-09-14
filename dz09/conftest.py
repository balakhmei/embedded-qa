import pytest

from device_driver import DeviceDriver, find_device_port

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
def authenticated_device(device):
    if not device.login("testuser", "test123"):
        pytest.fail("Failed to authenticate on device")

    return device