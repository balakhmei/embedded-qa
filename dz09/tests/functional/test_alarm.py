import pytest


@pytest.mark.parametrize("threshold", [20, 30, 40])
def test_distance_alarm_trigger(authenticated_device, threshold):
    device = authenticated_device

    device.set_sensor_mode("distance")
    device.set_distance_alarm(threshold)
    device.arm_alarm()
    device.start_sensor()

    try:
        assert device.wait_for_alarm_trigger(timeout=10)
    finally:
        device.stop_sensor()
        device.disarm_alarm()
        device.clear_alarm()
        device.disable_distance_alarm()