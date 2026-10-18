import re
import time

import serial

from drivers.find_ports import find_port


class UartClient:
    def __init__(self, port=None, baudrate=115200, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def open(self):
        if self.ser and self.ser.is_open:
            return

        if self.port is None:
            self.port = find_port(0x0403, 0x6001)

        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def read_lines(self, timeout=None):
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("UART port is not open")

        duration = self.timeout if timeout is None else timeout
        deadline = time.monotonic() + duration
        lines = []

        try:
            while time.monotonic() < deadline:
                self.ser.timeout = max(
                    0, deadline - time.monotonic()
                )

                raw = self.ser.readline()
                if not raw:
                    continue

                line = raw.decode(
                    "utf-8", errors="replace"
                )
                line = re.sub(
                    r"\x1b\[[0-9;]*[mK]", "", line
                ).strip()

                if line:
                    lines.append(line)

        finally:
            self.ser.timeout = self.timeout

        return lines

    def send_command(self, command, timeout=None):
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("UART port is not open")

        self.ser.reset_input_buffer()
        self.ser.write(
            (command.rstrip("\r\n") + "\r\n").encode("utf-8")
        )
        self.ser.flush()

        return self.read_lines(timeout)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
