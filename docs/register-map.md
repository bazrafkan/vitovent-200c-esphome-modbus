# Vitovent 200-C Modbus register map (reverse-engineered)

Bus: Modbus RTU 19200 8E1. Unit = slave **70 (0x46)**, master = LB1 panel, cycle ~5 s.
Temperatures are signed 16-bit ×0.1 °C. `0x8000` = value not available.

| Register | Type | Observed values | Meaning | Status |
|---|---|---|---|---|
| `0x00A2` | holding, written by LB1 (FC06) | 0..3, `0xFFFF` | **Speed command** (0..3 = speed 1..4, `0xFFFF` = standby) | ✔ confirmed (also written by ESP32) |
| `0x00DE` | holding | 0..3, `0xFFFF` | **Current level** (same encoding) | ✔ |
| `0x00A0` / `0x00A1` | holding | 50 / 70 / 115 / 155 for speeds 1–4 | **Supply / exhaust airflow, m³/h** | ✔ (matches LB1 display) |
| `0x00DC` / `0x00DD` | holding | 283/230, 423/351, 542/542, 700/700 | Fan command/target (supply/exhaust)? | ? |
| `0x013E` / `0x013F` | holding | ~880/1150 (v2), ~1105/1077 (v3) | **Actual supply / exhaust fan rpm** | ✔ |
| `0x008D` | holding | 175 → 213 | **Supply air temperature** ×0.1 °C | likely (LB1: 21.5 °C) |
| `0x0086` | holding | 149–162 | **Outdoor temperature** ×0.1 °C | likely (LB1: 15.2 °C) |
| `0x0095` | holding | 219 | **Room (extract) temperature** ×0.1 °C | ✔ (LB1: 21.9 °C) |
| `0x00D3` | holding | 153 | **Days until filter change** | ✔ (LB1: 153) |
| `0x017A` | holding | decreases ~5 per cycle | counter / timer | ? |
| `0x00AD`, `0x00B7`, coil `0x23` | | 16 / 1 / bit 1 briefly, then 0 / 0 / 0 | unknown (not manual/auto) | exposed as diagnostics |
| coils `0x44` / `0x45` | | 1 running, 0 in standby | fans running? | likely |
| coil `0x27` | written ON every cycle by LB1 | | panel heartbeat? | ? |
| coil `0x06` | written OFF every cycle by LB1 | | ? | ? |

Not found on the bus (probably stored in the LB1): room setpoint (20.0 °C), bypass minimum temperature (16.0 °C), bypass state, automatic mode and time program.

Help identifying the unknown registers is very welcome: open an issue with a log and what you did on the panel.
