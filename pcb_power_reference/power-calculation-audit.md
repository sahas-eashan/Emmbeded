# Power calculation audit

Reference: the supplied `C:\Users\Cyborg\Downloads\RCWL-0516.pdf` (11 pages). The user has confirmed a rectangular 9 V battery and removal of the 10 W LED array. The current design therefore includes the sensors, ESP32, and audio deterrent, plus the small power-indicator LED. Calculations below use a terminal voltage of 9.0 V; current increases as battery voltage falls if the converters can maintain regulation.

## Corrections to the supplied document

- Pages 5–7 calculate battery current at **12 V**, although page 8 uses **9 V**. These currents cannot be carried into the new design unchanged.
- Page 8 includes audio but omits the **10 W LED** specified on page 4 and included again on page 10. The user has now removed that LED array, so page 10's approximately 15.26 W/1.27 A deterrent result is obsolete. Page 8's approximately 4.15 W audio-only result is the relevant idealized baseline.
- Page 9 says “9 V, 7 Ah VRLA” in its title, but its 12 V nominal rating, 84 Wh energy, charge voltages, and referenced NP7-12 battery describe a **12 V, 7 Ah lead-acid battery**. These values do not describe a rectangular 9 V battery. The stated 19.6-day runtime therefore does not apply.
- A 90%-efficient conversion assumption does not represent an AMS1117 linear regulator. For an LDO, input current is approximately output current plus its ground/quiescent current; input power is not output power divided by 0.9.
- The named microphone is an **INMP441 digital I²S microphone**, not an analog-output microphone. It needs SCK, WS, and SD connections. GPIO34 can receive its I²S data, but reading GPIO34 with the ADC will not recover the microphone audio. Choose separate output-capable GPIOs for SCK and WS.
- Datasheet ESP32 sleep currents do not include regulator, indicator, divider, or external-circuit current. The document assumes Wi-Fi and Bluetooth are off and does not budget radio transmission or startup peaks.

## Baseline load assumptions retained from the document

These are design assumptions, not measurements of the assembled board.

| Mode | ESP32 current at 3.3 V | INMP441 current at 3.3 V | Combined 3.3 V current |
|---|---:|---:|---:|
| Deep sleep | 0.010 mA | 0.0045 mA | 0.0145 mA |
| Idle/light sleep | 0.8 mA | 0.8 mA | 1.6 mA |
| Active sensing, 80 MHz | 31 mA | 2.5 mA | 33.5 mA |
| Audio deterrent, 240 MHz | 68 mA | 2.5 mA | 70.5 mA |

RCWL-0516: 5 V, 3 mA in every row. HC-SR501: 5 V, 0.05 mA in every row. The amplifier and DFPlayer are assumed disabled outside audio events. An audio event uses one 3 W output channel, 90% amplifier efficiency, and a 5 V/30 mA DFPlayer allowance. The 10 W LED array has been removed from the confirmed design.

## Case A: retain the existing 5 V to 3.3 V AMS1117

Model: 9 V to 5 V buck at 90% efficiency, followed by the existing AMS1117 for the 3.3 V loads. Include the pictured 5 V indicator with a 2 kΩ resistor and an assumed red LED forward voltage of 2 V: approximately 1.5 mA. Include a 100 kΩ/27 kΩ battery divider: approximately 0.071 mA at 9 V.

For the exact selected LCSC part **C2992570**, the supplier datasheet lists **4 mA typical and 8 mA maximum quiescent current**. The table uses 4 mA. It also specifies a **10 mA minimum-load condition**: the document's sleep and idle 3.3 V loads are below this. Treat those rows as rough current estimates, not a guarantee that this regulator maintains the required output voltage at those loads.

```text
I_5V = I_3V3_load + I_AMS1117 + I_radar + I_PIR + I_indicator
       + I_DFPlayer + P_audio_output / (eta_amplifier × 5 V)

I_battery = (5 V × I_5V) / (eta_5V_buck × V_battery)
            + V_battery / (100 kΩ + 27 kΩ)
```

| Mode | Total 5 V rail current | Estimated battery current at 9 V |
|---|---:|---:|
| Deep sleep | 8.565 mA | **5.36 mA** |
| Idle/light sleep | 10.15 mA | **6.34 mA** |
| Active sensing, 80 MHz | 42.05 mA | **26.03 mA** |
| Audio deterrent, 240 MHz | 775.72 mA | **478.91 mA** |

