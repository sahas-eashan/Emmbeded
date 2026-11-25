# Sensor and audio connections using Tronic sets listed at 2.54 mm pitch

Wiring reference for the ESP32-WROOM-32 project. The 10 W LED is omitted. Sensors and audio boards are external, ready-made modules. All grounds connect together. Connector numbers below are **our PCB assignments**, not the physical order of pins on each sensor. Wire the module end by its printed signal labels.

## 1. Connector sets to buy

Selected connector requirement: **2.54 mm pitch, single-row, polarized through-hole PCB header with a matching wired plug**. The products below explicitly list 2.54 mm spacing. These Tronic sets include a male through-hole PCB header and a matching prewired female cable plug. The free wire ends must be soldered to the modules or fitted with suitable female contacts for the modules' existing headers.

| PCB reference | Connection | Tronic product | Code | Quantity |
|---|---|---|---|---|
| J_PIR, J_RADAR | PIR and radar, three contacts each | [Short 3-Way PCB Mount Wire Clip with Socket (XH-3PX-150MM)](https://tronic.lk/product/short-3-way-pcb-mount-wire-clip-with-socket-xh-3px-150m) | TA0007 | 2 sets |
| J_MIC | INMP441 | [6-way XH-6PX-150MM, 150 mm cable](https://tronic.lk/product/short-6-way-pcb-mount-wire-clip-with-socket-xh-6px-150m) | TA0009 | 1 set |
| J_DF | DFPlayer control and power | [4-way XH-4PX-150MM, 150 mm cable](https://tronic.lk/product/short-4-way-pcb-mount-wire-clip-with-socket-xh-4px-150m) | TA0422 | 1 set |
| J_AMP_PWR | PAM8403 power | [2-way XH-2PX-100MM, 100 mm cable](https://tronic.lk/product/short-2-way-pcb-mount-wire-clip-with-socket-xh-2px-100m) | TA0943 | 1 set |

Buy **two three-pin sets, one six-pin set, one four-pin set and one two-pin set**. Retain the three-pin PIR/radar connectors and four-pin DFPlayer connector even if they need sourcing elsewhere. TA0007 and TA0422 were listed out of stock when checked on 2026-09-20; the selected two- and six-pin sets were in stock. The longer three-pin [XH-3PX-300mm / TA0444](https://tronic.lk/product/long-3-way-pcb-mount-wire-clip-with-socket-xh-3px-300mm) is another listed candidate, also out of stock when checked. DFPlayer needs exactly four contacts for this circuit, with none spare. TA0900 is excluded from this pitch requirement because its listing says 2.0 mm.

**Footprint is not yet verified:** Tronic still uses inconsistent XH/PH family names alongside its 2.54 mm claims. Treat these as generic connector sets listed at 2.54 mm, not a confirmed genuine JST family. Genuine [JST XH](https://www.jst-mfg.com/product/index.php?lang=2&series=277) uses 2.50 mm pitch; [JST PH](https://www.jst-mfg.com/product/index.php?lang=2&series=199) uses 2.00 mm. Measure the supplied PCB header's pitch, pins and housing before selecting the EasyEDA footprint or manufacturing the PCB. The included plug and header are a matching set, but the catalogue text does not establish their full PCB geometry.

In EasyEDA, use 1x2, 1x3, 1x4 and 1x6 connector symbols, then assign footprints for the purchased **2.54 mm polarized connectors**. Do not assign a 2.50 mm XH or 2.00 mm PH footprint by name. At 2.54 mm pitch the first-to-last pin-centre spacing is 2.54 mm for two pins, 5.08 mm for three pins, 7.62 mm for four pins and 12.70 mm for six pins. Hole diameter, body outline and pin-1 orientation must also match. Exact footprint selection remains pending physical dimensions.

### Exact retail names and EasyEDA searches

The Tronic product model strings are **XH-3PX-150MM**, **XH-6PX-150MM**, **XH-4PX-150MM** and **XH-2PX-100MM**. Their full listing titles begin "Short [pin count]-Way PCB Mount Wire Clip with Socket". These are retail names, not verified manufacturer part numbers.

In the EasyEDA Library select **Symbol**, not PCB Module. Search terms to locate candidate components are `XH2.54-3P`, `XH2.54-6P`, `XH2.54-4P` and `XH2.54-2P`. A Tronic TA code is not an EasyEDA or LCSC identifier.

Verified public library titles include [JST-XH2.54-3P](https://easyeda.com/components/JST-XH2-54-3P_e3b8879c143a4febb21c96ed858e35f9) and [XH2.54-2P_C9900015554](https://easyeda.com/component/7f635dc58cf3441fb5cad8f5d16fea6e). These are library candidates, **not verified footprint matches** to the Tronic parts. The four-pin [XH2.54-4P_C9900010451](https://easyeda.com/component/5181c02118d34f8b87505d73950466a3) has verified 2.54 mm pitch; its housing fit remains to be checked against the purchased part. No exact matching six-pin footprint has been established. Some parts with "2.54" in the name actually specify 2.50 mm pitch, so inspect the geometry rather than accepting the name alone.

## 2. PIR module: HC-SR501

| J_PIR pin | PCB connection | Sensor end |
|---|---|---|
| 1 | +5V | VCC |
| 2 | GND | GND |
| 3 | PIR_OUT -> 1 kOhm -> GPIO32, ESP module pad 8 | OUT |

Add 100 kOhm from GPIO32 to GND so the input is defined with the cable unplugged. Add 100 nF and 10 uF in parallel from +5V to GND near the connector. Retain the module's own decoupling. The HC-SR501 has a 3.3 V logic output despite using a 5 V supply. Keep it powered if it must detect motion while the ESP32 sleeps. Allow the module to settle after power-up.

Source: [HC-SR501 supplier specification](https://www.dragonwake.com/download/sensor/HC-SR501/HC-SR501.pdf).

## 3. Radar module: RCWL-0516

| J_RADAR pin | PCB connection | Sensor end |
|---|---|---|
| 1 | 5V_RADAR, from the switch below | VIN |
| 2 | GND | GND |
| 3 | RADAR_OUT -> 1 kOhm -> GPIO33, ESP module pad 9 | OUT |

Leave the module's **3V3 output** and CDS terminals unconnected. Add 100 kOhm from GPIO33 to GND and 100 nF + 10 uF from 5V_RADAR to GND near J_RADAR. Configure GPIO33 as an input with no pull-up; do not drive it high while the radar is unpowered. The 1 kOhm resistor is not complete isolation against back-powering.

Sources: [SparkFun module listing](https://www.sparkfun.com/human-body-induction-module-rcwl-0516-with-headers.html), [module schematic](https://cdn.sparkfun.com/assets/b/3/2/b/6/RCWL-0516_Schematic.pdf).

### Radar power switch

Use new references **Q2** and **Q3**; keep Q1 for the existing battery-input AO3401A. Both new MOSFETs are SOT-23, with pins 1 = gate, 2 = source, 3 = drain.

| Connection | Destination |
|---|---|
| Q2 FDN340P source, pin 2 | +5V |
| Q2 FDN340P drain, pin 3 | 5V_RADAR -> J_RADAR pin 1 |
| Q2 FDN340P gate, pin 1 | Q3 FDV303N drain, pin 3 |
| R_PG, 100 kOhm | Q2 gate -> +5V / Q2 source |
| Q3 FDV303N source, pin 2 | GND |
| R_DRV, 1 kOhm | GPIO27, ESP module pad 12 -> Q3 gate, pin 1 |
| R_NG, 100 kOhm | Q3 gate -> GND, on the transistor side of R_DRV |

**GPIO27 HIGH = radar ON. LOW or floating = OFF.** Set GPIO27 LOW before configuring it as an output during startup. Allow the radar module to settle after switching it on before using its readings.

No gate Zener is needed for this regulated 5 V switch. FDN340P's gate rating is only +/-8 V: **do not use it as a replacement for the AO3401A in the 9 V input-protection block with the 8.2 V Zener.** The input-protection P-channel MOSFET and this load-switch P-channel MOSFET deliberately have different source/drain connections.

The old AO3400A circuit drawn directly between 3V3 and GND must be removed or rewired: turning it on would short the supply. For this Tronic-based version, replace that device with Q3 FDV303N and wire it as above; remove its direct 3V3 connection and use GPIO27 instead of GPIO2.

Sources: [FDN340P datasheet](https://www.onsemi.com/pdf/datasheet/fdn340p-d.pdf), [FDV303N datasheet](https://www.onsemi.com/download/data-sheet/pdf/fdv303n-d.pdf). See also `radar_power_switch_tronic.pdf` in this folder.

## 4. Microphone module: INMP441

| J_MIC pin | PCB connection | Microphone end |
|---|---|---|
| 1 | 3V3 | VDD |
| 2 | GND | GND |
| 3 | GPIO26, ESP module pad 11 | SCK |
| 4 | GPIO25, ESP module pad 10 | WS |
| 5 | GPIO34, ESP module pad 6 | SD |
| 6 | GND | L/R |

Add 100 kOhm from SD/GPIO34 to GND. L/R grounded selects the left I2S slot; configure firmware for that slot. GPIO34 is input-only, suitable for microphone data. **Supply the microphone with 3.3 V, not 5 V.** Ensure 100 nF bypassing at the microphone module itself; a capacitor only at the main PCB end does not replace it.

This plan assumes a short cable, such as the supplied 150 mm cable. Long I2S cable runs need a separate signal-integrity review. Keep microphone wiring away from the amplifier outputs and switching power circuit.

Source: [TDK INMP441 datasheet](https://product.tdk.com.cn/system/files/dam/doc/product/sw_piezo/mic/mems-mic/data_sheet/inmp441.pdf).

## 5. DFPlayer Mini module

Drawing: [dfplayer_circuit.pdf](dfplayer_circuit.pdf), with a preview in [dfplayer_circuit.png](dfplayer_circuit.png). The connector pin numbers are our custom cable assignments; the DFPlayer module pin numbers below are separate.

### Actual EasyEDA library entries for this circuit

Click the EasyEDA links and use **Open in Editor**, or search the exact title with **Symbol** selected. The resistor and 100 nF capacitor are actual entries in the LCSC category *inside EasyEDA*, not merely shopping-site records. The module and 100 uF entry are community components.

| Circuit item | Exact EasyEDA title | Linked package | Direct EasyEDA link |
|---|---|---|---|
| External DFPlayer module | DFPlayer Mini | DFPlayer Mini | [Component, contributor cKDVP7pjB](https://easyeda.com/component/DFPlayer_Mini-5dc49a1020904ea4b2f1a24056d818e6) |
| R_DF1, 1 kOhm | 0805W8F1001T5E | R0805 | [Component](https://easyeda.com/component/8aebd62994a05a89b2fc1c520ce2e64f) |
| J_DF, four-pin connector | XH2.54-4P_C9900010451 | CONN-TH_XH2.54-4P-1 | [Component](https://easyeda.com/component/5181c02118d34f8b87505d73950466a3) |
| C_DF1, 100 nF / 50 V | CL21B104KBCNNNC | C0805 | [Component](https://easyeda.com/component/c58e33efcd08c9c01df888e6a177ba93) |
| C_DF2, 100 uF / 25 V | 100uF 25V SMD | CAPAE660X800N | [Component, contributor Prado1](https://easyeda.com/component/ce76aea22f6445788a2582a1bbb24b79) |
| External amplifier module, optional drawing reference | AMPLIFIER-PAM8403 | AMPLIFIER-PAM8403 | [Component](https://easyeda.com/component/c39b9ae17ad0475fab86e6e84e910dd8) |

EasyEDA API verification confirms symbol docType 2 plus footprint docType 4 for J_DF, R_DF1, C_DF1 and C_DF2. The module pages confirm the catalogue title and a linked package; their complete pin-to-pad mappings have not been reviewed. Since DFPlayer and PAM8403 are external in this plan, their symbols may illustrate the wiring, but exclude their footprints from the main PCB; the four-pin connector, resistor and capacitors belong on the PCB.

**J_DF connector:** use four pins, referenced to Tronic TA0422 / XH-4PX-150MM. EasyEDA `XH2.54-4P_C9900010451` has linked footprint `CONN-TH_XH2.54-4P-1`: verified 2.54 mm pitch, 7.62 mm first-to-last pin span, 1.10 mm holes, 1.70 mm pads and approximately 12.7 x 5.7 mm body outline. Match the actual purchased header's housing and terminals before fabrication. The prior five-pin candidate is no longer part of this design.

| J_DF pin | PCB connection | DFPlayer end |
|---|---|---|
| 1 | +5V | VCC, module pin 1 |
| 2 | GND | GND, module pin 7 or 10 |
| 3 | GPIO17, ESP module pad 28 -> 1 kOhm -> connector | RX, module pin 2 |
| 4 | GPIO16, ESP module pad 27 | TX, module pin 3 |

Set the ESP32 UART to 9600 baud, 8N1, TX pin GPIO17 and RX pin GPIO16. Add C_DF1 = 100 nF (0.1 uF), 0805, and C_DF2 = 100 uF / 25 V aluminium electrolytic across the supply near the connector; retain local decoupling at the module end. These capacitors are a local design recommendation, not a claimed fixed requirement from the DFPlayer datasheet. Electrolytic capacitor positive goes to +5V and negative to GND. R_DF1 = 1 kOhm, 0805, belongs only in the ESP TX -> DFPlayer RX path. These names are placeholders: assign unused reference numbers when copying into the project. The documented DFPlayer uses approximately 3.3 V UART logic; an unidentified clone's output level has not been measured.

Sources: [DFRobot DFPlayer Mini documentation](https://wiki.dfrobot.com/dfr0299), [manufacturer pin table](https://dfimg.dfrobot.com/wiki/20532/DFR0299_mp3-player-module_datasheet_V1.0.pdf).

## 6. PAM8403 amplifier and speaker

This plan uses a ready-made PAM8403 amplifier module with its input coupling and local decoupling populated, not the bare IC.

| Connection | Destination |
|---|---|
| J_AMP_PWR pin 1 | +5V -> amplifier VCC / + |
| J_AMP_PWR pin 2 | GND -> amplifier GND / - |
| DFPlayer DAC_L | Amplifier left analogue input, L / L_IN |
| DFPlayer GND | Amplifier input GND |
| Speaker terminal 1 | Amplifier L+ |
| Speaker terminal 2 | Amplifier L- |

Add 100 nF + 100 uF near the amplifier supply input. Run its power and ground back to the main supply, rather than through sensor ground wires. The DAC_L/GND and speaker wires can connect directly between external modules; no main-PCB connector is needed for signals that do not return to the main PCB.

Leave DFPlayer SPK1/SPK2 unused when using the external amplifier. Neither PAM8403 speaker terminal connects to GND, and the L/R amplifier outputs must not be tied together. For stereo, repeat the analogue and speaker wiring with DAC_R and R+/R-.

Source: [PAM8403 datasheet](https://www.diodes.com/datasheet/download/PAM8403.pdf).

## 7. Tronic parts for the new blocks

All resistors below are **0805** (2012 metric), matching the requested size. Quantities describe the wiring above; existing suitable parts can be reused with unique references.

| Part | Quantity | Tronic code and link |
|---|---|---|
| FDN340P P-channel MOSFET, SOT-23 | 1 | [DI0036](https://tronic.lk/product/fdn340p-p-channel-power-mosfet-code-340) |
| FDV303N N-channel MOSFET, SOT-23 | 1 | [DI0094](https://tronic.lk/product/fdv303n-n-channel-mosfet) |
| 1 kOhm, 1%, 0805 | 4 | [RU0043, pack](https://tronic.lk/product/1k-18w-resistor-pack-smd-0805-1-approx-40pcs) |
| 100 kOhm, 1%, 0805 | 5 | [RU0091, pack](https://tronic.lk/product/100k-18w-resistor-pack-smd-0805-1-approx-40pcs) |
| 100 nF, 50 V, 0805 | 4 main-board bypass capacitors; verify microphone local bypass too | [CP0043, pack](https://tronic.lk/product/100nf-50v-capacitor-pack-smd-0805-approx-40pcs) |
| 10 uF, 50 V, 0805 | 2 | [CP0050, pack](https://tronic.lk/product/10uf-50v-capacitor-pack-smd-0805-approx-40pcs) |
| 100 uF, 25 V aluminium SMD, 6.3 x 7.7 mm body | 2 | [CA0195](https://tronic.lk/product/100uf-25v-electrolytic-capacitor-aluminium-smd-6-3x7-7m) |
| 10 kOhm, 1%, 0805 for EN pull-up | 1, reuse R7 if suitable | [RU0067, pack](https://tronic.lk/product/10k-18w-resistor-pack-smd-0805-1-approx-40pcs) |
| 1 uF, 50 V, 0805 for EN timing | 1 | [CP0047, pack](https://tronic.lk/product/1uf-50v-capacitor-pack-smd-0805-approx-40pcs) |

Exact Tronic listing titles for these parts:

- DI0036: **FDN340P P-channel Power MOSFET (Code 340)**.
- DI0094: **FDV303N N-channel MOSFET**.
- RU0043: **1k 1/8W Resistor Pack SMD 0805 1% (Approx. 40pcs)**.
- RU0091: **100k 1/8W Resistor Pack SMD 0805 1% (Approx. 40pcs)**.
- RU0067: **10k 1/8W Resistor Pack SMD 0805 1% (Approx. 40pcs)**.
- CP0043: **100nF 50V Capacitor Pack SMD 0805 (Approx. 40pcs)**.
- CP0050: **10uF 50V Capacitor Pack SMD 0805 (Approx. 40pcs)**.
- CP0047: **1uF 50V Capacitor Pack SMD 0805 (Approx. 40pcs)**.
- CA0195: **100uf 25V Electrolytic Capacitor Aluminium SMD (6.3x7.7mm)**.

For EasyEDA, search `FDN340P` and `FDV303N` for the MOSFETs, matching the SOT-23 pin map. For the generic Tronic resistors and ceramic capacitors, use resistor/capacitor symbols with 0805 footprints and set the values above. Tronic does not publish manufacturer part numbers for those packs, so a specific branded EasyEDA passive cannot be claimed to be the exact purchased part.

### Resistor and capacitor catalogue references and EasyEDA availability

The first six rows below are verified LCSC catalogue references with the specified nominal value and package. Actual EasyEDA symbol-and-footprint entries have now also been verified for the 1 kOhm resistor and 100 nF capacitor, linked in the DFPlayer section. EasyEDA availability of the other catalogue rows remains unverified. **A listing on LCSC does not prove availability in EasyEDA.** The user could not find C2983385 / GVZ1E107M0608CNVC in EasyEDA, so that earlier library recommendation is withdrawn and replaced below with an actual public EasyEDA entry. The Tronic column identifies the locally sold generic part: it is **not confirmation that Tronic supplies the listed brand or manufacturer part number**. Record the actual Tronic SKU in the purchasing BOM when buying the Tronic part.

| Value and package | Exact catalogue/library name | LCSC code or EasyEDA entry | Tronic part |
|---|---|---|---|
| 1 kOhm, 0805, 1%, 125 mW | 0805W8F1001T5E | [C17513](https://www.lcsc.com/product-detail/C17513.html) | RU0043 |
| 10 kOhm, 0805, 1%, 125 mW | 0805W8F1002T5E | [C17414](https://www.lcsc.com/product-detail/C17414.html) | RU0067 |
| 100 kOhm, 0805, 1%, 125 mW | 0805W8F1003T5E | [C149504](https://www.lcsc.com/product-detail/C149504.html) | RU0091 |
| 100 nF, 50 V, 0805 | CL21B104KBCNNNC | [C1711](https://www.lcsc.com/product-detail/C1711.html) | CP0043 |
| 1 uF, 50 V, 0805 | CL21B105KBFNNNE | [C28323](https://www.lcsc.com/product-detail/C28323.html) | CP0047 |
| 10 uF, 50 V, 0805 | CC0805KKX5R9BB106 | [C22465730](https://www.lcsc.com/product-detail/C22465730.html) | CP0050 |
| 100 uF, 25 V, SMD; check actual pad geometry | 100uF 25V SMD | [EasyEDA component ce76aea22f6445788a2582a1bbb24b79](https://easyeda.com/component/ce76aea22f6445788a2582a1bbb24b79) | CA0195 |

The first three references are UNI-ROYAL resistors. The 100 nF and 1 uF references are Samsung X7R; the 10 uF reference is YAGEO X5R. These dielectric specifications apply to the named catalogue parts only; Tronic's packs do not specify dielectric. Use the polarized symbol for 100 uF, with positive to the supply and negative to GND. The ceramic capacitors and resistors have no polarity. These references cover the remaining sensor/audio blocks and EN reset, not a qualification of the existing regulator capacitors.

**100 uF EasyEDA entry:** exact title `100uF 25V SMD`, contributor `Prado1`, linked package `CAPAE660X800N`. Open the EasyEDA component page and use **Open in Editor**. For a library search, use the EasyEDA search engine, Symbol type and User Contributed category rather than filtering to LCSC. The [EasyEDA component API](https://easyeda.com/api/components/ce76aea22f6445788a2582a1bbb24b79) confirms a schematic symbol (docType 2) plus a linked footprint (docType 4), with symbol pin 1 positive and pin 2 negative. Associated manufacturer part: `NACZ101M25V6.3X8TR13F`. Footprint base outline: 6.6 x 6.6 mm; pads: 3.80 x 1.85 mm each; pad-centre spacing: 5.10 mm. Placing it inside the user's editor has not been tested. The package is a candidate, not a verified match for Tronic CA0195: compare the actual capacitor's base, terminal spacing and pad requirements before fabrication.

Listings do not identify the ceramic capacitor manufacturer or dielectric; they are not established replacements for the buck regulator's specified capacitors. An electrolytic's body dimensions alone do not define its solder-pad geometry; check the purchased part before assigning that footprint.

## 8. Existing-sheet corrections still needed if unchanged

- D3's revised connection is correct for gate clamping: cathode/band to the input AO3401A source/BAT_P, anode to its gate. Label its value 8.2 V; keep the existing AO3401A here.
- Replace the EN reset network with 3V3 -> 10 kOhm -> EN; EN -> 1 uF -> GND; reset button directly between EN and GND. Remove the two 4.7 kOhm series branches and the extra timing capacitor. The previously drawn divider prevents the button pulling EN reliably low.
- The programming connector should expose GND, TXD0/GPIO1, RXD0/GPIO3, EN and GPIO0; a sixth 3V3 contact can be a voltage reference. Do not use CLK or SD0, which belong to the module's flash interface. Use a 3.3 V logic UART adapter and avoid powering the 3V3 rail from two supplies at once.
- Put the battery divider's `GPIO35` net label on ESP32 IO35 / module pad 7 as well as the divider node. The divider measures the protected, switched battery rail. With 100 kOhm on top and 27 kOhm to ground, V_BAT = V_ADC * 127/27. At 9 V, the ideal ADC voltage is approximately 1.91 V. Use appropriate ADC attenuation and calibration; voltage alone is only an estimate of battery state.
- Resolve the drawn L7805's heat before PCB layout: it dissipates (V_BAT - 5 V) * total 5 V rail current. A buck reduces that loss. A rectangular 9 V battery also needs a loaded test with the ESP32 and audio; changing the regulator does not establish that battery's peak-current capability.
- Give every component a unique reference across sheets. Add test points for BAT_P, +5V, 3V3, 5V_RADAR and GND. Keep the ESP32 antenna area clear per the module layout guidance.

Sources: [Espressif schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html), [ESP32-WROOM-32 module datasheet](https://documentation.espressif.com/esp32-wroom-32_datasheet_en.html), [ST L78 datasheet](https://www.st.com/resource/en/datasheet/l78.pdf).

This is a wiring/design reference, not an imported EasyEDA project or a bench-tested PCB. Component-to-footprint pin mapping, connector dimensions and the complete PCB layout still need verification.
