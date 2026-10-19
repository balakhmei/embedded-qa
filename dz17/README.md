# SENTRY SWM-2 — Embedded QA & HIL Automation

Embedded QA diploma project for testing the SENTRY SWM-2 firmware on an ESP32-S3 device under test (DUT).

The project combines manual firmware verification with a Python/pytest hardware-in-the-loop (HIL) prototype. The automation interacts with real hardware through UART, USB-controlled relays, and camera-based LED detection.

For manual test results, firmware defects, OTA verification, and release assessment, see [REPORT.md](REPORT.md).

## 1. Test Stand Architecture

```text
                      MacBook (pytest)
                             |
             +---------------+----------------+
             |               |                |
         USB Serial       USB Relay          SSH
          FT232R          4 channels          |
             |               |                |
           UART          K1 / K2 / K3 / K4    |
             |               |                |
             +------- ESP32-S3 DUT -----------+
                         |                    |
                     Physical LED             |
                         |                    |
                  Raspberry Pi Camera         |
                         |                    |
                  Raspberry Pi 5 <------------+
                  led_detector.py
```

The MacBook runs the test framework. The Raspberry Pi captures camera images and classifies the DUT's physical LED color. The USB relay simulates physical button presses.

## 2. Hardware

| Component | Purpose |
|---|---|
| ESP32-S3 | SENTRY SWM-2 DUT |
| FT232R USB-UART adapter | DUT console communication |
| CH340-based 4-channel USB relay | Physical button actuation |
| Raspberry Pi 5 | Vision processing |
| Raspberry Pi Camera Module 3 | Physical LED observation |
| MacBook | pytest test runner |

USB relay channel mapping:

| DUT button | Relay channel |
|---|---|
| K1 | CH1 |
| K2 | CH2 |
| K3 | CH3 |
| K4 | CH4 |

The relay contacts simulate button activation. Verify the physical wiring before running HIL tests.

## 3. Project Structure

```text
dz17/
├── drivers/
│   ├── button_controller.py
│   ├── find_ports.py
│   ├── relay_controller.py
│   ├── uart_client.py
│   └── vision_client.py
├── helpers/
│   ├── session_helper.py
│   └── valve_helper.py
├── tests/
│   ├── conftest.py
│   ├── test_bug_cic_01.py
│   ├── test_full_hil.py
│   ├── test_k2_relay_hil.py
│   ├── test_k3_sonar_hil.py
│   ├── test_k4_alert_ack_hil.py
│   ├── test_negative_uart.py
│   ├── test_relay_sequence.py
│   └── test_vision_hil.py
├── vision_hil/
│   └── led_detector.py
├── docs/
├── evidence/
├── firmware/
├── logs/
├── tools/
├── pytest.ini
├── requirements.txt
├── REPORT.md
└── README.md
```

### Main components

| Component | Responsibility |
|---|---|
| [UART client](drivers/uart_client.py) | Sends DUT commands and reads console responses |
| [Port discovery](drivers/find_ports.py) | Finds USB serial devices by VID/PID |
| [Relay controller](drivers/relay_controller.py) | Controls four USB relay channels |
| [Button controller](drivers/button_controller.py) | Simulates short, long, and paired button presses |
| [Vision client](drivers/vision_client.py) | Runs the detector remotely over SSH and retrieves evidence |
| [LED detector](vision_hil/led_detector.py) | Captures camera images and classifies LED color |
| [Session helper](helpers/session_helper.py) | Prepares DUT sessions for authenticated commands |
| [Valve helper](helpers/valve_helper.py) | Provides valve-related test helpers |
| [Pytest fixtures](tests/conftest.py) | Manages hardware resources and failure evidence |

## 4. MacBook Setup

Use a Python environment with the dependencies from [requirements.txt](requirements.txt).

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

The requirements include pytest 9.1.1 and pyserial 3.5.

### USB port discovery

The framework automatically detects supported serial devices:

| Interface | VID | PID | Baud rate |
|---|---|---|---|
| FT232R UART | `0403` | `6001` | 115200 |
| CH340 USB relay | `1A86` | `7523` | 9600 |

The [port discovery module](drivers/find_ports.py) returns an error when no matching device or multiple matching devices are found. UART and relay controllers also accept an explicitly supplied port.

UART uses 8 data bits, no parity, and 1 stop bit (8N1).

## 5. Raspberry Pi Vision Module

The Raspberry Pi runs the operational copy of `led_detector.py` at:

```text
~/vision_hil/led_detector.py
```

The repository includes the [LED Detector source code](vision_hil/led_detector.py), which is deployed and executed on Raspberry Pi 5.

The detector uses:

- `picamera2` for Raspberry Pi camera capture;
- `cv2` (OpenCV) for image processing;
- a 1280 × 720 capture resolution;
- a fixed region of interest (ROI): `(555, 315, 595, 355)`;
- HSV color classification with a minimum threshold of 20 detected pixels.

Possible classification results are `RED`, `GREEN`, and `UNKNOWN`.

Example detector output:

```text
LED_COLOR=GREEN RED_PIXELS=<count> GREEN_PIXELS=<count>
```

Here, `<count>` represents the measured pixel count, not a fixed expected value.

The detector supports two optional arguments:

| Argument | Purpose |
|---|---|
| `--image PATH` | Analyze an existing image |
| `--save PATH` | Save a newly captured image |

### SSH integration

The MacBook's [VisionClient](drivers/vision_client.py) uses the SSH host alias `rpi` and executes:

```bash
ssh rpi 'python3 ~/vision_hil/led_detector.py'
```

SSH access, the Raspberry Pi camera, and the required Pi-side Python packages must be configured before running vision tests.

The Pi-side detector is not installed through the MacBook's `requirements.txt`. Its runtime requires `picamera2` and OpenCV in the Raspberry Pi Python environment.

