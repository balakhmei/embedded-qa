# SENTRY SWM-2 — Acceptance Test Report

**Project:** Embedded QA Diploma — HW-17  
**Device:** ESP32-S3 DevKit  
**Firmware:** v2.1.0 (stable), v2.3.0 (beta)  
**Requirements:** `docs/requirements/PRD.md`  
**Status:** Ready for final review — selected-feature testing documented; UART credential redaction and screenshot privacy audit completed; final submission review pending

## 1. Test Environment

- ESP32-S3 DevKit
- HC-SR04 ultrasonic sensor
- Relay and status LEDs
- K1–K4 buttons with USB relay HIL controller
- UART console: 115200 baud
- Wi-Fi 2.4 GHz
- Python / pytest / pyserial

### Scope and Requirements Coverage

Five firmware features were selected for diploma acceptance testing: **OTA, Sonar, Guard, CIC Alert Center, and Relay**. Additional authentication, state, button and lamp checks support the selected scenarios but are not claimed as exhaustively covered features.

| Feature | PRD requirements | Verified scenarios | Known failures / coverage gaps |
|---|---|---|---|
| OTA | OTA-1–OTA-12 | Update, boot validation, manual/automatic rollback, downgrade handling, five negative OTA/recovery scenarios, server restoration | OTA-10 persistence PARTIAL; not every requirement and OTA path exhaustively verified |
| Sonar | DS-1–DS-7 | Reading/count boundaries, log intervals, calibration boundaries, alarm thresholds, statistics/history, no-echo/out-of-range, selected v2.3.0 regression | DS-1 count 20 FAIL; DS-3 documented calibration reset syntax FAIL on both v2.1.0 and v2.3.0; DS-7 not fully verified |
| Guard | GD-1–GD-5 | Arm/readiness, arming delay, intrusion, panic, tamper, PIN handling | GD-4 PIN counter reset FAIL; GD-5 not fully verified |
| CIC Alert Center | AL-1–AL-5 | Alert listing, multiple alerts/FIFO, acknowledgement, clear restrictions and selected regression | AL-3 acknowledgement by ID FAIL; AL-5 not fully verified |
| Relay | RL-1–RL-7 | On/off, physical relay/indicator and pulse lower-bound regression | RL-3 pulse 99 FAIL; remaining RL requirements not exhaustively verified |

**Coverage interpretation:** PASS and FAIL apply only to the specific scenarios documented below. Unexecuted or incompletely checked requirements remain NOT TESTED or PARTIAL; this report does not claim 100% PRD coverage.

## 2. Acceptance Test Checklist

### 2.1 Firmware v2.1.0

