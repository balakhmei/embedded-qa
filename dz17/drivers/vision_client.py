import re
import subprocess
from pathlib import Path


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

    def capture_evidence(self, filename):
        local_dir = Path(__file__).resolve().parents[1] / "evidence" / "hil"
        local_dir.mkdir(parents=True, exist_ok=True)

        filename = Path(filename).name
        if not filename.lower().endswith(".png"):
            raise ValueError("Evidence filename must end with .png")

        remote_path = f"vision_hil/evidence/{filename}"
        local_path = local_dir / filename

        subprocess.run(
            [
                "ssh",
                self.host,
                f"python3 ~/vision_hil/led_detector.py --save ~/vision_hil/evidence/{filename}",
            ],
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=True,
        )

        subprocess.run(
            ["scp", f"{self.host}:{remote_path}", str(local_path)],
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=True,
        )

        return local_path
