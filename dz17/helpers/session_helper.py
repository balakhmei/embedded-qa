class SessionHelper:
    def __init__(self, uart):
        self.uart = uart

    def ensure_ready(self):
        wifi = self.uart.send_command("reconnect", timeout=8)

        if not any(
            "got ip" in line.lower()
            or "connected to" in line.lower()
            or "W114" in line
            for line in wifi
        ):
            raise AssertionError(
                f"Wi-Fi reconnect not confirmed: {wifi[-10:]}"
            )

        session = self.uart.send_command("whoami", timeout=3)

        if any("user: user" in line.lower() for line in session):
            print("AUTH: already logged in")
            return

        login = self.uart.send_command(
            "login user 123456", timeout=4
        )

        if any("E2" in line for line in login):
            raise AssertionError(
                "UART login failed; check DUT authentication state"
            )

        session = self.uart.send_command("whoami", timeout=3)

        if not any("user: user" in line.lower() for line in session):
            raise AssertionError(
                f"UART login not confirmed: {session[-10:]}"
            )

        print("WIFI: connected")
        print("AUTH: user logged in")