| Test ID | PRD | Test scenario | Result | Evidence |
|---|---|---|---|---|
| TC-AC-001 | AC-1 | Relay command without Wi-Fi → E002 | PASS | [`logs/uart_fw_2_1_0_negative.log`](logs/uart_fw_2_1_0_negative.log) |
| TC-AC-002 | AC-1 | Relay command without login → E003 | PASS | [`evidence/fw_2_1_0_negative_unauthorized_relay.png`](evidence/fw_2_1_0_negative_unauthorized_relay.png) |
| TC-AC-003 | AC-2 | Unknown command → E001 | PASS | [`logs/uart_fw_2_1_0_negative.log`](logs/uart_fw_2_1_0_negative.log) |
| TC-AU-001 | AU-2 | Invalid password → E209 | PASS | [`evidence/fw_2_1_0_negative_invalid_password.png`](evidence/fw_2_1_0_negative_invalid_password.png) |
| TC-AU-002 | AU-2 | Three failed attempts → E210 | PASS | [`evidence/fw_2_1_0_negative_login_lockout.png`](evidence/fw_2_1_0_negative_login_lockout.png) |
| TC-AU-003 | AU-2 | Successful login after lockout period | PASS | [`logs/uart_fw_2_1_0_negative.log`](logs/uart_fw_2_1_0_negative.log) |
| TC-ST-001 | ST-1 | Invalid state 5 → E301; state remains NORMAL | PASS | [`logs/uart_fw_2_1_0_negative.log`](logs/uart_fw_2_1_0_negative.log) |
| TC-OTA-001 | Versioning | Firmware v2.1.0 boot in NORMAL | PASS | [`evidence/fw_2_1_0_boot_normal.png`](evidence/fw_2_1_0_boot_normal.png) |
| TC-BTN-001 | PRD §1, §12 | K4 short press on v2.1.0 → E099 | PASS | [`logs/uart_fw_2_1_0.log`](logs/uart_fw_2_1_0.log) |
| TC-BTN-002 | PRD §12 | K1 short press: lamp OFF → ON → OFF | PASS | [`evidence/fw_2_1_0_hil_k1_lamp_on.png`](evidence/fw_2_1_0_hil_k1_lamp_on.png) |
| TC-BTN-003 | PRD §12 | K1 long press (≥1.5 s): next lamp color | PASS | [`evidence/fw_2_1_0_hil_k1_long_press.png`](evidence/fw_2_1_0_hil_k1_long_press.png) |
| TC-BTN-004 | PRD §12 | K2 short press: valve CLOSED → OPEN → CLOSED | PASS | [`evidence/fw_2_1_0_hil_k2_valve_toggle.png`](evidence/fw_2_1_0_hil_k2_valve_toggle.png) |
| TC-BTN-005 | PRD §12 | K2 long press (≥1.5 s): 1-second valve pulse | PASS | [`logs/uart_fw_2_1_0.log`](logs/uart_fw_2_1_0.log) |
| TC-BTN-006 | PRD §12 | K3 short press: start 30-second sonar session | PASS | [`evidence/fw_2_1_0_hil_k3_sonar_30s.png`](evidence/fw_2_1_0_hil_k3_sonar_30s.png) |
| TC-ST-002 | ST-1, §12 | K2+K3 hold: NORMAL → DEBUG | PASS | [`evidence/fw_2_1_0_hil_k2_k3_debug.png`](evidence/fw_2_1_0_hil_k2_k3_debug.png) |
| TC-ST-003 | ST-1, §12 | K3+K4 hold: DEBUG → VERBOSE | PASS | [`evidence/fw_2_1_0_hil_k3_k4_verbose.png`](evidence/fw_2_1_0_hil_k3_k4_verbose.png) |
| TC-ST-004 | ST-2, §12 | K4+K1 hold from VERBOSE → EMERGENCY | PASS | [`evidence/fw_2_1_0_hil_k4_k1_emergency.png`](evidence/fw_2_1_0_hil_k4_k1_emergency.png) |
| TC-ST-005 | ST-4 | Reboot restores NORMAL state | PASS | [`logs/uart_fw_2_1_0.log`](logs/uart_fw_2_1_0.log) |
| TC-DS-001 | DS-5 | Sonar statistics: count, errors, min/max/avg | PASS | [`evidence/fw_2_1_0_sonar_statistics.png`](evidence/fw_2_1_0_sonar_statistics.png) |
| TC-DS-002 | DS-6 | Sonar reports E701 (no echo) and E702 (out of range) | PASS | [`logs/uart_fw_2_1_0.log`](logs/uart_fw_2_1_0.log) |
| TC-DS-003 | DS-1 | `distance 1` and `distance 19` accepted | PASS | [`logs/uart_fw_2_1_0_boundaries.log`](logs/uart_fw_2_1_0_boundaries.log) |
| TC-DS-004 | DS-1 | `distance 20` accepted (upper boundary) | FAIL — BUG-SONAR-01 | [`evidence/BUG-SONAR-01_distance_20_rejected.png`](evidence/BUG-SONAR-01_distance_20_rejected.png) |
| TC-DS-005 | DS-1 | `distance 0` and `distance 21` rejected with E704 | PASS | [`logs/uart_fw_2_1_0_boundaries.log`](logs/uart_fw_2_1_0_boundaries.log) |
| TC-DS-006 | DS-2 | `distance log` intervals 100, 1000, 5000 ms | PASS | [`logs/uart_fw_2_1_0_sonar.log`](logs/uart_fw_2_1_0_sonar.log) |
| TC-DS-007 | DS-2 | Log intervals 99 and 5001 ms rejected with E705 | PASS | [`logs/uart_fw_2_1_0_sonar.log`](logs/uart_fw_2_1_0_sonar.log) |
| TC-DS-008 | DS-3 | Calibration at 5 and 300 cm accepted; 4 and 301 rejected | PASS | [`logs/uart_fw_2_1_0_sonar.log`](logs/uart_fw_2_1_0_sonar.log) |
| TC-DS-009 | DS-3 | `distance calibrate reset` | FAIL — BUG-SONAR-02 (v2.1.0) | [`evidence/BUG-SONAR-02_calibration_reset_rejected.png`](evidence/BUG-SONAR-02_calibration_reset_rejected.png) |
| TC-DS-010 | DS-4 | Alarm thresholds 5 and 300 accepted; 4 and 301 rejected | PASS | [`logs/uart_fw_2_1_0_sonar.log`](logs/uart_fw_2_1_0_sonar.log) |
| TC-DS-011 | DS-5 | Filter, statistics and history operations | PASS (tested scenarios) | [`logs/uart_fw_2_1_0_sonar.log`](logs/uart_fw_2_1_0_sonar.log) |
| TC-GD-001 | GD-1–GD-3 | Guard/Alert commands unavailable on v2.1.0 | EXPECTED / NOT A BUG | PRD §1 |
| TC-BTN-007 | §12 | Other button combinations, including K1+K2 | NOT FULLY VERIFIED | — |
| TC-HL-001 | HL-3 | Health interval 10/300 and 9/301 boundary checks | NOT VERIFIED | — |
| TC-OTA-010 | OTA-10 | All listed NVS settings retained across each OTA path | PARTIAL / NOT FULLY VERIFIED | [`logs/uart_fw_2_1_0_ota.log`](logs/uart_fw_2_1_0_ota.log) |

