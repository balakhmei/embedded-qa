import time
from serial.tools import list_ports

from device_driver import DeviceDriver

def test_sensor_history(device):
    print("\n=== TEST 1: Sensor History ===")

    # Запускаємо збір показань сенсора
    device.send_command("sensor start")

    # Чекаємо достатньо часу для накопичення більше 8 показань
    time.sleep(10)

    # Зупиняємо збір даних
    device.send_command("sensor stop")

    # Отримуємо історію показань
    response = device.send_command("sensor history")

    # Вибираємо тільки рядки, що містять показання сенсора
    lines = [
        line for line in response
        if "[Sensor]" in line and "] temp:" in line
    ]

    count = len(lines)

    print(f"Sensor records found: {count}")

    if count <= 5:
        print(
            f"PASS: Bug reproduced. Expected 10 records, "
            f"but received {count}."
    )
    else:
        print(
            f"FAIL: Bug not reproduced. Expected 10 records, "
            f"received {count}."
    )
    
def test_led_blink(device):
    print("\n=== TEST 2: LED Blink ===")

    # Запам'ятовуємо час перед виконанням команди
    start_time = time.time()

    response = device.send_command("led blink 15")

    for line in response:
        print(line)

    # Розраховуємо фактичний час виконання команди
    elapsed_time = time.time() - start_time

    print(f"Execution time: {elapsed_time:.2f} seconds")

    # Якщо час < 3.5 с, дефект обрізання значення > 10 підтверджено
    if elapsed_time < 3.5:
        print(
            f"PASS: Bug reproduced. Expected ~4.5 s, "
            f"but command completed in {elapsed_time:.2f} s."
        )
    else:
        print(
            f"FAIL: Bug not reproduced. "
            f"Execution time: {elapsed_time:.2f} s."
        )

def test_login_rate_limit(device):
    print("\n=== TEST 3: Login Rate Limit ===")

    # Завершуємо поточну сесію перед перевіркою авторизації
    device.send_command("logout")

    # Три невдалі спроби входу
    for attempt in range(3):
        response = device.send_command("login testuser wrongpass")
        print(f"Wrong login attempt {attempt + 1}")

        for line in response:
            print(line)

    # Після трьох помилок пробуємо правильний пароль
    response = device.send_command("login testuser test123")

    for line in response:
        print(line)

    locked = any("locked" in line.lower() for line in response)
    session_started = any("Session Started" in line for line in response)

    if locked and not session_started:
        print(
            "PASS: Bug reproduced. Account is locked after 3 failed attempts "
            "and Session Started is absent."
    )
    else:
        print(
            "FAIL: Bug not reproduced. "
            f"locked={locked}, Session Started={session_started}"
    )

def find_device_port():
    for port in list_ports.comports():
        if port.vid == 0x1A86 and port.pid == 0x55D3:
            return port.device

    return None
  
port = find_device_port()

if port is None:
    print("FAIL: Device port not found.")
else:
    print(f"Detected port: {port}")

    device = DeviceDriver(port)

    try:
        device.open()

        if device.login("testuser", "test123"):
            print("Login: PASS")

            test_sensor_history(device)
            test_led_blink(device)
            test_login_rate_limit(device)

        else:
            print("Login: FAIL")

    finally:
        device.close()