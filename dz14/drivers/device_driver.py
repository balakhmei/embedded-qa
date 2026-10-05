import re
import time
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
        self.last_wifi_message = None

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

        # Remove ANSI escape-codes
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

        # Return the standard timeout
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
        
    def _write_line(self, text=""):
        self.ser.write((text + "\r\n").encode("utf-8"))
    
    def wifi_scan(self):
        self.ser.reset_input_buffer()
        self.ser.write(b"scan\r\n")

        networks = []
        expected_count = None
        deadline = time.monotonic() + 6

        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            self.ser.timeout = remaining

            raw_line = self.ser.readline()

            if not raw_line:
                continue

            line = self._decode_line(raw_line)

            count_match = re.search(r"found\s+(\d+)\s+networks", line)
            if count_match:
                expected_count = int(count_match.group(1))

            match = re.search(r"SSID:\s*(.*?)\s+RSSI:", line)
            if match:
                networks.append(match.group(1).strip())

            if expected_count is not None and len(networks) >= expected_count:
                break

        self.ser.timeout = self.timeout

        return networks
    
    def wifi_status(self):
        response = self.send_command("status")
        text = "\n".join(response)

        connected = re.search(
            r"WiFi:\s*connected",
            text,
            re.IGNORECASE
        ) is not None

        ssid_match = re.search(
            r"SSID:\s*(.+)",
            text,
            re.IGNORECASE
        )

        ip_match = re.search(
            r"IP:\s*(\d+\.\d+\.\d+\.\d+)",
            text,
            re.IGNORECASE
        )

        rssi_match = re.search(
            r"RSSI:\s*(-?\d+)\s*dBm",
            text,
            re.IGNORECASE
        )

        return {
            "connected": connected,
            "ssid": ssid_match.group(1).strip() if ssid_match else None,
            "ip": ip_match.group(1) if ip_match else None,
            "rssi": int(rssi_match.group(1)) if rssi_match else None,
        }
    
    def wifi_disconnect(self):
        return self.send_command("disconnect")
      
    def wifi_connect(self, ssid="", password=""):
        self._write_line("connect")

        if not self.wait_for_pattern("Enter SSID", timeout=10):
            return False

        self._write_line(ssid)

        if not ssid:
            result = self.wait_for_pattern(
                "successfully connected",
                timeout=20
            )
            
            return result

        if not self.wait_for_pattern("Enter password:", timeout=10):
            return False

        self._write_line(password)
        
        self.last_wifi_message = None

        deadline = time.monotonic() + 20

        try:
            while time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                self.ser.timeout = remaining

                raw_line = self.ser.readline()

                if not raw_line:
                    continue

                line = self._decode_line(raw_line)

                if "successfully connected" in line:
                    self.last_wifi_message = line
                    return True

                if "password too short" in line:
                    self.last_wifi_message = line
                    return False

                if "connect to the AP fail" in line:
                    self.last_wifi_message = line
                    return False
                  
            self.last_wifi_message = "timeout"
            return False

        finally:
            self.ser.timeout = self.timeout
    