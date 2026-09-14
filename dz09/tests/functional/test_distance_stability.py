import statistics

import statistics

import pytest


@pytest.mark.xfail(
    reason="Distance readings are intermittently unstable with a fixed target"
)
def test_distance_readings_are_stable(authenticated_device):
    readings = [
        authenticated_device.get_distance()
        for _ in range(10)
    ]

    median = statistics.median(readings)
    tolerance = 3.0

    stable_readings = [
        value
        for value in readings
        if abs(value - median) <= tolerance
    ]

    assert len(stable_readings) >= 9, (
        f"Distance readings are unstable: {readings}"
    )