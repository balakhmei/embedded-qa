import re

import pytest



CREATED_PATTERN = re.compile(r"\[CIC #(\d+) INFO\] test: test alert")
LIST_PATTERN = re.compile(
    r"#(\d+)\s+\S+\s+(INFO|WARNING|CRITICAL)\s+(\*)?\s+"
)


def get_alert_states(uart, ids):
    lines = uart.send_command("alert list", timeout=4)
    states = {}

    for line in lines:
        match = LIST_PATTERN.search(line)
        if match and int(match.group(1)) in ids:
            states[int(match.group(1))] = match.group(3) == "*"

    assert set(states) == set(ids), (
        f"Expected alert IDs {ids}, found {states}"
    )
    return states


def test_bug_cic_01_ack_by_id(authenticated_uart):
    uart = authenticated_uart

    ids = []
    for _ in range(2):
        lines = uart.send_command("alert test info", timeout=3)
        matches = [
            match
            for line in lines
            if (match := CREATED_PATTERN.search(line))
        ]
        assert matches, f"Alert creation failed: {lines[-15:]}"
        ids.append(int(matches[-1].group(1)))

    assert ids[0] != ids[1], f"Duplicate alert IDs: {ids}"

    before = get_alert_states(uart, ids)
    assert all(before.values()), f"Alerts not initially unacknowledged: {before}"

    response = uart.send_command(f"alert ack {ids[1]}", timeout=3)
    print(f"\nACK TARGET: #{ids[1]}")
    print("\n".join(line for line in response if "[CIC]" in line))

    after = get_alert_states(uart, ids)
    print(f"BEFORE: {before}")
    print(f"AFTER:  {after}")

    if not after[ids[0]] and after[ids[1]]:
        pytest.xfail(
            f"BUG-CIC-01 confirmed: alert #{ids[0]} acknowledged "
            f"instead of target #{ids[1]}"
        )

    assert after[ids[0]], (
        f"Unexpected ACK behavior: alert #{ids[0]} was acknowledged"
    )
    assert not after[ids[1]], (
        f"Target alert #{ids[1]} remains unacknowledged"
    )
