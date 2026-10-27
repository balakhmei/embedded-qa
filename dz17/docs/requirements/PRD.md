# PRD: SENTRY SWM-2 — Sonar Watch Module (fw_7)

## 0. Device Overview

**SENTRY SWM-2 (Sonar Watch Module)** is an upgraded module for the forward sonar station of a diesel-electric submarine. The module is installed in sonar compartment No. 2 and performs four functions:

- **Short-range active sonar** — ping/echo contact detection at close range: docking, approaching divers and underwater vehicles, and collision hazards.
- **Perimeter watch** (starting with v2.3.0) — monitors the area around the hull while at anchor or resting on the seabed: unknown contact → INTRUSION → GENERAL ALARM.
- **Actuator control** — ballast/trim valve and signal beacon.
- **Telemetry for the CIC** (Combat Information Center) — module status, depth, hull pressure, water, battery bus, and communications.

Communication with shore and fleet assets is provided through an **antenna buoy** (2.4 GHz Wi-Fi). Firmware is updated over the air (OTA) via the buoy.

The module is used on a training test bench. The laboratory setup is based on an ESP32-S3 DevKit that simulates the module's subsystems:

- HC-SR04 (TRIG 5 / ECHO 18) — **40 kHz hydroacoustic transducer** (active sonar).
- Relay (GPIO8) + LED (GPIO4) — **valve solenoid** and indicator (the actual submarine uses a trim valve).
- Onboard RGB LED (GPIO48) — **signal beacon / module status indicator**.
- K1–K4 buttons (GPIO41, 40, 39, 38) — **watch operator control panel**.
- Depth, pressure, and battery sensors are absent from the test bench. The module uses a **host-platform simulator** (`[NAV] depth sensor offline (lab mode) - using simulator`). Depth, pressure, water, battery, and sea-noise values in the logs are simulated and do not affect the module's logic.

Background telemetry messages (`[NAV]`, `[ACU]`, `[PWR]`, `[HW]`, `[LINK]`), including warnings (`W` without a numeric code, e.g., biologics detected, ripple, thermocline), are informational. They are not module errors or defects.

Commands have functional aliases (the left- and right-hand forms are equivalent):

```text
sonar ...      = distance ...
beacon ...     = lamp ...
valve ...      = relay ...      (valve open = relay on, valve close = relay off)
telemetry ...  = health ...
watch ...      = guard ...      (starting with v2.3.0)
cic ...        = alert ...      (starting with v2.3.0)
```

Log tag mapping: `[SONAR]` — distance sensor; `[VALVE]` — relay (OPEN = on, closed = off); `[BEACON]` — lamp; `[TELEMETRY]` — health; `[WATCH]` — Guard; `[CIC #id ...]` — alerts; `[LINK]` — Wi-Fi; `[AUTH]` — account; `[COLLISION]` — contact closer than 20 cm.

Control interface: UART console at 115200 8N1, command followed by Enter. All messages are written to the log under the `sentry` tag. Error codes use `E<code>` for errors and `W<code>` for warnings.

**This document defines the expected behavior. Any deviation from the behavior specified here is a defect.**

---

## 1. Firmware Versions and OTA Server

- **2.1.0** — stable channel. All functionality except Guard and Alert Center.
- **2.3.0** — beta channel. Adds SENTRY Guard, Alert Center, and the K4 button; includes fixes for defects in 2.1.0.

In 2.1.0, `guard ...`, `alert ...`, and K4 return `E099 ... planned in v2.3.0`. This is expected behavior, not a defect. Every subsequent version must retain all previous functionality and must not perform worse.

Default server (GitHub, HTTPS):

```text
https://raw.githubusercontent.com/BohdanHorbanych/esp32-ota-files/main/fw7/
    stable.txt, beta.txt          - channel version numbers
    v<X.Y.Z>/sentry_fw7.bin       - firmware image
    broken/sentry_fw7.bin         - intentionally broken firmware (rollback testing)
```