The checklist records verified scenarios, not exhaustive PRD coverage. Unlisted boundary or persistence cases are **NOT TESTED / NOT VERIFIED** unless independently evidenced.

### 2.2 Firmware v2.3.0

| Test ID | PRD | Test scenario | Result | Evidence |
|---|---|---|---|---|
| TC-REG-LM-01 | LM-1–LM-4 | Lamp on/off, red color, brightness 20%, blink/solid; physical LED | PASS (tested scenarios) | [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) |
| TC-REG-RL-01 | RL-1 | Relay on/off; physical relay and indicator | PASS | [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) |
| TC-REG-RL-02 | RL-3 | `relay pulse 99` must return E603 and not activate relay | FAIL — BUG-RL-01 | [`evidence/REG_BUG-RL-01_pulse_99_v2.3.0.png`](evidence/REG_BUG-RL-01_pulse_99_v2.3.0.png) |
| TC-REG-DS-01 | DS-1 | Single sonar reading with target and no-echo handling | PASS (tested scenarios) | [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) |
| TC-REG-DS-02 | DS-1 | Boundary values: `distance 19` accepted (19/19), `distance 20` rejected (E704), `distance 21` rejected (E704) | FAIL — BUG-SONAR-01 (`20`); PASS (`19`, `21`) | [`evidence/fw_2_3_0_sonar_boundary_19_20_21.png`](evidence/fw_2_3_0_sonar_boundary_19_20_21.png), [`evidence/fw_2_3_0_sonar_distance_20_retest.png`](evidence/fw_2_3_0_sonar_distance_20_retest.png), [`logs/uart_fw_2_3_0_sonar_regression.log`](logs/uart_fw_2_3_0_sonar_regression.log) |
| TC-REG-DS-03 | DS-3, DS-5 | `distance reset`, statistics | PASS (tested commands only) | [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) |
| TC-REG-DS-04 | DS-3 | Exact `distance calibrate reset` syntax rejected with E706; alternative `distance reset` accepted | FAIL — BUG-SONAR-02 (documented syntax); workaround PASS | [`evidence/fw_2_3_0_sonar_calibrate_reset.png`](evidence/fw_2_3_0_sonar_calibrate_reset.png), [`logs/uart_fw_2_3_0_sonar_regression.log`](logs/uart_fw_2_3_0_sonar_regression.log) |
| TC-GD-001 | GD-1 | Guard arm with ready sensor; 10-second arming delay | PASS | [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) |
| TC-GD-002 | GD-1 | Guard arm without valid sonar reading blocked | PASS | [`evidence/GUARD-03_arm_sensor_not_ready_E805.png`](evidence/GUARD-03_arm_sensor_not_ready_E805.png) |
| TC-GD-003 | GD-3 | Intrusion, timeout, panic and sonar tamper alarm paths | PASS (documented scenarios) | [`evidence/GD-02_intrusion_timeout_alarm_PASS.png`](evidence/GD-02_intrusion_timeout_alarm_PASS.png), [`evidence/GD-03_K4_long_press_panic_PASS.png`](evidence/GD-03_K4_long_press_panic_PASS.png), [`evidence/GD-03_sonar_tamper_3_failures_PASS.png`](evidence/GD-03_sonar_tamper_3_failures_PASS.png) |
| TC-GD-004 | GD-4 | Correct PIN disarms; wrong-PIN counter resets | FAIL — BUG-GUARD-01 | [`evidence/REG_BUG-GUARD-01_PIN_counter_v2.3.0.png`](evidence/REG_BUG-GUARD-01_PIN_counter_v2.3.0.png) |
| TC-AL-001 | AL-1–AL-2 | Alert list, unacknowledged markers, multiple alerts | PASS (tested scenarios) | [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) |
| TC-AL-002 | AL-3 | `alert ack 4` acknowledges ID 4 specifically | FAIL — BUG-CIC-01 | [`evidence/REG_BUG-CIC-01_wrong_alert_ack_v2.3.0.png`](evidence/REG_BUG-CIC-01_wrong_alert_ack_v2.3.0.png) |
| TC-AL-003 | AL-3–AL-4 | `alert ack all`; reject clear with unacknowledged alerts; clear after ack | PASS | [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) |
| TC-SYS-001 | §13 | Final status v2.3.0, NORMAL, valve CLOSED, Guard DISARMED, no unacked alerts | PASS | [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) |
| TC-REG-FULL | §2–§13 | Exhaustive repeat of every v2.1.0 boundary and persistence test | NOT COMPLETED | — |

