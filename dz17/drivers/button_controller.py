import time


class ButtonController:
    CHANNELS = {
        "K1": 1,
        "K2": 2,
        "K3": 3,
        "K4": 4,
    }

    def __init__(self, relay):
        self.relay = relay

    def _channel(self, button):
        if button not in self.CHANNELS:
            raise ValueError(f"Unknown button: {button}")
        return self.CHANNELS[button]

    def short_press(self, button):
        self.relay.press(self._channel(button), duration=0.2)

    def long_press(self, button):
        self.relay.press(self._channel(button), duration=1.7)

    def press_pair(self, first, second):
        ch1 = self._channel(first)
        ch2 = self._channel(second)

        if ch1 == ch2:
            raise ValueError("Buttons must be different")

        self.relay.on(ch1)
        try:
            self.relay.on(ch2)
            time.sleep(2.2)
        finally:
            self.relay.off(ch2)
            self.relay.off(ch1)
