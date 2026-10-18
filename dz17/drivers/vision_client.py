import re
import subprocess


class VisionClient:
    def __init__(self, host="rpi", timeout=30):
        self.host = host
        self.timeout = timeout

    def get_led_color(self):
        result = subprocess.run(
            ["ssh", self.host, "python3 ~/vision_hil/led_detector.py"],
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=True,
        )

        match = re.search(
            r"LED_COLOR=(RED|GREEN|UNKNOWN)",
            result.stdout,
        )

        if not match:
            raise ValueError(
                f"Unexpected LED detector output: {result.stdout}"
            )

        return match.group(1)
