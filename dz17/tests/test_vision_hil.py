import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from drivers.relay_controller import RelayController
from drivers.vision_client import VisionClient



def test_k1_toggles_led_color(relay, vision):
    initial_color = vision.get_led_color()
    assert initial_color in ("RED", "GREEN"), (
        f"Unexpected initial LED color: {initial_color}"
    )

    expected_color = "GREEN" if initial_color == "RED" else "RED"
    print(f"\nInitial LED: {initial_color}")

    relay.press(1, duration=0.2)
    time.sleep(1)

    actual_color = vision.get_led_color()
    print(f"Expected LED: {expected_color}")
    print(f"Actual LED:   {actual_color}")

    assert actual_color == expected_color, (
        f"K1 toggle failed: expected {expected_color}, got {actual_color}"
    )
