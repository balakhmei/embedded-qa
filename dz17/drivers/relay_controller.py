import time
import serial
from drivers.find_ports import find_port


class RelayController:
    def __init__(self, port=None, baudrate=9600):
        self.port = port if port is not None else find_port(0x1A86, 0x7523)
        self.baudrate = baudrate

    def set_channel(self, channel: int, state: bool):
        if channel not in range(1, 5):
            raise ValueError("Channel must be between 1 and 4")

        command = bytes([
            0xA0,
            channel,
            int(state),
            (0xA0 + channel + int(state)) & 0xFF,
        ])

        with serial.Serial(self.port, self.baudrate, timeout=1) as connection:
            connection.write(command)
            connection.flush()

    def on(self, channel: int):
        self.set_channel(channel, True)

    def off(self, channel: int):
        self.set_channel(channel, False)

    def press(self, channel: int, duration=0.2):
        if duration <= 0:
            raise ValueError("Duration must be positive")

        self.on(channel)
        try:
            time.sleep(duration)
        finally:
            self.off(channel)