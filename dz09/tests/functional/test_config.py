import pytest


@pytest.mark.xfail(
    reason="Firmware bug: dist_threshold is not persisted after reboot"
)

def test_config_persistence(authenticated_device):
    device = authenticated_device

    device.set_config("dist_threshold", 60)
    device.save_config()

    device.reboot()

    # Firmware outputs "Device ready" instead of "App started".
    # See README.md for details.
    assert device.wait_for_pattern(
        "Device ready",
        timeout=10
    )

    assert device.login("testuser", "test123")

    response = device.get_config("dist_threshold")

    assert any(
        "dist_threshold = 60" in line
        for line in response
    )