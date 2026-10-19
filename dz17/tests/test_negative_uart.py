import re

import pytest


@pytest.mark.parametrize(
    "command, expected_error",
    [
        ("invalidcommand", "E001"),
        ("lamp brightness 101", "E504"),
        ("distance 21", "E704"),
        ("relay pulse 99", "E603"),
    ],
    ids=["NEG-001", "NEG-002", "NEG-003", "BUG-RL-01"],
)
def test_invalid_uart_commands(authenticated_uart, command, expected_error):
    lines = authenticated_uart.send_command(command, timeout=4)

    responses = [
        line for line in lines
        if "sentry:" in line and "[PWR]" not in line
    ]

    print(f"\nCOMMAND: {command}")
    print("\n".join(responses))

    error_found = any(
        re.search(rf"\b{expected_error}\b", line)
        for line in responses
    )

    if command == "relay pulse 99" and not error_found:
        opened = any("[VALVE] OPEN (pulse)" in line for line in responses)
        closed = any("[VALVE] CLOSED (pulse end)" in line for line in responses)

        if opened and closed:
            pytest.xfail(
                "BUG-RL-01: invalid 99 ms pulse was executed"
            )

    assert error_found, (
        f"Expected {expected_error} for '{command}', "
        f"received: {responses}"
    )