An equivalent server can be hosted locally using `tools/ota_server.py` (see `tools/README.md`). Switch the device to that server using `ota server`.

Flash partition layout: NVS at `0x9000` (settings), `otadata` at `0xf000`, `ota_0` at `0x20000`, and `ota_1` at `0x1A0000`, with each OTA partition sized at 1.5 MB.

---

## 2. Access Control and System States

**AC-1. Access levels.** Every command is marked in `help`: no marker — always available; `[wifi]` — requires Wi-Fi (otherwise E002); `[login]` — requires Wi-Fi and login (otherwise E003); `[debug]` — requires debug access (otherwise E004).

**AC-2. Unknown command** — `E001 unknown command '<x>'. Type 'help'`. The first word is case-insensitive. Non-Latin characters are ignored with W006.

**ST-1. System states** (`state`, `state <1-4|name>`, [login]):

- **1 NORMAL (patrol)** — normal watch duty.
- **2 DEBUG (maintenance)** — raw sensor data (without filtering or calibration), parser diagnostics (`[DBG] ...`), and LED blink-code indication.
- **3 VERBOSE (tactical)** — additional logs (`[V] ...`), health reports every 10 s, LED heartbeat, and `Did you mean '<cmd>'?` suggestions for unknown commands.
- **4 EMERGENCY** — emergency surfacing; the module is locked (telemetry depth decreases).

**ST-2. EMERGENCY** can only be entered from 3 VERBOSE. From any other state, return `E302 EMERGENCY can be entered only from 3 VERBOSE (now N NAME)` without changing the state. This rule applies equally to commands and buttons.

**ST-3. In EMERGENCY**, only the following commands are allowed: `help`, `status`, `whoami`, `version`, `health now`, `alert list` (starting with v2.3.0), and `reboot`. Any other command returns E005 / E001 and increases the transducer driver temperature. At 95 °C, an emergency reboot occurs. EMERGENCY can only be exited by reboot (`E304`). Buttons in EMERGENCY return `E005 buttons blocked in EMERGENCY`.

**ST-4.** Re-entering the current state returns `W303 already in N NAME`. `logout` returns DEBUG / VERBOSE to NORMAL. After reboot, the state is always NORMAL.

---

## 3. Wi-Fi

**WF-1. `connect`** (activate the buoy and connect) — scan, list networks, enter SSID (name or number), and enter password. Password shorter than 8 characters: E112; empty SSID: E111. Success: `got ip`, `connected to '<ssid>', rssi N dBm`, Internet connectivity check, and NTP time synchronization. The network is saved in NVS.

**WF-2. Connection errors:** E101 — incorrect password; E102 — network not found; E103 — unsupported encryption; E104 — no IP address (DHCP); E105 — no Internet access; W106 — NTP failed; W107 — weak signal (< -80 dBm); E108 — other cause.

**WF-3.** `reconnect` — connect to the saved network (none saved: E113; already connected: W114). `forget` — erase the saved network. `disconnect` — disconnect (W115 if not connected). There is no automatic connection on startup: boot log contains `known network '<ssid>'. Type 'reconnect'`.

**WF-4.** `scan` — list networks with RSSI. `net` — IP, gateway, DNS, MAC. `ping [host]` — defaults to 8.8.8.8. `time` — current time (E121 if not synchronized).

**WF-5.** On connection loss: `W110 wifi connection lost`, followed by three automatic reconnection attempts.

---

## 4. User Account

**AU-1. `register <login> <pass>`** [wifi] — one profile per device (repeat registration: E202). Login: 3–16 characters, `a-z A-Z 0-9 _` (E204). Password: 6–32 characters (E205). Login `debug` is reserved (E203). The profile is stored in NVS and persists across reboot and OTA.

