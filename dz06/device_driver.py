import re
import time
import serial


class DeviceDriver:
    def __init__(self, port, timeout=2):
        # Зберігаємо параметри підключення
        self.port = port
        self.timeout = timeout
        self.ser = None
    
    def open(self):
        # Відкриваємо UART-з'єднання з параметрами 115200 8N1
        self.ser = serial.Serial(
            port=self.port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )
      
        # Очищуємо вхідний буфер від даних, отриманих до початку тесту
        self.ser.reset_input_buffer()
    
    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        
    def read_lines(self, timeout):
        lines = []
        end_time = time.time() + timeout

        # Читаємо UART до завершення заданого часу очікування
        while time.time() < end_time:
            raw_line = self.ser.readline()

            if not raw_line:
                continue

            # Перетворюємо отримані bytes у звичайний Python-рядок
            line = raw_line.decode("utf-8", errors="replace")
            
            # Видаляємо ANSI escape-коди з відповіді пристрою
            line = re.sub(r'\x1b\[[0-9;]*[mK]', '', line)
            
            # Прибираємо \r\n та зайві пробіли на початку і в кінці рядка
            line = line.strip()

            # Порожні рядки не додаємо до результату
            if line:
                lines.append(line)

        return lines
    
    def send_command(self, command):
        # Гарантуємо завершення кожної UART-команди символами CR+LF
        if not command.endswith("\r\n"):
            command += "\r\n"
          
        self.ser.write(command.encode("utf-8"))
        
        # Даємо firmware невелику паузу для формування відповіді
        time.sleep(0.1)

        return self.read_lines(self.timeout)
    
    def wait_for(self, pattern, timeout):
        end_time = time.time() + timeout

        # Читаємо UART до появи потрібного тексту або завершення timeout
        while time.time() < end_time:
            raw_line = self.ser.readline()

            if not raw_line:
                continue

            line = raw_line.decode("utf-8", errors="replace")
            line = re.sub(r'\x1b\[[0-9;]*[mK]', '', line)
            line = line.strip()

            if pattern in line:
                return True

        return False
    
    def login(self, login, password):
        # Створюємо користувача, після чого виконуємо авторизацію
        self.send_command(f"register {login} {password}")

        response = self.send_command(f"login {login} {password}")

        # Успішна авторизація підтверджується повідомленням firmware
        for line in response:
            if "Session Started" in line:
                return True

        return False
