# Home Assistant integration

## 1. ESPHome device

After flashing [`vmc-control.yaml`](../esphome/vmc-control.yaml) the device is discovered by the ESPHome integration (Settings → Devices & services). Enter the API encryption key (`vmc_api_key` from your `secrets.yaml`). Entities are prefixed `vmc_` because the friendly name is `VMC`.

Main entities:

- `fan.vmc_ventilation` – **Ventilation**: 4 speeds = 25 % steps (25/50/75/100 %). Turn off = standby, turn on = last speed.
- `select.vmc_fan_speed` – Fan speed 1–4
- sensors listed in the [README](../README.md#what-you-get)

## 2. Helpers and automations

Copy [`packages/vmc.yaml`](../homeassistant/packages/vmc.yaml) to `<config>/packages/` and enable packages:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Replace `sensor.kitchen_induction_power` with the power sensor of your hob (here a Shelly EM). If you prefer the UI, create the helpers manually and paste the automations from [`automations/`](../homeassistant/automations) into the automation YAML editor.

### Helpers

| Helper | Default | Purpose |
|---|---|---|
| `input_number.vmc_cooking_start_threshold` | 200 W | hob power that starts the boost (a range hood alone draws 107–150 W here, so it must stay below this) |
| `input_number.vmc_cooking_stop_threshold` | 50 W | hob power considered "off" |
| `input_number.vmc_cooking_stop_delay` | 5 min | how long below the stop threshold before restoring |
| `input_number.vmc_cooking_boost_speed` | 4 | speed while cooking |
| `input_datetime.vmc_morning_boost_start` / `_end` | 08:00 / 09:00 | morning boost window |
| `input_number.vmc_morning_boost_speed` | 4 | speed during the morning boost |

### VMC Boost While Cooking

- Hob power **above** the start threshold → snapshot the fan into `scene.vmc_before_cooking` (only if not already boosting) and set the boost speed. There is intentionally no `for:` on this trigger: at low power levels an induction hob pulses on/off (~650 W every 6–18 s).
- Hob power **below** the stop threshold for the stop delay → restore the snapshot and delete the scene.
- `mode: restart`. Note: scenes created with `scene.create` are lost on an HA restart, so a restart during cooking leaves the boost speed on.

### VMC Morning Boost

- At the start time → snapshot into `scene.vmc_before_morning` and set the morning speed.
- At the end time → restore, unless the cooking boost is active (it will restore by itself).

## 3. Dashboard

[`dashboards/ventilation.yaml`](../homeassistant/dashboards/ventilation.yaml) is a sections-based dashboard with two views:

- **Status** – Ventilation tile with fan-speed icon buttons, hob power, airflow, filter days, temperatures, fan rpm, 24 h history graphs, diagnostic registers.
- **Settings** – enable/disable and tune the cooking boost and morning boost helpers.

Create a new dashboard (Settings → Dashboards → Add dashboard → New dashboard from scratch), open the raw configuration editor and paste the file. The `sensor.vmc_power_meter_*`, `update.vmc_power_meter_firmware` and `button.vmc_power_meter_restart` entities come from a separate Shelly meter on the unit's supply; remove those cards if you don't have one.