**AU-2. `login <login> <pass>`** [wifi]. Incorrect credentials: `E209 wrong login or password. Attempts: N/3`. After three failed attempts: `E210 too many attempts, account locked for 30 s`; subsequently `E207 account locked. Try again in N s`. The attempt limit applies to **any** login name entered in the `login` command. Already logged in: E206.

**AU-3. `logout`** — end the session: turn off the lamp and relay, stop measurements, and return DEBUG / VERBOSE to NORMAL. Without an active session: W211.

**AU-4. `whoami`** — `user: <login>, access: user|debug`. The `access` field indicates the current access level (`debug` after successful `sudo`).

**AU-5. `passwd <old> <new>`** [login] — permanently changes the profile password (NVS). The new password works after logout, reboot, and OTA; the old one no longer works. Incorrect old password: E215; new password length 6–32 characters (E205).

**AU-6. `sudo <password>`** [login] — elevate the current user to debug access. Incorrect password: E213; already in debug mode: W212. The sudo password is not provided in this document.

---

## 5. OTA

**OTA-1. `version`** — `SENTRY SWM-2 sonar watch module, fw v<version> (build <date>)`, `partition: ota_N @ <address>, state: valid`. The version must match in `version`, the boot log, and `ota`.

**OTA-2. `ota` / `ota status`** — current firmware and partition, and previous firmware in the other partition.

**OTA-3. `ota check`** — current version, stable and beta versions from the server, and `update available` / `up to date (stable)` / `running newer than stable`.

**OTA-4. `ota update`** — install stable; `ota update beta` — install beta. If that version is already installed, return `[OTA] already up to date`; do not download anything or reboot.

**OTA-5. `ota install <X.Y.Z>`** — install a specific version. Invalid version format: E414; version unavailable on the server: E415. An older version without `force` returns `E408 downgrade blocked: vA -> vB. Use 'ota install B force'` and leaves firmware unchanged. With `force`, downgrading is allowed (as is reinstalling the same version, with W409).

**OTA-6. Update sequence:** `current vA (ota_N) -> target partition ota_M`, `downloading <url>`, `image: sentry_fw7 vB`, progress every 10%, `success: vA -> vB in N s. Rebooting...`. New firmware is written to the inactive partition.

**OTA-7. Self-check.** After reboot: `new firmware, PENDING_VERIFY - self-check...` → `self-check passed, firmware marked VALID`.

**OTA-8. Rollback.** `ota broken` installs intentionally broken firmware. After reboot: `self-check FAILED ... Rolling back...`. The device automatically restores the previous version; `version` reports the previous version with state `valid`. `ota rollback` manually boots firmware from the other partition (not present: E416; invalid: E417).

**OTA-9. Errors:** E401 — update already in progress; E402 — server unavailable; E403 — channel cannot be read; E405 — download did not start; E406 — file is not a firmware image; E407 — firmware belongs to another project; E410 — download interrupted; E411 — no Internet; E412 — corrupted image. After any error, the device remains on the current version and operational, and the next OTA attempt works immediately.

**OTA-10. Data persistence.** After any OTA operation (upgrade / downgrade / rollback), the following must persist: Wi-Fi network, user profile and password, lamp settings and scenes, relay cycle counter and auto mode, sensor calibration / alarm / filter, health settings, and Guard PIN and zone.

**OTA-11. `ota url <url> [force]`** — install an image from an arbitrary HTTP/HTTPS URL (non-HTTP/HTTPS: E418).

**OTA-12. `ota server [<url>|default]`** — show / change the update server. `ota server http://192.168.1.10:8000/fw7/` routes all `ota check / update / install / broken` operations to this server. The server is saved in NVS (boot log: `custom update server: ...`). `ota server default` restores GitHub.

---

## 6. Signal Beacon — Smart Lamp (Onboard RGB LED, K1 Button)

**LM-1. `lamp on|off|toggle`** [login]. Repeated `on` / `off`: W510. After reboot and logout, the lamp is off.