**Regression scope:** targeted physical and UART checks were completed for Lamp, Relay, Sonar, Guard and CIC. This is **not** evidence of exhaustive regression for Wi-Fi, account, telemetry, all button combinations or all NVS settings.

## 3. OTA Test Results

| Test ID | PRD | Scenario | Result | Evidence |
|---|---|---|---|---|
| OTA-01 | OTA-4, OTA-6, OTA-7 | v2.1.0 → v2.3.0 beta; new image boots and self-check succeeds | PASS | [`evidence/OTA-01_v2.3.0_boot_after_update.png`](evidence/OTA-01_v2.3.0_boot_after_update.png), [`evidence/OTA-02_partition_status_after_update.png`](evidence/OTA-02_partition_status_after_update.png) |
| OTA-02 | OTA-8 | Manual rollback v2.3.0 → v2.1.0 | PASS | [`evidence/OTA-03_rollback_v2.3.0_to_v2.1.0.png`](evidence/OTA-03_rollback_v2.3.0_to_v2.1.0.png), [`evidence/OTA-04_rollback_partition_status.png`](evidence/OTA-04_rollback_partition_status.png) |
| OTA-03 | OTA-8 | Broken firmware image triggers automatic rollback | PASS | [`evidence/OTA-05_broken_firmware_auto_rollback.png`](evidence/OTA-05_broken_firmware_auto_rollback.png), [`evidence/OTA-06_auto_rollback_partition_status.png`](evidence/OTA-06_auto_rollback_partition_status.png) |
| OTA-04 | OTA-5 | Downgrade without `force` blocked | PASS | [`evidence/OTA-07_downgrade_without_force.png`](evidence/OTA-07_downgrade_without_force.png) |
| OTA-05 | OTA-5 | Forced downgrade permitted | PASS | [`evidence/OTA-08_forced_downgrade_success.png`](evidence/OTA-08_forced_downgrade_success.png) |
| OTA-NEG-01 | OTA-9 | Garbage image rejected with E406 | PASS | [`evidence/OTA_NEG_01_garbage_firmware_rejected.png`](evidence/OTA_NEG_01_garbage_firmware_rejected.png) |
| OTA-NEG-02 | OTA-9 | Truncated image rejected with E412; recovery OTA succeeds | PASS | [`evidence/OTA_NEG_02_truncated_firmware_rejected.png`](evidence/OTA_NEG_02_truncated_firmware_rejected.png), [`evidence/OTA_NEG_02_recovery_valid_ota_PASS.png`](evidence/OTA_NEG_02_recovery_valid_ota_PASS.png) |
| OTA-NEG-03 | OTA-9 | Corrupted image rejected with E412; recovery OTA succeeds | PASS | [`evidence/OTA_NEG_03_corrupted_firmware_rejected_PASS.png`](evidence/OTA_NEG_03_corrupted_firmware_rejected_PASS.png), [`evidence/OTA_NEG_03_recovery_valid_ota_PASS.png`](evidence/OTA_NEG_03_recovery_valid_ota_PASS.png) |
| OTA-NEG-04 | OTA-9 | Local server interrupts download (`--drop-at`); E410; recovery succeeds | PASS | [`logs/uart_ota_negative_v2_3_0.log`](logs/uart_ota_negative_v2_3_0.log), [`evidence/OTA_NEG_04_recovery_valid_ota_PASS.png`](evidence/OTA_NEG_04_recovery_valid_ota_PASS.png) |
| OTA-NEG-05 | OTA-9 | Wi-Fi lost during slow OTA; W110/E410; recovery succeeds | PASS | [`evidence/OTA_NEG_05_wifi_loss_E410_PASS.png`](evidence/OTA_NEG_05_wifi_loss_E410_PASS.png), [`evidence/OTA_NEG_05_recovery_valid_ota_PASS.png`](evidence/OTA_NEG_05_recovery_valid_ota_PASS.png) |
| OTA-10 | OTA-10 | Persistence of **every** specified setting across up/down/rollback | PARTIAL / NOT FULLY VERIFIED | — |
| OTA-SERVER | OTA-12 | Restore default GitHub update server after local tests | PASS | [`logs/uart_ota_negative_v2_3_0.log`](logs/uart_ota_negative_v2_3_0.log) |

