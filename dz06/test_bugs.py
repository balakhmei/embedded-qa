import time

from serial.tools import list_ports

from device_driver import DeviceDriver


VID = 0x1A86
PID = 0x55D3

SENSOR_INTERVAL_SECONDS = 3
SENSOR_WAIT_SECONDS = 30


def find_device_port():
    for port in list_ports.comports():
        if port.vid == VID and port.pid == PID:
            return port.device

    return None


def test_sensor_history(device):
    print("\n=== TEST 1: Sensor History ===")

    # Запускаємо збір показань сенсора
    device.send_command("sensor start")

    # Чекаємо достатньо часу, щоб firmware гарантовано
    # згенерувала більше 8 показань.
    #
    # sensor_interval = 3000 ms,
    # тому 30 секунд достатньо приблизно для 10 показань.
    time.sleep(SENSOR_WAIT_SECONDS)

    # Зупиняємо збір даних
    device.send_command("sensor stop")

    # Отримуємо історію показань
    response = device.send_command("sensor history")

    # Вибираємо тільки рядки з показаннями сенсора
    lines = [
        line
        for line in response
        if "[Sensor]" in line and "] temp:" in line
    ]

    count = len(lines)

    print(f"Sensor records found: {count}")

    # Методика тесту:
    # ми дали пристрою час накопичити >8 записів.
    # Якщо history повертає максимум 5,
    # дефект обмеження буфера підтверджено.
    if count <= 5:
        print(
            f"PASS: Bug reproduced. "
            f"More than 8 readings should have been generated, "
            f"but history returned only {count} records."
        )
    else:
        print(
            f"FAIL: Bug not reproduced. "
            f"History returned {count} records."
        )


def test_led_blink(device):
    print("\n=== TEST 2: LED Blink ===")

    # monotonic() краще підходить для вимірювання duration
    start_time = time.monotonic()

    response = device.send_command("led blink 15")

    for line in response:
        print(line)

    elapsed_time = time.monotonic() - start_time

    print(f"Execution time: {elapsed_time:.2f} seconds")

    # Для led blink 15 очікується приблизно 4.5 секунди.
    # Якщо команда завершується < 3.5 с,
    # дефект обрізання значення > 10 підтверджено.
    if elapsed_time < 3.5:
        print(
            f"PASS: Bug reproduced. "
            f"Expected ~4.5 s, "
            f"but command completed in {elapsed_time:.2f} s."
        )
    else:
        print(
            f"FAIL: Bug not reproduced. "
            f"Execution time: {elapsed_time:.2f} s."
        )


def test_login_rate_limit(device):
    print("\n=== TEST 3: Login Rate Limit ===")

    # Явно приводимо пристрій до потрібного початкового стану.
    device.send_command("logout")

    # Три невдалі спроби входу
    for attempt in range(3):
        response = device.send_command(
            "login testuser wrongpass"
        )

        print(f"Wrong login attempt {attempt + 1}")

        for line in response:
            print(line)

    # Після трьох невдалих спроб перевіряємо правильний пароль
    response = device.send_command(
        "login testuser test123"
    )

    for line in response:
        print(line)

    locked = any(
        "locked" in line.lower()
        for line in response
    )

    session_started = any(
        "Session Started" in line
        for line in response
    )

    if locked and not session_started:
        print(
            "PASS: Bug reproduced. "
            "Account is locked after 3 failed attempts "
            "and Session Started is absent."
        )
    else:
        print(
            "FAIL: Bug not reproduced. "
            f"locked={locked}, "
            f"Session Started={session_started}"
        )


def main():
    port = find_device_port()

    if port is None:
        print("FAIL: Device port not found.")
        return

    print(f"Detected port: {port}")

    device = DeviceDriver(port)

    try:
        device.open()

        if not device.login("testuser", "test123"):
            print("Login: FAIL")
            return

        print("Login: PASS")

        test_sensor_history(device)
        test_led_blink(device)
        test_login_rate_limit(device)

    finally:
        device.close()


if __name__ == "__main__":
    main()