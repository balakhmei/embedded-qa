# Smart Greenhouse Controller — Traceability Matrix

The following matrix provides traceability between the product requirements
defined in `PRD.md` and the corresponding automated HIL tests.

| Requirement ID | Test File | Test Function |
|---|---|---|
| **FR-001** | `tests/functional/test_sensors.py` | `test_temperature_reading()` |
| **FR-002** | `tests/functional/test_sensors.py` | `test_humidity_reading()` |
| **FR-003** | `tests/functional/test_sensors.py` | `test_soil_moisture_reading()` |
| **FR-004** | `tests/functional/test_sensors.py` | `test_light_level_reading()` |
| **FR-005** | `tests/functional/test_fan_control.py` | `test_fan_activates_at_high_temperature()` |
| **FR-005** | `tests/functional/test_fan_control.py` | `test_fan_deactivates_below_temperature_threshold()` |
| **FR-006** | `tests/functional/test_irrigation.py` | `test_pump_activates_at_low_soil_moisture()` |
| **FR-006** | `tests/functional/test_irrigation.py` | `test_pump_deactivates_when_soil_moisture_restored()` |
| **FR-007** | `tests/functional/test_light_control.py` | `test_grow_light_activates_at_low_light()` |
| **FR-007** | `tests/functional/test_light_control.py` | `test_grow_light_deactivates_at_sufficient_light()` |
| **FR-008** | `tests/functional/test_actuator_status.py` | `test_actuator_states_reported_via_uart()` |
| **FR-009** | `tests/functional/test_sensor_failure.py` | `test_sensor_failure_reports_error()` |
| **FR-009** | `tests/functional/test_sensor_failure.py` | `test_sensor_failure_keeps_actuator_in_safe_state()` |
| **FR-010** | `tests/functional/test_startup.py` | `test_system_initializes_after_startup()` |
| **NFR-001** | `tests/non_functional/test_timing.py` | `test_sensor_update_interval()` |
| **NFR-002** | `tests/non_functional/test_timing.py` | `test_actuator_response_time()` |
| **NFR-003** | `tests/non_functional/test_uart.py` | `test_uart_configuration()` |
| **NFR-004** | `tests/non_functional/test_reliability.py` | `test_one_hour_continuous_operation()` |
| **NFR-005** | `tests/non_functional/test_recovery.py` | `test_recovery_after_reboot()` |
| **NFR-006** | `tests/non_functional/test_recovery.py` | `test_safe_output_state_during_initialization()` |