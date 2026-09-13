import serial
import time

PORT = "/dev/cu.usbmodem5C930634961"

ser = serial.Serial(
  port=PORT,
  baudrate=115200,
  bytesize=serial.EIGHTBITS,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  timeout=2,
)

print("Port opened:", ser.is_open)
ser.write(b"help\r\n")

response = b""

while True:
    data = ser.read(ser.in_waiting or 1)

    if data:
        response += data
    else:
        break

print(response.decode())
ser.close()
