import time


def test_k1_relay_camera_uart(relay, vision, uart):
    initial_color = vision.get_led_color()
    assert initial_color in ("RED", "GREEN"), (
        f"Unexpected initial LED color: {initial_color}"
    )

    initial_status = uart.send_command("status", timeout=3)
    assert any("SWM-2 status" in line for line in initial_status), (
        f"DUT did not return expected status: {initial_status}"
    )

    expected_color = "GREEN" if initial_color == "RED" else "RED"

    relay.press(1, duration=0.2)
    time.sleep(1)

    actual_color = vision.get_led_color()
    assert actual_color == expected_color, (
        f"Expected LED {expected_color}, got {actual_color}"
    )

    final_status = uart.send_command("status", timeout=3)
    assert any("SWM-2 status" in line for line in final_status), (
        f"DUT did not respond after K1 press: {final_status}"
    )

    print(f"\nLED: {initial_color} -> {actual_color}")
    print("UART: responsive before and after K1 press")
