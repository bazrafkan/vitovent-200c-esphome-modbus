# Viessmann Vitovent 200-C → Home Assistant (ESPHome + Modbus RS485)

Local monitoring **and fan speed control** of a **Viessmann Vitovent 200-C** heat-recovery ventilation unit (VMC / MVHR) from Home Assistant, using a ~20 € ESP32 board and an RS485 transceiver connected **in parallel** to the bus between the unit and its **LB1** wall panel.

No cloud, no ViCare, no gateway, and the original LB1 panel keeps working: changes made on the panel show up in Home Assistant and vice versa.

Viessmann does not publish a Modbus register map for this unit. The map in this repository was reverse-engineered by passively sniffing the LB1 ↔ unit traffic (raw logs included).

> ⚠️ **Disclaimer.** This is an unofficial, community project, not affiliated with Viessmann. Opening the panel and writing to the bus is at your own risk and may affect your warranty. Always power the unit off before wiring. Only tested on one Vitovent 200-C (2026, LB1 panel).

## What you get

| Home Assistant entity | Source |
|---|---|
| `fan.vmc_ventilation` – on/off (off = standby) + 4 speeds | reg `0x00DE` (read), `0x00A2` (write) |
| `select.vmc_fan_speed` – speed 1–4 | same |
| `sensor.vmc_fan_level` | reg `0x00DE` |
| `sensor.vmc_supply_airflow` / `sensor.vmc_exhaust_airflow` (m³/h) | reg `0x00A0` / `0x00A1` |
| `sensor.vmc_supply_fan_speed` / `sensor.vmc_exhaust_fan_speed` (rpm) | reg `0x013E` / `0x013F` |
| `sensor.vmc_room_temperature` (°C) | reg `0x0095` |
| `sensor.vmc_supply_air_temperature` (°C) | reg `0x008D` |
| `sensor.vmc_outdoor_temperature` (°C, likely) | reg `0x0086` |
| `sensor.vmc_filter_days_remaining` | reg `0x00D3` |
| 2 diagnostic registers (`0x00AD`, `0x00B7`, meaning unknown) | |

Plus, in Home Assistant:
- **Cooking boost** – when the induction hob draws power, the unit goes to speed 4 and returns to its previous state 5 minutes after cooking ends.
- **Morning boost** – speed 4 from 08:00 to 09:00, then the previous state is restored.
- All thresholds, times and speeds are helpers editable from a **Ventilation** dashboard (Status / Settings tabs).

## Repository layout

```
esphome/
  vmc-sniffer-debug.yaml   step 1: raw hex dump of the bus (discovery)
  vmc-sniffer.yaml         step 2: read-only decoder → HA sensors
  vmc-control.yaml         step 3: decoder + speed/standby control (current firmware)
  secrets.yaml.example
tools/parse_modbus.py      splits raw hex logs into Modbus frames and lists register values
logs/                      raw sniffing sessions (baseline, speed 1/3/4, auto, standby)
homeassistant/
  packages/vmc.yaml        helpers + both automations as a single HA package
  automations/             the two automations as standalone YAML
  dashboards/ventilation.yaml
docs/
  hardware.md              parts list and wiring
  sniffing.md              how the protocol was reverse-engineered
  register-map.md          Modbus register map
  home-assistant.md        HA integration, automations and dashboard
```

## Quick start

1. **Hardware** – Seeed XIAO ESP32-S3 + Waveshare TTL TO RS485 (C), wired in parallel to the LB1 data pair. See [docs/hardware.md](docs/hardware.md).
2. **Firmware** – in the ESPHome Device Builder create a device, fill `secrets.yaml` from [`esphome/secrets.yaml.example`](esphome/secrets.yaml.example) and flash [`esphome/vmc-control.yaml`](esphome/vmc-control.yaml). If you want to be extra careful, start with the read-only [`vmc-sniffer.yaml`](esphome/vmc-sniffer.yaml): it never transmits.
3. **Home Assistant** – adopt the ESPHome device (API encryption key from your secrets), then add [`homeassistant/packages/vmc.yaml`](homeassistant/packages/vmc.yaml) and the [dashboard](homeassistant/dashboards/ventilation.yaml). See [docs/home-assistant.md](docs/home-assistant.md).

## Bus summary

- Modbus RTU, **19200 baud, 8E1**
- Unit = slave **70 (0x46)**, LB1 panel = master, one polling cycle every **~5 s**
- Speed command: **FC06 write to `0x00A2`**, value `0..3` = speed 1..4, `0xFFFF` = standby
- Current speed: read `0x00DE` (same encoding)

Full details in [docs/register-map.md](docs/register-map.md).

## How control works without removing the panel

Modbus allows only one master. The LB1 stays the master; the ESP32 listens and, only when a new speed is requested from HA, sends a single FC06 write in the ~4 s silent gap after an LB1 cycle (at least 300 ms after the last byte, at most once per cycle, up to 5 attempts). The write is considered done only when the unit reports the new value in `0x00DE`. The LB1 then reads the new level from the unit, so the panel display follows.

## Not (yet) supported

- **Auto mode / time program**: lives inside the LB1 and is not visible on the bus. Use HA automations instead (see the morning boost).
- Room setpoint, bypass min temperature and bypass state were not found in the traffic.
- Meaning of `0x00AD`, `0x00B7`, coils `0x23`, `0x44/0x45` is not fully known. PRs welcome!

## License

MIT – see [LICENSE](LICENSE).