OTA execution logs: [`logs/uart_fw_2_1_0_ota.log`](logs/uart_fw_2_1_0_ota.log), [`logs/uart_ota_v2_1_0_to_v2_3_0_guard_cic_regression.log`](logs/uart_ota_v2_1_0_to_v2_3_0_guard_cic_regression.log), [`logs/uart_ota_negative_v2_3_0.log`](logs/uart_ota_negative_v2_3_0.log). Final running image: v2.3.0, partition `ota_1`, VALID.

## 4. Bug Reports

Severity and priority below are QA assessments; no fixed numeric reproduction count is claimed where the exact number was not recorded.

### BUG-RL-01 — Relay pulse below minimum is executed
- **Versions:** observed on v2.3.0; v2.1.0 status not confirmed.
- **PRD:** RL-3. **Severity:** Medium. **Priority:** High.
- **Preconditions:** authenticated session; relay initially OFF.
- **Steps:** run `relay pulse 99`; observe UART and physical relay.
- **Expected:** `E603 pulse must be 100-10000 ms`; no activation.
- **Actual:** `[VALVE] OPEN (pulse)` followed by `[VALVE] CLOSED (pulse end)`; relay physically switched.
- **Reproducibility:** reproduced during v2.3.0 regression; exact trial count not recorded.
- **Evidence:** [`evidence/REG_BUG-RL-01_pulse_99_v2.3.0.png`](evidence/REG_BUG-RL-01_pulse_99_v2.3.0.png); [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) lines 75–76.

