def test_wrong_password(device, wifi_ssid):
    device.wifi_disconnect()

    result = device.wifi_connect(
        wifi_ssid,
        "WrongPass123"
    )

    assert result is False, (
        "Connection unexpectedly succeeded with wrong password"
    )

    assert "connect to the AP fail" in device.last_wifi_message, (
        f"Expected connection failure message, got: "
        f"{device.last_wifi_message}"
    )


def test_short_password(device, wifi_ssid):
    device.wifi_disconnect()

    result = device.wifi_connect(
        wifi_ssid,
        "1234567"
    )

    assert result is False, (
        "Connection unexpectedly accepted password shorter than 8 characters"
    )

    assert "password too short" in device.last_wifi_message, (
        f"Expected short password message, got: "
        f"{device.last_wifi_message}"
    )


def test_nonexistent_ssid(device):
    result = device.wifi_connect(
        "NonExistingWiFi_12345",
        "12345678"
    )

    assert result is False, (
        "Connection to unknown SSID unexpectedly succeeded"
    )

    response = device.send_command("help")

    assert response, (
        "Device did not respond to help after failed connection"
    )