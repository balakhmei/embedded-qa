# Smart Greenhouse Controller — Product Requirements Document

## 1. Product Overview

The **Smart Greenhouse Controller** is an IoT-based embedded system designed to monitor environmental conditions inside a greenhouse and automatically control connected equipment.

The system monitors:

* air temperature;
* air humidity;
* soil moisture;
* ambient light level.

Based on sensor measurements, the controller automatically operates:

* a ventilation fan;
* a water pump;
* a grow light.

The main controller is an **ESP32-S3**. Sensor data is periodically collected and processed by the firmware. When predefined thresholds are reached, the corresponding actuator is automatically switched ON or OFF.

The system also provides diagnostic information through a UART serial interface, allowing automated HIL tests to monitor the device state and verify its behavior.

---

## 2. Technical Stack

### Hardware

* **ESP32-S3** — main microcontroller / Device Under Test (DUT)
* **DHT22 (AM2302)** — air temperature and humidity sensor
* **Capacitive Soil Moisture Sensor v1.2** — soil moisture sensor
* **BH1750** — digital ambient light sensor
* **Relay modules** — control of external loads
* **Ventilation fan** — greenhouse cooling
* **Water pump** — irrigation system
* **Grow light** — additional plant lighting
* **USB-UART interface** — communication between the DUT and test host

### Firmware

* ESP32 firmware
* GPIO
* ADC
* I2C
* UART
* sensor and actuator control logic

### Test Automation

* Python 3
* pytest
* pyserial
* HIL test controller
* UART communication
* Wokwi for simulation of a selected key scenario

---

## 3. Functional Requirements

### FR-001 — Air Temperature Monitoring

The system shall periodically measure air temperature using the DHT22 sensor and make the current temperature available through the UART diagnostic interface.

### FR-002 — Air Humidity Monitoring

The system shall periodically measure relative air humidity using the DHT22 sensor and make the current humidity value available through the UART diagnostic interface.

### FR-003 — Soil Moisture Monitoring

The system shall periodically measure the soil moisture level using the capacitive soil moisture sensor and make the current value available through the UART diagnostic interface.

### FR-004 — Ambient Light Monitoring

The system shall periodically measure the ambient light level using the BH1750 sensor and make the current value available through the UART diagnostic interface.

### FR-005 — Automatic Fan Control

The controller shall activate the ventilation fan when the measured air temperature is **30°C or higher**.

The controller shall deactivate the ventilation fan when the temperature falls below the configured threshold.

### FR-006 — Automatic Irrigation Control

The controller shall activate the water pump when the measured soil moisture level is **30% or lower**.

The controller shall deactivate the water pump when the soil moisture level rises above the configured threshold.

### FR-007 — Automatic Grow Light Control

The controller shall activate the grow light when the measured ambient light level is below **500 lux**.

The controller shall deactivate the grow light when the ambient light level is **500 lux or higher**.

### FR-008 — Actuator State Reporting

The system shall provide the current states of the fan, water pump, and grow light through the UART diagnostic interface.

### FR-009 — Sensor Failure Handling

The controller shall detect invalid or unavailable sensor readings and report the corresponding sensor error through the diagnostic interface.

A sensor failure shall not cause uncontrolled activation of an actuator.

### FR-010 — System Startup

After power-on or reboot, the controller shall initialize all sensors and actuator outputs and enter its normal monitoring state.

---

## 4. Non-Functional Requirements

### NFR-001 — Sensor Update Interval

Environmental sensor values shall be updated at least once every **5 seconds** during normal operation.

### NFR-002 — Actuator Response Time

After a monitored parameter crosses its configured threshold, the corresponding actuator state shall be updated within **2 seconds**.

### NFR-003 — UART Availability

The diagnostic UART interface shall operate at **115200 baud, 8 data bits, no parity, and 1 stop bit (115200 8N1)**.

### NFR-004 — Reliability

The controller shall operate continuously for at least **1 hour** without firmware crash, unexpected reboot, or loss of sensor monitoring.

### NFR-005 — Recovery After Reboot

After a software or hardware reboot, the controller shall return to its normal monitoring state within **10 seconds**.

### NFR-006 — Safe Output State

During initialization or when a critical sensor error is detected, the affected actuator shall remain in a defined safe state and shall not switch unpredictably.

---

## 5. Critical Use Cases

### UC-001 — Greenhouse Overtemperature

1. The greenhouse temperature increases.
2. DHT22 reports a temperature of 30°C or higher.
3. ESP32-S3 processes the sensor value.
4. The ventilation fan is activated.
5. The fan state is reported through UART.
6. When the temperature falls below the threshold, the fan is deactivated.

### UC-002 — Dry Soil Irrigation

1. Soil moisture decreases to 30% or lower.
2. The soil moisture sensor reports the low moisture level.
3. ESP32-S3 processes the measurement.
4. The water pump is activated.
5. The pump state is reported through UART.
6. When sufficient soil moisture is restored, the pump is deactivated.

### UC-003 — Low Ambient Light

1. Ambient light falls below 500 lux.
2. BH1750 reports the low light level.
3. ESP32-S3 processes the measurement.
4. The grow light is activated.
5. The grow light state is reported through UART.
6. When ambient light reaches 500 lux or higher, the grow light is deactivated.

### UC-004 — Sensor Failure

1. A sensor stops responding or provides an invalid value.
2. ESP32-S3 detects the invalid sensor state.
3. The controller reports a sensor error through UART.
4. The corresponding actuator remains in its defined safe state.
5. Normal control resumes after valid sensor data becomes available again.

### UC-005 — Device Reboot and Recovery

1. The controller is rebooted.
2. ESP32-S3 initializes the firmware and peripherals.
3. Sensors and actuator outputs are initialized.
4. Actuators remain in their defined safe states during initialization.
5. The system returns to normal monitoring within 10 seconds.
