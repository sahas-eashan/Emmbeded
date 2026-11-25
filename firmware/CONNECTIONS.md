# Connections (read from the PCB file)

Source: `PCB_Embedded_PCB_2026-11-25.pcbdoc`. Board 62.9 × 67.5 mm, 2 layers. All nets routed, no shorts, no clearance below 6 mil.
The firmware pin map is [include/pins.h](include/pins.h).

## Connector → module

| PCB connector | Pin 1 | Pin 2 | Pin 3 | Pin 4 | Pin 5 | Pin 6 | Module |
|---|---|---|---|---|---|---|---|
| **U7** (XH 3P) | 5V_RADAR (switched) | GND | OUT → R5 → **GPIO21** | | | | RCWL-0516 radar |
| **U2** (3-pin header) | GND | OUT → R8 → **GPIO34** | **3V3** | | | | HC-SR501 PIR |
| **J1** (6P) | GND | GND (→ mic L/R) | **GPIO33** → mic SD | **GPIO25** → mic WS | **GPIO26** → mic SCK | 3V3 | INMP441 mic |
| **P2** (XH 4P) | +5V | GND | DF **RX** ← R17 1k ← **GPIO17** | DF **TX** → **GPIO18** | | | DFPlayer Mini |
| **P1** (XH 2P) | +5V | GND | | | | | PAM8403 power |
| **U3** (2×3 header) | 3V3 | ⚠ CLK (flash) | GND | TXD0 | RXD0 | ⚠ SD0 (flash) | USB-UART programming |
| **U6** DC jack → **SW3** rocker → Q1 (reverse-polarity P-MOSFET) → **BAT_P** | | | | | | | 9 V input |

## Other signals

| Function | GPIO | Hardware |
|---|---|---|
| Radar power switch | **GPIO16** (net `RADAR_SWITCH`, module pad 27) | HIGH = radar on (Q3 → Q2 high-side), R16 holds it off at boot |
| Battery sense | GPIO35 | BAT_P → R10 → GPIO35 → R11 → GND, C8 filter |
| BOOT button SW2 | GPIO0 | R6 pull-up, R7 series |
| RESET button SW1 | EN | RC network R1/R2/R3/C1/C2 |
| Power LED | none | LED1 + R12 hard-wired to +5V |
| 5 V regulator | U4 (TO-220, 7805-type) | BAT_P → +5V |
| 3.3 V regulator | U5 (SOT-223, AMS1117-3.3) | +5V → 3V3 |

Pin assignments differ from the earlier `sensor_connections_tronic.md` plan: PIR moved to GPIO34, mic SD to GPIO33, radar to GPIO21, radar switch to **GPIO16 (not GPIO27)**, DFPlayer TX line to GPIO18. The firmware follows the **PCB**.

## Check these before powering the board

1. **D1 is across BAT_P and GND.** The plan puts the 8.2 V Zener from BAT_P (cathode) to Q1's **gate** (anode). On this PCB it sits directly across the supply, so a 9 V battery would push heavy current through an 8.2 V Zener. With a 9 V battery, **leave D1 unpopulated**. Q1's ±12 V gate rating covers 9 V without it.
2. **U3 programming header exposes CLK (GPIO6) and SD0 (GPIO7).** These are the module's internal flash pins. **Never connect anything to U3 pins 2 and 6.** To program, use only TXD0, RXD0 and GND. Hold **BOOT (SW2)**, tap **RESET (SW1)**, then release BOOT. Power the board from the battery/jack, not from the adapter's 3V3.
3. **EN reset network** is still the older two-branch divider. If SW1 doesn't reset the ESP32, power-cycle instead (the fix is a direct EN-to-GND button).
4. **PIR is powered from 3V3.** The HC-SR501 is specified for 4.5–20 V. If it never triggers, feed it from the module's 3.3 V regulator bypass or a 5 V wire.
5. **U4 (linear 5 V) heat.** About 4 V × 0.7 A ≈ 2.8 W during full-volume audio, which needs a heatsink. Test audio at low volume first.
6. **J1 and SW1/SW2 holes are 0.8 mm.** XH/header pins usually need about 1.0 mm, so check that the parts fit before soldering. P2's footprint pitch is 2.50 mm (not 2.54); a 4-pin plug still fits.
7. The exported GND pour is unfilled. GND is fully routed with tracks, so this is fine, but rebuild the copper area in EasyEDA before generating Gerbers.

## Test order (`pio run -e hwtest -t upload -t monitor`)

| Key | Test | Pass |
|---|---|---|
| `b` | Battery | Reading matches a multimeter on BAT_P (else fix `R_BATT_*` in config.h) |
| `R` | Radar power | 5 V at U7 pin 1 when ON, 0 V when OFF |
| `r` | Radar | HIGH ~2 s when you move in front of it |
| `p` | PIR | HIGH on motion, after ~60 s warm-up |
| `m` | Microphone | One slot reacts to claps/speech: set `MIC_SLOT` (verified: slot A = 0) |
| `c` | Crow detector | Play crow calls from a phone: `CROW-LIKE CALL` lines and `CROW CONFIRMED`. Tune `CROW_*` in config.h |
| `d` | DFPlayer | `DFPlayer OK`, file count > 0, sound from speaker. SD card: `0001.mp3` in the root |
| `k` | BOOT button | 1 → 0 when pressed |
| `a` | All together | Live dashboard used for calibrating thresholds |

Then flash the final firmware: `pio run -e main -t upload -t monitor`. Set `ENABLE_LIGHT_SLEEP = false` while debugging.

## Final firmware behaviour

PIR wakes the board from light sleep, then the microphone confirms a crow call before the deterrent plays.

`WARMUP 60 s` -> `IDLE` (light sleep, wake on PIR HIGH or the 15-min battery timer) -> `LISTEN` (8 s after the last PIR activity, max 20 s) -> crow confirmed -> `DETER` (max 3 s) -> `COOLDOWN 15 s` -> `LISTEN` if PIR still active, else `IDLE`.

- **Crow detection:** each 50 ms block's 0.5-2.5 kHz band level is compared to a learned background. A run of loud in-band blocks lasting 100-1500 ms is a call; `CROW_CALLS_REQUIRED` calls within 5 s confirm a crow. Current values are lenient for the demo; the field values are noted next to each setting in config.h.
- **Radar:** `USE_RADAR = false` keeps GPIO16 LOW (radar plugged in but unpowered). Setting it `true` powers the radar during LISTEN only, waits `RADAR_SETTLE_MS`, and lets `CONFIRM_MODE` use it.
- **Battery:** checked every 15 min. Below 7.0 V the outputs switch off and the board sleeps on the timer only until the battery is back above 7.4 V. Set `BATTERY_MONITOR = false` when powering the board from USB or the Pi 5 V (BAT_P then reads ~0 V and would count as a fault).
- **Mic sleep:** the INMP441 powers down when its clock stops before sleep. After waking, the first 300 ms are discarded while it starts up.
