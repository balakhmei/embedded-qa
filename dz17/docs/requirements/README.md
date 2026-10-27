# fw_7: SENTRY SWM-2 — Submarine Sonar Watch Module

- `sentry_fw7_v2.1.0_merged.bin` — initial firmware version 2.1.0 (bootloader + partition table + otadata + application), flashed as a single image at address `0x0`.
- `PRD.md` — firmware description and product requirements.
- `HW-17.md` — assignment instructions.
- `tools/` — local OTA server for testing firmware update failure scenarios.

Firmware version 2.3.0 cannot be flashed using esptool; the device downloads and installs it via OTA from https://github.com/BohdanHorbanych/esp32-ota-files (`fw7/`).

## Flashing Instructions

```bash
esptool.py --chip esp32s3 --port <YOUR_PORT> erase-flash
esptool.py --chip esp32s3 --port <YOUR_PORT> -b 460800 write-flash 0x0 sentry_fw7_v2.1.0_merged.bin
```

**The `erase-flash` step is mandatory.** Otherwise, data from previous firmware installations may remain in the NVS and `otadata` partitions.

After flashing, open a serial terminal configured for **115200 baud, 8N1**, and press **RESET**. Verify that the boot log contains `SENTRY SWM-2 ... fw v2.1.0` and `ready. state 1 NORMAL (patrol)`.

Then execute the following commands in order: `help`, `connect`, `register <login> <pass>`, `login <login> <pass>`, `ota check`.

**Serial port examples:** macOS — `/dev/cu.usbserial-*` or `/dev/cu.usbmodem-*`; Windows — `COMx`; Linux — `/dev/ttyUSB*` or `/dev/ttyACM*`.
