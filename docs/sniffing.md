# Reverse-engineering the protocol

No register map for the Vitovent 200-C is published (the service manual only lists fault codes and service-menu diagnostics). The map was derived by passively listening to the LB1 ↔ unit traffic.

## 1. Raw capture

Flash [`esphome/vmc-sniffer-debug.yaml`](../esphome/vmc-sniffer-debug.yaml). It configures the UART with a dummy receiver and dumps every burst of bytes as hex:

```
[17:13:54.581][D][uart_debug:113]: <<< 46 03 02 00 00 0C 4B 46 03 00 85 00 02 DA 95
```

Finding the line settings took two attempts, and the symptoms are worth knowing:

- At 19200 the first capture was mostly `FE FA FF` bytes with a regular ~5 s rhythm: data was there, but garbage.
- At 38400 every bit appeared doubled (`66 18 1E 78 E6`), which proves the real speed is half of that, i.e. **19200**.
- Simulating a Modbus frame read with inverted polarity reproduced the `FE FA FF` pattern exactly, so the A/B wires were swapped. After swapping A+/B− on the Waveshare, 396 frames out of 396 passed the CRC check: **19200 baud, 8E1, slave 0x46**.

If you need to search yourself, use the `vmc_baud` / `vmc_parity` substitutions (9600 / 19200 / 38400, EVEN / NONE).

## 2. Controlled sessions

While logging, the panel was used to change one thing at a time. Each session is in [`logs/`](../logs):

| File | Action on the LB1 |
|---|---|
| `2026-10-31-1711-baseline.txt` | nothing (speed 2) |
| `2026-10-31-1714-speed1.txt` | speed 1 |
| `2026-10-31-1723-speed3.txt` | speed 3 |
| `2026-10-31-1741-speed4.txt` | speed 4 |
| `2026-10-31-1742-auto.txt` | switch to automatic mode |
| `2026-10-31-1841-standby.txt` | standby button (captured with `vmc-control.yaml`, which logs every changed register with tag `vmcbus`) |

Values shown on the panel (room temperature, airflow, filter days) were noted at the same time to match registers to readings.

(Wi-Fi SSID, MAC addresses and IPs have been anonymised in the logs.)

## 3. Decoding

[`tools/parse_modbus.py`](../tools/parse_modbus.py) concatenates all `<<<` bytes of a log, splits them into frames by checking the Modbus CRC-16, pairs each request with its response and prints the distinct values seen per register:

```
python3 tools/parse_modbus.py logs/2026-10-31-1714-speed1.txt
FC3 addr 160 (0xA0) n=2: [(50, 50), (70, 70)]
...
WRITE COIL 0x27 = 0xff00
WRITE COIL 0x6 = 0x0
```

Diffing the output between sessions shows which registers follow the speed (`0xA0/0xA1`, `0xDC/0xDD`, `0xDE`, `0x13E/0x13F`) and that the panel **writes** `0x00A2` with FC06 when you press a speed button.

Observations:
- The LB1 polls ~25 blocks of coils (FC01) and holding registers (FC03) every ~5 s, and writes coil `0x27` = ON and coil `0x06` = OFF every cycle.
- Switching to "auto" only writes `0xA2`: the time program is stored in the panel.
- Standby writes `0xA2 = 0xFFFF`; the unit then reports `0xDE = 0xFFFF`, airflow and rpm 0, coils `0x44/0x45` → 0.

## 4. From sniffer to controller

[`vmc-sniffer.yaml`](../esphome/vmc-sniffer.yaml) decodes frames on the ESP32 itself and publishes sensors. [`vmc-control.yaml`](../esphome/vmc-control.yaml) adds a writer that injects `FC06 0x00A2` into the idle gap after a panel cycle (see the README), a `select` and a `fan` entity.

Tip: for ESPHome `delta` filters on integer values use `0.5`, not `1`; a change equal to the delta is rejected.
