# DZ-12 — End-to-End Automation on a HIL Test Stand

## Smart Greenhouse Controller

This project describes an end-to-end Hardware-in-the-Loop (HIL) test
architecture for an IoT Smart Greenhouse Controller based on ESP32-S3.

The system monitors:

- air temperature and humidity
- soil moisture
- ambient light

and automatically controls:

- ventilation fan
- irrigation pump
- grow light

## HIL Test Architecture

The proposed HIL test stand consists of:

- **ESP32-S3** — Device Under Test (DUT)
- **Arduino Mega 2560** — HIL controller for sensor simulation and
  actuator output monitoring
- **Python + pytest + pyserial** — automated test framework running
  on the Test Host

The HIL controller generates simulated sensor conditions for the DUT
and monitors actuator outputs, allowing automated verification of
system behavior.

## Project Contents

- `PRD.md` — product requirements and critical use cases
- `stand_diagram.png` — HIL test stand architecture
- `project_structure.md` — proposed automated test project structure
- `traceability_matrix.md` — requirements-to-tests traceability
- `wokwi_link.md` — Wokwi simulation and test results
- `screenshots/` — screenshots of the Wokwi test scenario

## Wokwi Demonstration

A working Wokwi simulation demonstrates the automatic ventilation
scenario.

Tested behavior:

- **25.1 °C → FAN OFF**
- **30.7 °C → FAN ON**

The ventilation fan is represented by an LED controlled through a relay.

See [`wokwi_link.md`](wokwi_link.md) for the simulation link,
screenshots, and test results.

## Requirements Coverage

The proposed automated HIL tests provide traceability for all
functional and non-functional requirements defined in `PRD.md`.

See [`traceability_matrix.md`](traceability_matrix.md) for the complete
requirements-to-tests mapping.