**LM-2. `lamp color <name>`** — white, red, green, blue, yellow, purple, cyan, orange. `lamp color R G B` — each component must be 0–255 (E502). Unknown color: E503.

**LM-3. `lamp brightness <0-100>`** — percentage (E504 outside range).

**LM-4. `lamp mode solid|blink|breathe|rainbow`** (E505). Brightness applies in all modes.

**LM-5. `lamp timer <1-3600>`** — automatic shutdown; `[BEACON] auto-off in N s` (seconds). `lamp timer 0` cancels the timer. Outside range: E506; lamp off: E507. `lamp status` shows `timer N s left`.

**LM-6. `lamp scene save|load <1-3>`** — save / apply color, brightness, and mode (E508 for invalid scene number; E509 for empty scene).

**LM-7. `lamp status`** — `ON|off, color (r,g,b), brightness N%, mode <m>, timer ...`. Color, brightness, mode, and scenes are stored in NVS.

**LM-8. LED.** When the lamp is off, the LED indicates the system state. Priority: EMERGENCY > Guard ALARM > OTA (blinking blue) > sensor error (red for 2 s) > Guard INTRUSION / ARMING > lamp > state indication.

---

## 7. Valve — Relay (GPIO8 + LED GPIO4, K2 Button)

**RL-1. `relay on|off|toggle`** [login]. The LED lights when the relay is on. Repeated `on` / `off`: W601. No more than two switching operations per second (E602).

**RL-2. `relay status`** — state, auto mode, `cycles N`: total number of switching operations (each on or off transition increments the count by 1). The counter is stored in NVS.

**RL-3. `relay pulse <100-10000>`** — switch on for N ms, then switch off. Outside range (including below 100): `E603 pulse must be 100-10000 ms`. Relay already on: E604.

**RL-4. `relay schedule <on> <off>`** — on/off cycle with intervals of 2–3600 s (E606). `relay schedule off` stops the schedule (W605 if not running).

**RL-5. `relay auto on|off`** — activate the relay when the sensor crosses the alarm threshold.

**RL-6. `relay health`** — contact wear (rated life: 100,000 switching operations) and coil status.

**RL-7.** `logout` disables the relay, pulse, and schedule (except during Guard ALARM).

---

## 8. Active Sonar — HC-SR04 (K3 Button)

**DS-1. `distance`** [login] — take one measurement. `distance <N>` — take N measurements (**1–20 inclusive**) and calculate the average. Outside range: E704.

**DS-2. `distance log [100-5000]`** — continuous measurements at the specified interval in milliseconds (E705). `distance stop` stops measurements (W710). While measurements are running, other `distance ...` commands return E711.

**DS-3. `distance calibrate <5-300>`** — place an object at a known distance; firmware calculates the correction (offset). `distance calibrate reset` resets calibration. Errors: E706, E707.

**DS-4. `distance alarm <5-300>|off`** — threshold: `[SONAR] PROXIMITY ALARM: contact at X cm`, `[SONAR] proximity alarm cleared` (5 cm hysteresis). E708.

**DS-5. `distance filter on|off`** — median of five measurements (on by default). `distance stats` — count, errors, min / max / avg. `distance history` — last 10 measurements.

**DS-6.** Object closer than 20 cm: `[COLLISION] contact too close: X cm` (once per approach; triggers again after the object moves beyond 25 cm). No echo: E701; out of range: E702 (LED red for 2 s).

**DS-7. Proximity indicator.** If the valve is open (relay on) and measurements are running, the LED blinks faster as an object approaches; below 10 cm, it stays continuously lit.

---

## 9. Telemetry (Health)

**HL-1.** After Wi-Fi connection and login, automatic report every 30 s (configurable); in VERBOSE every 10 s; in EMERGENCY every 5 s:

```text
[TELEMETRY #N] <time> up <uptime> heap <KB> rssi <dBm> temp <C> depth <m> hull <bar> batt <V> valve open|closed sonar <cm|-> state <STATE> [WARN ...]
```

