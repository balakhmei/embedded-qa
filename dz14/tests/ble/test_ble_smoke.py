import asyncio

from bleak import BleakClient, BleakScanner


DEVICE_NAME = "SENTRY-BLE"
LED_UUID = "00001525-1212-efde-1523-785feabcd123"


def test_ble_led_dual_channel(device):
    async def run_test():
        ble_device = await BleakScanner.find_device_by_name(
            DEVICE_NAME,
            timeout=10.0,
        )

        assert ble_device is not None, \
            f"{DEVICE_NAME} was not found"

        async with BleakClient(ble_device) as client:
            assert client.is_connected, \
                f"Failed to connect to {DEVICE_NAME}"

            await client.write_gatt_char(
                LED_UUID,
                b"\x01",
                response=True,
            )

            assert device.wait_for_pattern(
                "LED ON!",
                timeout=5,
            ), "UART did not report LED ON!"

            await client.write_gatt_char(
                LED_UUID,
                b"\x00",
                response=True,
            )

            assert device.wait_for_pattern(
                "LED OFF!",
                timeout=5,
            ), "UART did not report LED OFF!"

    asyncio.run(run_test())