### Vision evidence

`VisionClient.capture_evidence()` triggers a camera capture on the Pi and copies the resulting PNG into:

```text
evidence/hil/
```

When a test using the `vision` fixture fails during its test call, the pytest hook attempts to capture a timestamped image with the suffix `_FAIL.png`. Evidence capture failures are reported as warnings.

**Calibration limitation:** The ROI is fixed in the current prototype. Moving the camera or DUT may invalidate the ROI and cause vision test failures. Recalibrate and rerun affected tests after physical changes to the stand.

## 6. Physical Button Automation

The [ButtonController](drivers/button_controller.py) exposes:

| Operation | Duration |
|---|---|
| `short_press(button)` | 0.2 s |
| `long_press(button)` | 1.7 s |
| `press_pair(first, second)` | 2.2 s |

The [RelayController](drivers/relay_controller.py) sends four-byte binary commands to the USB relay. It validates channel numbers and attempts to release a channel after a simulated press.

The pytest `relay` fixture also attempts to release channels CH1–CH4 during teardown.

## 7. Automated Tests

The current pytest configuration collects **10 tests**:

| Test group | Coverage |
|---|---|
| [`test_full_hil.py`](tests/test_full_hil.py) | K1, relay, camera, and UART integration |
| [`test_k2_relay_hil.py`](tests/test_k2_relay_hil.py) | K2 relay behavior |
| [`test_k3_sonar_hil.py`](tests/test_k3_sonar_hil.py) | K3 sonar start/stop |
| [`test_k4_alert_ack_hil.py`](tests/test_k4_alert_ack_hil.py) | K4 alert acknowledgment |
| [`test_vision_hil.py`](tests/test_vision_hil.py) | Physical LED color changes |
| [`test_negative_uart.py`](tests/test_negative_uart.py) | Four parameterized negative UART scenarios |
| [`test_bug_cic_01.py`](tests/test_bug_cic_01.py) | Known alert acknowledgment defect |

The [relay sequence script](tests/test_relay_sequence.py) is a diagnostic utility rather than an additional collected pytest test.

### Discover tests without running hardware actions

```bash
python3 -m pytest --collect-only -q
```

### Run the automated suite

Ensure the DUT, UART adapter, USB relay, Raspberry Pi, camera, and SSH connection are ready. Close other applications holding the serial ports before starting.

```bash
python3 -m pytest -v
```

The tests interact with physical hardware. Do not run them against an incorrectly wired or unattended test stand.

### Run one test

```bash
python3 -m pytest -v tests/test_vision_hil.py
```

### Test fixtures

| Fixture | Purpose |
|---|---|
| `relay` | Creates the relay controller and releases channels on teardown |
| `vision` | Provides the Raspberry Pi VisionClient |
| `uart` | Opens and closes UART communication |
| `authenticated_uart` | Prepares an authenticated DUT session |

## 8. Regression Results and Known Defects

The original framework regression established the following baseline:

```text
8 passed, 2 xfailed in 152.47s
```

The two expected failures correspond to documented firmware defects:

- **BUG-RL-01:** Invalid `relay pulse 99` command activates a valve instead of returning the expected error.
- **BUG-CIC-01:** Acknowledgment by alert ID affects the wrong alert.

`XFAIL` means the test encountered a known defect under its expected-failure condition. It does **not** mean that the defect is fixed.

Regression artifacts:

- [Full regression log](logs/full_framework_regression.log)
- [JUnit XML](logs/full_framework_regression.xml)
- [Pytest result screenshot](evidence/hil/full_framework_pytest_v_8pass_2xfail.png)

**Final verification:** After stabilizing the test stand, the camera ROI was recalibrated to
`(555, 315, 595, 355)`. Static RED/GREEN detection and both targeted Vision HIL tests passed.

Two consecutive complete regressions confirmed repeatable results:

| Run | Passed | Xfailed | Failed | Duration |
| --- | ---: | ---: | ---: | --- |
| Final run 1 | 8 | 2 | 0 | 151.59 s |
| Final run 2 | 8 | 2 | 0 | 151.55 s |

Final regression artifacts:

- [Run 1 log](logs/final_framework_regression.log)
- [Run 1 JUnit XML](logs/final_framework_regression.xml)
- [Run 1 screenshot](evidence/hil/final_framework_pytest_8pass_2xfail.png)
- [Run 2 log](logs/final_framework_regression_run2.log)
- [Run 2 JUnit XML](logs/final_framework_regression_run2.xml)
- [Run 2 screenshot](evidence/hil/final_framework_regression_run2.png)

Both `XFAIL` results remain known firmware defects, not successful firmware fixes.

See [REPORT.md](REPORT.md) for detailed manual testing, firmware findings, and the release recommendation.

## 9. Scope and Limitations

This is a focused HIL automation prototype supporting the wider manual Embedded QA investigation, not complete automated coverage of the product requirements.

Current limitations include:

- Fixed camera ROI and color thresholds.
- Dependence on the Raspberry Pi camera and SSH availability.
- Dependence on correct physical relay wiring.
- USB identification by VID/PID, which requires disambiguation when multiple matching devices are attached.
- Automated coverage limited to the currently implemented scenarios.

## 10. Evidence and Documentation

- [REPORT.md](REPORT.md) — testing results, firmware defects, OTA verification, and release assessment.
- [docs/](docs/) — supporting project documentation.
- [evidence/](evidence/) — screenshots and captured evidence.
- [logs/](logs/) — console output and regression logs.
- [firmware/](firmware/) — firmware-related project files.
- [tools/](tools/) — supporting tools.

The automation results complement the manual testing report. Firmware defects, hardware setup issues, and vision calibration failures should be distinguished when evaluating test outcomes.
