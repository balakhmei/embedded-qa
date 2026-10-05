import re
import pytest


def test_scan_finds_networks(device, wifi_ssid):
    networks = device.wifi_scan()

    assert networks, "Wi-Fi scan returned no networks"
    assert wifi_ssid in networks, f"{wifi_ssid} was not found"


def test_connect_success(device, wifi_ssid, wifi_password):

    # Precondition: device must be disconnected
    device.wifi_disconnect()

    result = device.wifi_connect(wifi_ssid, wifi_password)

    assert result, f"Failed to connect to {wifi_ssid}"

    status = device.wifi_status()

    assert status["connected"] is True
    assert status["ssid"] == wifi_ssid
    assert re.fullmatch(
        r"\d+\.\d+\.\d+\.\d+", status["ip"]
    ),  f"Invalid IP address: {status['ip']}"


@pytest.mark.xfail(
    reason="Firmware reports WiFi connected after disconnect"
)
def test_disconnect(device, wifi_ssid, wifi_password):
    status = device.wifi_status()

    if not status["connected"]:
        connected = device.wifi_connect(wifi_ssid, wifi_password)
        assert connected, f"Failed to connect to {wifi_ssid}"

    device.wifi_disconnect()

    status = device.wifi_status()

    assert status["connected"] is False
    assert status["ssid"] is None
    assert status["ip"] is None
    assert status["rssi"] is None


def test_credentials_survive_reboot(device, wifi_ssid, wifi_password):
  
    # Make sure valid credentials are saved first
    if not device.wifi_status()["connected"]:
        assert device.wifi_connect(wifi_ssid, wifi_password)

    # Reboot the device
    device.reboot()

    # Wait until the device is ready again
    assert device.wait_for_pattern(
        "Type 'connect' to join a network", timeout=15
    ),  "Device did not become ready after reboot"

    # Connect using saved credentials (empty SSID)
    result = device.wifi_connect()

    assert result is True, (
        "Failed to connect using saved Wi-Fi credentials after reboot"
    )
