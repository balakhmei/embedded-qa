import re
import time
from turtle import mode

import serial
from serial.tools import list_ports

def find_device_port(vid=0x0403):
    for port in list_ports.comports():
        if port.vid == vid:
            return port.device

    raise RuntimeError(
        f"USB-UART adapter with VID {vid:04X} not found"
    )
    
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

        return self.read_lines(self.timeout)

    def wait_for_pattern(self, pattern, timeout):
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
        self.send_command("logout")

        self.send_command(
            f"register {login} {password}"
        )

        response = self.send_command(
            f"login {login} {password}"
        )

        return any(
            "Session Started" in line
            for line in response
        )
    
    def get_status(self):
        return self.send_command("status")
      
    def get_distance(self):
        response = self.send_command("distance")

        for line in response:
            match = re.search(
                r"\[Distance\].*?([\d.]+)\s*cm",
                line
            )

            if match:
                return float(match.group(1))

        raise RuntimeError(
            "Distance value not found in device response"
        )
        
    def set_led(self, state):
        if state not in ("on", "off"):
            raise ValueError("LED state must be 'on' or 'off'")

        return self.send_command(f"led {state}")
    
    def arm_alarm(self):
        return self.send_command("alarm arm")


    def disarm_alarm(self):
        return self.send_command("alarm disarm")


    def clear_alarm(self):
        return self.send_command("alarm clear")


    def get_alarm_status(self):
        return self.send_command("alarm status")
      
    def set_distance_alarm(self, threshold):
        return self.send_command(f"distance alarm {threshold}")


    def disable_distance_alarm(self):
        return self.send_command("distance alarm off")
    
    def set_sensor_value(self, value):
        return self.send_command(f"sensor set {value}")
      
    def start_sensor(self):
        return self.send_command("sensor start")


    def stop_sensor(self):
        return self.send_command("sensor stop")
    
    def set_alarm_threshold(self, value):
        return self.send_command(
            f"config set alarm_threshold {value}"
        )
        
    def wait_for_alarm_trigger(self, timeout=5):
        return self.wait_for_pattern(
            "TRIGGERED",
            timeout
        )
        
    def set_sensor_mode(self, mode):
      return self.send_command(f"sensor mode {mode}")
    
    def set_config(self, key, value):
        return self.send_command(f"config set {key} {value}")

    def get_config(self, key):
        return self.send_command(f"config get {key}")

    def save_config(self):
        return self.send_command("config save")

    def reboot(self):
        self.ser.write(b"reboot\r\n")