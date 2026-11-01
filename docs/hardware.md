# Hardware and wiring

## Parts

| Part | Notes |
|---|---|
| Seeed Studio **XIAO ESP32-S3** | any ESP32 works; pins below are for the XIAO |
| **Waveshare TTL TO RS485 (C)** | 3.3 V compatible, automatic direction control, screw terminals |
| USB-C 5 V power supply | powers the XIAO |
| Short twisted pair | from the LB1 terminals to the RS485 module |
| Multimeter, small screwdriver | |

Any 3.3 V RS485 transceiver with automatic direction control (or a MAX3485 with DE/RE driven by a GPIO) should work.

## TTL side: RS485 module ↔ XIAO

| Waveshare (C) | XIAO ESP32-S3 |
|---|---|
| VCC | 3V3 |
| GND | GND |
| TXD | D7 (GPIO44, RX) |
| RXD | D6 (GPIO43, TX) |

If you see no data at all, swap TXD/RXD: it is harmless while running the read-only sniffer, which never transmits.

**120 Ω termination:** set the module's "120R" switch/jumper to **OFF**. The bus is already terminated; you are tapping into it, not ending it.

## Bus side: at the LB1 panel

1. Switch the ventilation unit **off**.
2. Unclip the LB1 panel from its wall base. In this installation it has 4 wires (green, yellow, white, brown).
3. With the unit **on** and the multimeter on V DC, find the pair with a steady **~27 V**: that is the panel power supply. **Do not touch it.**
4. The other pair is the RS485 data bus (terminals **3–4** on this installation).
5. Unit **off** again: connect the data pair to **A+ and B−** of the RS485 module, **in parallel** with the existing wires (do not disconnect them). Leave PE unconnected.
6. Clip the panel back and switch the unit on.

If frames do not decode (CRC errors / garbage), swap A+ and B−.

Logging goes over the XIAO's USB (`hardware_uart: USB_SERIAL_JTAG`), so the hardware UART is entirely dedicated to the bus.
