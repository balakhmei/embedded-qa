import re
from dataclasses import dataclass


VALVE_PATTERN = re.compile(
    r"\[VALVE\]\s+(open|closed),\s+auto\s+(on|off),\s+cycles\s+(\d+)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ValveStatus:
    state: str
    auto: str
    cycles: int


class ValveHelper:
    def __init__(self, uart):
        self.uart = uart

    def get_status(self):
        lines = self.uart.send_command("relay status", timeout=3)

        matches = [
            match
            for line in lines
            if (match := VALVE_PATTERN.search(line))
        ]

        if not matches:
            raise AssertionError(
                f"VALVE status not found in UART response: {lines[-10:]}"
            )

        state, auto, cycles = matches[-1].groups()

        return ValveStatus(
            state=state.lower(),
            auto=auto.lower(),
            cycles=int(cycles),
        )
