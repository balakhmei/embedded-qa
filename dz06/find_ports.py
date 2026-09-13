from serial.tools import list_ports


ports = list_ports.comports()

if not ports:
    print("No serial ports found.")
else:
    print("Available serial ports:")

    for port in ports:
        print(f"Device: {port.device}")
        print(f"Description: {port.description}")
        print(f"HWID: {port.hwid}")
        print("-" * 40)