### BUG-SONAR-01 — Maximum valid measurement count rejected
- **Versions:** observed on v2.1.0 and reproduced on v2.3.0.
- **PRD:** DS-1. **Severity:** Medium. **Priority:** High.
- **Preconditions:** authenticated session, sonar ready.
- **Steps:** run `distance 19`, `distance 20`, `distance 21`.
- **Expected:** counts 19 and 20 accepted; count 21 rejected with E704.
- **Actual:** 19/19 measurements succeeded; `distance 20` incorrectly returned E704; `distance 21` correctly returned E704.
- **Reproducibility:** confirmed on both versions; exact trial count not recorded.
- **Evidence:** [`evidence/BUG-SONAR-01_distance_20_rejected.png`](evidence/BUG-SONAR-01_distance_20_rejected.png), [`evidence/REG_BUG-SONAR-01_count_20_v2.3.0.png`](evidence/REG_BUG-SONAR-01_count_20_v2.3.0.png), [`evidence/fw_2_3_0_sonar_boundary_19_20_21.png`](evidence/fw_2_3_0_sonar_boundary_19_20_21.png), [`evidence/fw_2_3_0_sonar_distance_20_retest.png`](evidence/fw_2_3_0_sonar_distance_20_retest.png); [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) line 112; [`logs/uart_fw_2_3_0_sonar_regression.log`](logs/uart_fw_2_3_0_sonar_regression.log).

### BUG-SONAR-02 — Calibration reset syntax rejected
- **Versions:** observed on v2.1.0 and reproduced on v2.3.0.
- **PRD:** DS-3. **Severity:** Medium (provisional). **Priority:** Medium (provisional).
- **Preconditions:** authenticated session, sonar available.
- **Steps:** run `distance calibrate reset` (exact PRD syntax).
- **Expected:** stored calibration offset reset.
- **Actual:** `distance calibrate reset` returned E706 on both v2.1.0 and v2.3.0. On v2.3.0, `distance reset` successfully reset calibration as an alternative command.
- **Reproducibility:** confirmed on both versions; exact trial count not recorded.
- **Evidence:** [`evidence/BUG-SONAR-02_calibration_reset_rejected.png`](evidence/BUG-SONAR-02_calibration_reset_rejected.png), [`evidence/fw_2_3_0_sonar_calibrate_reset.png`](evidence/fw_2_3_0_sonar_calibrate_reset.png); [`logs/uart_fw_2_1_0_sonar.log`](logs/uart_fw_2_1_0_sonar.log), [`logs/uart_fw_2_3_0_sonar_regression.log`](logs/uart_fw_2_3_0_sonar_regression.log).
- **Workaround:** use `distance reset` on v2.3.0. The documented `distance calibrate reset` syntax remains defective.

### BUG-GUARD-01 — Wrong PIN counter not reset after valid PIN
- **Versions:** feature introduced in v2.3.0; reproduced on v2.3.0.
- **PRD:** GD-4. **Severity:** High. **Priority:** High.
- **Preconditions:** authenticated user, ready sonar, Guard can be armed.
- **Steps:** arm; enter wrong PIN twice; successfully disarm with correct PIN; rearm; enter one wrong PIN.
- **Expected:** counter reset after successful PIN and on each arm; first new error `Attempts: 1/3`.
- **Actual:** first wrong PIN after rearming reports `Attempts: 3/3`, triggers GENERAL ALARM, CRITICAL alert and valve activation.
- **Reproducibility:** reproduced during testing and regression; exact trial count not recorded.
- **Evidence:** [`evidence/BUG-GUARD-01_pin_counter_reproduced.png`](evidence/BUG-GUARD-01_pin_counter_reproduced.png), [`evidence/REG_BUG-GUARD-01_PIN_counter_v2.3.0.png`](evidence/REG_BUG-GUARD-01_PIN_counter_v2.3.0.png); [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) lines 227–228.

