def test_device_status(authenticated_device):
    response = authenticated_device.get_status()

    assert any("[Status] Checking components" in line for line in response)
    
    
def test_distance_reading(authenticated_device):
    distance = authenticated_device.get_distance()

    assert distance >= 0
    
    
def test_led_control(authenticated_device):
    response = authenticated_device.set_led("on")

    assert any("LED ON" in line for line in response)

    authenticated_device.set_led("off")
    