Starting with 2.3.0, the line also includes `watch <state> alerts <unacknowledged alerts>`. Depth / hull / battery values come from the host-platform simulator.

**HL-2. Warnings:** low heap, weak signal, no Internet, sensor error, overheat, guard alarm (2.3.0).

**HL-3.** `health` — current settings; `health now` — immediate report; `health on|off` (W901); `health interval <10-300>` — **10 and 300 inclusive** (E902 outside range). Settings are stored in NVS.

---

## 10. Perimeter Watch — SENTRY Guard (Starting with v2.3.0, K4 Button)

**GD-1. `guard arm`** — 10-second exit delay (`arming in N s`), then `ARMED`: the sensor monitors the zone. `guard` / `guard status` — state, zone, and last measured distance.

**GD-2.** Object closer than the configured zone (default 50 cm; `guard zone <10-200>`, E808) triggers `INTRUSION`, followed by a 15-second window to enter `guard disarm <pin>`; otherwise, `ALARM`.

**GD-3. ALARM** is also triggered by `guard panic`, holding K4, three incorrect PIN attempts, or three measurements without an echo (tamper). ALARM behavior: CRITICAL alert, relay ON, red/blue LED, and reminder every 10 s.

**GD-4. `guard disarm <pin>`** — disarm / stop ALARM (default PIN: 1234). Incorrect PIN: `E803 wrong PIN. Attempts: N/3`; third incorrect attempt triggers ALARM. The attempt counter **starts at zero** on each `guard arm` and resets after a correct PIN.

**GD-5. `guard pin <old> <new>`** — four digits (E804); only allowed while disarmed (E807). `guard log` — last 10 events. Logout does not disarm Guard.

---

## 11. CIC Alerts — Alert Center (Starting with v2.3.0)

**AL-1.** Last 20 alerts, with INFO / WARNING / CRITICAL severity levels. Sources: watch, sonar, telemetry, state, selftest, test. New alert: `[CIC #id LEVEL] src: text`.

**AL-2. `alert` / `alert list`** — list of alerts; `*` indicates unacknowledged.

**AL-3. `alert ack`** — acknowledge the most recent unacknowledged alert. `alert ack <id>` — acknowledge **the specific alert with that ID** (not found: E851; already acknowledged: W852). `alert ack all` — acknowledge all (W853 if there is nothing to acknowledge).

**AL-4. `alert clear`** — clear the list only after all alerts have been acknowledged (E855). `alert test info|warning|critical` — generate a test alert (E854).

**AL-5.** CRITICAL (except when entering EMERGENCY): relay ON and NORMAL / DEBUG → VERBOSE.

---

## 12. Buttons (Login Required; Otherwise E003)

- **K1:** short press — lamp on/off; hold for 1.5 s — next color.
- **K2:** short press — relay on/off; hold for 1.5 s — 1-second pulse.
- **K3:** short press — measure for 30 s every 500 ms (press again to stop).
- **K4 (2.3.0):** short press — acknowledge latest alert; hold for 1.5 s — PANIC.
- **Hold a button pair for 2 s:** K1+K2 — 1 NORMAL; K2+K3 — 2 DEBUG; K3+K4 — 3 VERBOSE; K4+K1 — 4 EMERGENCY (only from state 3; ST-2).

---

## 13. System

- `help` — command list (grouped, with access markers).
- `status` — firmware, state, Wi-Fi, user, time, relay, Guard (2.3.0), distance, heap.
- `sysinfo` — chip, flash, memory, uptime, temperature. Also `temp`, `uptime`.
- `reboot` — 3-2-1 countdown and restart.
- Boot log — version, partition, and last reset reason (`last reset: power on|software reboot|PANIC|watchdog|brownout`).

The firmware contains hidden commands and capabilities not listed in `help`. Discovering them is part of exploratory testing.