### BUG-CIC-01 — Acknowledgement by ID targets wrong alert
- **Versions:** feature introduced in v2.3.0; reproduced on v2.3.0.
- **PRD:** AL-3. **Severity:** High. **Priority:** High.
- **Preconditions:** multiple alerts present, IDs 3 and 4 distinguishable, both unacknowledged.
- **Steps:** inspect `alert list`; run `alert ack 4`; inspect `alert list` again.
- **Expected:** ID 4 acknowledged; ID 3 unchanged.
- **Actual:** UART reports `#4 acknowledged`, but ID 3 loses its `*` marker while ID 4 remains unacknowledged.
- **Reproducibility:** observed in several CIC test conditions and v2.3.0 regression; exact trial count not recorded.
- **Evidence:** [`evidence/BUG-CIC-01_ack_id_mismatch.png`](evidence/BUG-CIC-01_ack_id_mismatch.png), [`evidence/REG_BUG-CIC-01_wrong_alert_ack_v2.3.0.png`](evidence/REG_BUG-CIC-01_wrong_alert_ack_v2.3.0.png); [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log) around line 357.

**Classification:** BUG-SONAR-01 persists across versions (not a newly introduced regression). BUG-GUARD-01 and BUG-CIC-01 concern functionality new in v2.3.0. BUG-RL-01 is confirmed on v2.3.0 but cannot be classified as newly introduced without v2.1.0 comparison.

## 5. Bug Matrix

| Bug | v2.1.0 | v2.3.0 | Classification |
|---|---|---|---|
| BUG-RL-01 | NOT VERIFIED | FAIL | Confirmed v2.3.0; origin unknown |
| BUG-SONAR-01 | FAIL | FAIL | Persistent defect |
| BUG-SONAR-02 | FAIL | FAIL | Persistent defect (documented syntax); v2.3.0 workaround available |
| BUG-GUARD-01 | N/A — Guard unavailable | FAIL | New-feature defect |
| BUG-CIC-01 | N/A — CIC unavailable | FAIL | New-feature defect |

**No defect is labelled “fixed and reintroduced” without evidence of a previously passing version.**

## 6. Security Findings

- Authentication and authorization negative tests on v2.1.0 returned the expected E002/E003/E209/E210 errors (see §2.1). These are **PASS** checks, not security vulnerabilities.
- Incorrect Guard PIN attempt accounting can trigger an unintended alarm and relay activation; tracked as **BUG-GUARD-01**.
- CIC acknowledgement mismatch may mislead an operator into believing a specific alert has been acknowledged; tracked as **BUG-CIC-01**.
- Hidden commands / privilege escalation: **NOT TESTED / no verified finding reported**. No vulnerability claim is made without evidence.
- **Submission hygiene:** redact Wi-Fi passwords, account credentials, tokens and personal identifiers in UART logs/screenshots before packaging.

## 7. Final QA Assessment

**Recommendation: NO-GO for promoting v2.3.0 beta to stable at this stage.**

**Reasons:** (1) BUG-GUARD-01 can cause a false GENERAL ALARM and activate the valve after a previously successful disarm; (2) BUG-CIC-01 acknowledges the wrong alert despite reporting success; (3) relay pulse boundary validation and sonar upper-boundary handling do not meet PRD; (4) full OTA-10 persistence and exhaustive regression are not verified.

**What passed:** firmware update and self-check, manual/automatic rollback, forced downgrade, five OTA fault/recovery scenarios, core Lamp/Relay/Sonar functions, and selected Guard/CIC scenarios.

**Release conditions:** fix and retest the high-severity Guard and CIC issues, resolve or explicitly accept the other defects, verify OTA-10 data persistence and complete critical-path regression. Repeat the affected tests on the proposed release candidate.

**Last observed device state:** v2.3.0 on `ota_1`, NORMAL, valve CLOSED, Guard DISARMED, CIC unacknowledged alerts = 0.

## 8. Evidence and Logs

