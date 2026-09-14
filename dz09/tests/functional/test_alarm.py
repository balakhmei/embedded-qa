import pytest


@pytest.mark.parametrize(
    "threshold",
    [20, 30, 40],
)
def test_distance_alarm_threshold(authenticated_device, threshold):
    response = authenticated_device.set_distance_alarm(threshold)

    assert any(
        f"closer than {threshold} cm" in line
        for line in response
    )