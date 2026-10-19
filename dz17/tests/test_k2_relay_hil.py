import time

from drivers.button_controller import ButtonController
from helpers.valve_helper import ValveHelper


def test_k2_relay_toggle(relay, uart):
    buttons = ButtonController(relay)
    valve = ValveHelper(uart)

    initial = valve.get_status()
    assert initial.auto == "off", "Valve AUTO mode must be OFF"

    expected = "open" if initial.state == "closed" else "closed"
    pressed = False

    try:
        buttons.short_press("K2")
        pressed = True
        time.sleep(1)

        after_first = valve.get_status()

        assert after_first.state == expected, (
            f"Expected {expected}, got {after_first.state}"
        )
        assert after_first.cycles == initial.cycles + 1, (
            f"Expected cycles {initial.cycles + 1}, "
            f"got {after_first.cycles}"
        )

        buttons.short_press("K2")
        time.sleep(1)

        after_second = valve.get_status()

        assert after_second.state == initial.state, (
            f"Expected restored state {initial.state}, "
            f"got {after_second.state}"
        )
        assert after_second.cycles == initial.cycles + 2, (
            f"Expected cycles {initial.cycles + 2}, "
            f"got {after_second.cycles}"
        )

        print(
            f"\nK2: {initial.state} -> "
            f"{after_first.state} -> {after_second.state}"
        )
        print(
            f"CYCLES: {initial.cycles} -> "
            f"{after_first.cycles} -> {after_second.cycles}"
        )

    finally:
        if pressed:
            try:
                current = valve.get_status()
                if current.state != initial.state:
                    time.sleep(1)
                    buttons.short_press("K2")
                    time.sleep(1)

                restored = valve.get_status()
                if restored.state != initial.state:
                    print(
                        "WARNING: Valve did not return "
                        f"to initial state {initial.state}"
                    )
            except Exception as exc:
                print(f"WARNING: Valve restoration failed: {exc}")