### UART logs
- [`logs/uart_fw_2_1_0.log`](logs/uart_fw_2_1_0.log)
- [`logs/uart_fw_2_1_0_negative.log`](logs/uart_fw_2_1_0_negative.log)
- [`logs/uart_fw_2_1_0_boundaries.log`](logs/uart_fw_2_1_0_boundaries.log)
- [`logs/uart_fw_2_1_0_sonar.log`](logs/uart_fw_2_1_0_sonar.log)
- [`logs/uart_fw_2_3_0_sonar_regression.log`](logs/uart_fw_2_3_0_sonar_regression.log)
- [`logs/uart_fw_2_1_0_ota.log`](logs/uart_fw_2_1_0_ota.log)
- [`logs/uart_ota_v2_1_0_to_v2_3_0_guard_cic_regression.log`](logs/uart_ota_v2_1_0_to_v2_3_0_guard_cic_regression.log)
- [`logs/uart_ota_negative_v2_3_0.log`](logs/uart_ota_negative_v2_3_0.log)
- [`logs/uart_regression_v2_3_0.log`](logs/uart_regression_v2_3_0.log)

### Screenshots
- `evidence/` — firmware v2.1.0 functional/HIL, negative, sonar and Guard/CIC screenshots; OTA and fault-injection evidence; four v2.3.0 regression bug screenshots. Exact filenames are referenced in tables and bug reports.

### Additional Screenshots

**OTA and recovery**
- [`OTA_NEG_02_recovery_status_PASS.png`](evidence/OTA_NEG_02_recovery_status_PASS.png)
- [`OTA_NEG_03_recovery_status_PASS.png`](evidence/OTA_NEG_03_recovery_status_PASS.png)
- [`OTA_NEG_05_recovery_status_PASS.png`](evidence/OTA_NEG_05_recovery_status_PASS.png)
- [`fw_2_1_0_wifi_connection.png`](evidence/fw_2_1_0_wifi_connection.png)

**Guard**
- [`BUG-GUARD-01_pin_counter_not_reset.png`](evidence/BUG-GUARD-01_pin_counter_not_reset.png)
- [`GUARD-01_intrusion_general_alarm.png`](evidence/GUARD-01_intrusion_general_alarm.png)
- [`GUARD-02_zone_above_maximum.png`](evidence/GUARD-02_zone_above_maximum.png)
- [`GUARD-04_arm_sonar_E701_E702.png`](evidence/GUARD-04_arm_sonar_E701_E702.png)
- [`GUARD-05_wrong_pin_three_attempts_alarm.png`](evidence/GUARD-05_wrong_pin_three_attempts_alarm.png)

**Sonar**
- [`SONAR-03_five_consecutive_measurement_errors.png`](evidence/SONAR-03_five_consecutive_measurement_errors.png)

**CIC Alert Center**
- [`BUG-CIC-01_ack_after_fifo_overflow.png`](evidence/BUG-CIC-01_ack_after_fifo_overflow.png)
- [`BUG-CIC-01_ack_id13_after_fifo.png`](evidence/BUG-CIC-01_ack_id13_after_fifo.png)
- [`BUG-CIC-01_ack_status_after_two_ids.png`](evidence/BUG-CIC-01_ack_status_after_two_ids.png)
- [`BUG-CIC-01_ack_without_id_status.png`](evidence/BUG-CIC-01_ack_without_id_status.png)
- [`BUG-CIC-01_oldest_alert_ack_E851.png`](evidence/BUG-CIC-01_oldest_alert_ack_E851.png)
- [`CIC_AL1_FIFO_20_alerts_PASS.png`](evidence/CIC_AL1_FIFO_20_alerts_PASS.png)

### Automation
- `drivers/relay_controller.py`
- `tests/test_relay_sequence.py`

**Evidence limitations:** screenshot and log filenames were confirmed in the project file listing, but their full contents have not all been independently audited against every report claim. Reproduction counts are intentionally not fabricated.

**Submission checklist:** redact credentials and sensitive identifiers; confirm that each referenced file is included; verify logs for every bug and OTA transition; complete any outstanding critical tests; package the report and `logs/` as specified in HW-17. Do not mark a test PASS solely because a file exists.
