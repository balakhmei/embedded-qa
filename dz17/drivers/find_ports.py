from serial.tools import list_ports


def find_port(vid: int, pid: int) -> str:
    matches = [
        port
        for port in list_ports.comports()
        if port.vid == vid and port.pid == pid
    ]

    if not matches:
        raise RuntimeError(
            f"USB device {vid:04X}:{pid:04X} not found"
        )

    if len(matches) > 1:
        devices = ", ".join(port.device for port in matches)
        raise RuntimeError(
            f"Multiple USB devices {vid:04X}:{pid:04X} found: {devices}"
        )

    return matches[0].device
