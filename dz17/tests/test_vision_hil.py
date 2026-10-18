import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from drivers.relay_controller import RelayController


def get_led_color():
    result = subprocess.run(
        ["ssh", "rpi", "python3 ~/vision_hil/led_detector.py"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )

    match = re.search(r"LED_COLOR=(RED|GREEN|UNKNOWN)", result.stdout)
    assert match, f"LED detector returned unexpected output: {result.stdout}"
    return match.group(1)


def test_k1_toggles_led_color():
    initial_color = get_led_color()
    assert initial_color in ("RED", "GREEN"), (
        f"Unexpected initial LED color: {initial_color}"
    )

    expected_color = "GREEN" if initial_color == "RED" else "RED"
    print(f"\nInitial LED: {initial_color}")

    relay = RelayController()
    relay.press(1, duration=0.2)
    time.sleep(1)

    actual_color = get_led_color()
    print(f"Expected LED: {expected_color}")
    print(f"Actual LED:   {actual_color}")

    assert actual_color == expected_color, (
        f"K1 toggle failed: expected {expected_color}, got {actual_color}"
    )
