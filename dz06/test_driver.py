from device_driver import DeviceDriver


PORT = "/dev/cu.usbmodem5C930634961"

device = DeviceDriver(PORT)

device.open()

result = device.login("testuser", "test123")

print("Login result:", result)

device.close()