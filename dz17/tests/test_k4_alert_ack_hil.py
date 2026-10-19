import re

from drivers.button_controller import ButtonController


CREATED_PATTERN = re.compile(r"\[CIC #(\d+) INFO\] test: test alert")
ACK_PATTERN = re.compile(r"\[CIC\] #(\d+) acknowledged \(K4\)")
LIST_PATTERN = re.compile(r"#(\d+)\s+\S+\s+(INFO|WARNING|CRITICAL)\s+(\*)?\s+")


def test_k4_ack_latest_alert(relay, uart):
    buttons = ButtonController(relay)

    created_lines = uart.send_command("alert test info", timeout=3)
    created = [
        match
        for line in created_lines
        if (match := CREATED_PATTERN.search(line))
    ]

    assert created, f"Test alert creation not confirmed: {created_lines[-15:]}"
    alert_id = int(created[-1].group(1))

    print(f"\nCREATED ALERT: #{alert_id}")

    before_lines = uart.send_command("alert list", timeout=3)
    before_matches = [
        match
        for line in before_lines
        if (match := LIST_PATTERN.search(line))
        and int(match.group(1)) == alert_id
    ]

    assert before_matches, f"Alert #{alert_id} not found before ACK"
    assert before_matches[-1].group(3) == "*", (
        f"Alert #{alert_id} was already acknowledged"
    )

    buttons.short_press("K4")

    ack_lines = uart.read_lines(timeout=3)
    ack_ids = [
        int(match.group(1))
        for line in ack_lines
        if (match := ACK_PATTERN.search(line))
    ]

    assert alert_id in ack_ids, (
        f"K4 did not acknowledge alert #{alert_id}: {ack_lines[-15:]}"
    )

    after_lines = uart.send_command("alert list", timeout=3)
    after_matches = [
        match
        for line in after_lines
        if (match := LIST_PATTERN.search(line))
        and int(match.group(1)) == alert_id
    ]

    assert after_matches, f"Alert #{alert_id} missing after ACK"
    assert after_matches[-1].group(3) is None, (
        f"Alert #{alert_id} remains unacknowledged"
    )

    print(f"ACKNOWLEDGED ALERT: #{alert_id}")
    print("K4 SHORT PRESS: PASS")
