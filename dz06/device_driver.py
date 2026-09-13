import re
import time

import serial


class DeviceDriver:
    def __init__(self, port, timeout=2):
        self.port = port
        self.timeout = timeout
        self.ser = None

    def open(self):
        self.ser = serial.Serial(
            port=self.port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )

        self.ser.reset_input_buffer()

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _decode_line(self, raw_line):
        line = raw_line.decode("utf-8", errors="replace")

        # Видаляємо ANSI escape-коди
        line = re.sub(r'\x1b\[[0-9;]*[mK]', '', line)

        return line.strip()

    def read_lines(self, timeout):
        lines = []
        deadline = time.monotonic() + timeout

        while True:
            remaining = deadline - time.monotonic()

            if remaining <= 0:
                break

            self.ser.timeout = remaining
            raw_line = self.ser.readline()

            if not raw_line:
                continue

            line = self._decode_line(raw_line)

            if line:
                lines.append(line)

        # Повертаємо стандартний timeout
        self.ser.timeout = self.timeout

        return lines

    def send_command(self, command):
        if not command.endswith("\r\n"):
            command += "\r\n"

        self.ser.write(command.encode("utf-8"))

        time.sleep(0.1)

        return self.read_lines(self.timeout)

    def wait_for(self, pattern, timeout):
        deadline = time.monotonic() + timeout

        try:
            while True:
                remaining = deadline - time.monotonic()

                if remaining <= 0:
                    return False

                self.ser.timeout = remaining
                raw_line = self.ser.readline()

                if not raw_line:
                    continue

                line = self._decode_line(raw_line)

                if pattern in line:
                    return True

        finally:
            self.ser.timeout = self.timeout

    def login(self, login, password):
        self.send_command(f"register {login} {password}")

        response = self.send_command(
            f"login {login} {password}"
        )

        return any(
            "Session Started" in line
            for line in response
        )