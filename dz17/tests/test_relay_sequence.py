import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from drivers.relay_controller import RelayController


relay = RelayController()

sequences = [
    [1, 2, 3, 4],
    [1, 4, 2, 3],
]

# Ensure all channels start OFF
for channel in range(1, 5):
    relay.off(channel)

for index, sequence in enumerate(sequences, start=1):
    print(f"\nSequence {index}: {sequence}", flush=True)

    for channel in sequence:
        print(f"CH{channel} ON", flush=True)
        relay.on(channel)
        time.sleep(1)

        print(f"CH{channel} OFF", flush=True)
        relay.off(channel)
        time.sleep(0.5)

print("\nSequence completed.", flush=True)