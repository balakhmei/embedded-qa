# Smart Greenhouse Controller — Test Project Structure

```text
dz12/
├── PRD.md
├── stand_diagram.png
├── project_structure.md
├── traceability_matrix.md
├── wokwi_link.md
├── README.md
│
├── screenshots/
│   ├── fan_off_25_1.png
│   └── fan_on_30_7.png
│
├── drivers/
│   ├── device_driver.py
│   └── find_ports.py
│
├── hil/
│   ├── hil_controller.py
│   ├── sensor_simulator.py
│   └── output_monitor.py
│
├── tests/
│   ├── smoke/
│   │   ├── test_dut_connection.py
│   │   └── test_hil_connection.py
│   │
│   ├── functional/
│   │   ├── test_sensors.py
│   │   ├── test_fan_control.py
│   │   ├── test_irrigation.py
│   │   ├── test_light_control.py
│   │   ├── test_actuator_status.py
│   │   ├── test_sensor_failure.py
│   │   └── test_startup.py
│   │
│   └── non_functional/
│       ├── test_timing.py
│       ├── test_uart.py
│       ├── test_reliability.py
│       └── test_recovery.py
│
├── conftest.py
├── pytest.ini
└── requirements.txt