import re

from drivers.button_controller import ButtonController


PING_PATTERN = re.compile(
    r"\[SONAR\] ping: echo (\d+(?:\.\d+)?) cm"
)


def test_k3_sonar_start_stop(relay, uart):
    buttons = ButtonController(relay)
    started = False

    try:
        buttons.short_press("K3")
        started = True

        start_lines = uart.read_lines(timeout=5)
        start_output = "\n".join(start_lines)

        assert "active pinging for 30 s" in start_output, (
            f"Sonar start confirmation missing: {start_lines[-15:]}"
        )

        distances = [
            float(match.group(1))
            for line in start_lines
            if (match := PING_PATTERN.search(line))
        ]

        assert len(distances) >= 3, (
            f"Expected at least 3 sonar measurements, got {len(distances)}"
        )

        print(f"\nSONAR START: PASS")
        print(f"MEASUREMENTS: {len(distances)}")
        print(f"DISTANCES: {distances}")

        buttons.short_press("K3")
        started = False

        stop_lines = uart.read_lines(timeout=3)
        stop_output = "\n".join(stop_lines)

        assert "pinging stopped (K3)" in stop_output, (
            f"Sonar stop confirmation missing: {stop_lines[-15:]}"
        )

        print("SONAR STOP: PASS")

    finally:
        if started:
            try:
                buttons.short_press("K3")
                print("CLEANUP: K3 stop requested")
            except Exception as exc:
                print(f"WARNING: Sonar cleanup failed: {exc}")