Using 8 mA instead of 4 mA for regulator quiescent current adds approximately **2.47 mA** at the 9 V input under the same buck assumption. A 10 mA bleeder load, if added to address minimum load, would add another approximately **6.17 mA** at the battery. Neither addition is included in the table.

## Case B: independent buck converters for 5 V and 3.3 V

Recommended topology: feed a 5 V buck and a **3.3 V buck directly from the protected battery input**, in parallel. The 3.3 V regulator therefore replaces the AMS1117 rather than following the 5 V converter. An AP63203 is the proposed fixed-3.3 V regulator; component selection and connections are provided in the accompanying power reference.

The following table reproduces the document's **idealized 90% efficiency assumption**, now consistently at 9 V and with the two rails supplied by separate bucks. It **excludes converter quiescent-current effects and efficiency variation, the indicator LED, the battery divider, and other board overhead**. It is a comparison baseline, not a prediction of measured sleep current.

```text
P_battery = (5 V × I_5V_load) / eta_5V_buck
            + (3.3 V × I_3V3_load) / eta_3V3_buck

I_battery = P_battery / V_battery

Audio adds: 3 W / (0.90 × 0.90) + (5 V × 30 mA) / 0.90
```

| Mode | Idealized battery power | Idealized current at 9 V |
|---|---:|---:|
| Deep sleep | 17.00 mW | **1.889 mA** |
| Idle/light sleep | 22.81 mW | **2.535 mA** |
| Active sensing, 80 MHz | 139.78 mW | **15.531 mA** |
| Audio deterrent, 240 MHz | 4.146 W | **460.65 mA** |

Under the same assumptions, the 5 V indicator adds about 0.926 mA of battery current and the divider adds about 0.071 mA. Converter efficiency must be checked at each actual load: **90% is especially unreliable for the tiny 3.3 V sleep load**. Use measured input current or the full converter loss model; do not add quiescent current a second time if it is already included in measured efficiency.

## Radar switching and regulator sizing

Switching off a 5 V/3 mA radar saves approximately **1.85 mA at 9 V**, assuming 90% buck efficiency and unchanged other loads. This applies to either topology. A powered-off radar cannot generate a wake signal, so PIR must remain powered if it is the wake source. Firmware must allow radar startup/settling time after restoring its power, and signal connections must not feed power into the disabled radar.

With independent bucks, the 5 V rail supplies approximately **0.70 A** during the modeled full-output audio event: about 667 mA for the amplifier, 30 mA for the DFPlayer, and 3.05 mA for the motion sensors. The pictured indicator adds about 1.5 mA. A properly implemented **2 A-rated 5 V buck** provides useful converter margin for this confirmed load; verify the actual selected components, thermal layout, load transients, and input-voltage range. A converter's 2 A rating does not establish the battery's available current. The modeled 3.3 V rail load in this event is 70.5 mA with Wi-Fi and Bluetooth off, but regulator selection must also allow ESP32 startup and any enabled radio activity.

## Battery selection and runtime

Do not use 7 Ah or 84 Wh for the rectangular battery, and do not infer its suitability from the nominal 9 V label. Obtain its exact chemistry and model, manufacturer discharge curves, supported load, and loaded-voltage behavior. The approximately **0.46–0.48 A sustained full-output audio case** is already a demanding load for this battery format, even after removal of the 10 W LED. Validate operation at the weakest acceptable battery voltage, including audio transients, before fixing the battery and converter design.

For runtime, calculate time-weighted battery energy using non-overlapping mode durations and the selected battery's **usable energy at the actual discharge load and cutoff voltage**. Pages 9–10's lead-acid example cannot establish the runtime of the new battery.

## Sources

- User-supplied `RCWL-0516.pdf`, pages 2–10: sensor identities, mode currents, audio/LED assumptions, and the inconsistent voltage/capacity calculations audited here.
- [Supplier datasheet for the exact AMS1117-3.3 part C2992570](https://datasheet.lcsc.com/datasheet/pdf/30502c8696c347d1305c8558cd512433.pdf?productCode=C2992570): regulator quiescent current and minimum-load condition.
- [ESP32-WROOM-32 datasheet](https://documentation.espressif.com/esp32-wroom-32_datasheet_en.html): GPIO35 is ADC1_CH7, module pad 7; I²S signal routing and ADC electrical limits.
- [Arduino-ESP32 ADC documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html): use calibrated `analogReadMilliVolts()` with the selected attenuation; battery voltage equals measured ADC voltage times `(100 + 27) / 27` for the stated divider, before any input-protection drop correction.

This is a calculation review and design reference, not measured hardware validation.
