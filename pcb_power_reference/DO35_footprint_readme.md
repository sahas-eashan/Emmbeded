# Through-hole footprint for the Tronic 8.2 V Zener

Candidate for Tronic DI0102, subject to checking the purchased diode's dimensions.
Tronic identifies it as an 8.2 V, 0.5 W through-hole diode but does not publish a
manufacturer part number or mechanical drawing. Its product photograph shows
a small axial glass diode.

## Verified EasyEDA footprint

`D_DO-35_SOD27_P7.62MM_HORIZONTAL`

Library ID: `674eb866e74a499cb53dbfc5093abd4f`

- Pad spacing: 7.62 mm, centre to centre.
- Copper pads: approximately 1.60 mm.
- Plated holes: approximately 0.80 mm.
- Pad 1: cathode K, at the stripe/square-pad end; connect to BAT_P.
- Pad 2: anode A; connect to the MOSFET gate.

This file describes physical PCB pads. Use an 8.2 V Zener schematic symbol and
label its supplier part `Tronic DI0102`; keep the actual supplier identity in the
BOM. In the symbol's pin mapping, set cathode K to pin 1 and anode A to pin 2 for
this particular footprint. Other diode footprints may use a different numbering.

## EasyEDA Standard

1. Open `DO35_7p62_EasyEDA.json` using **File > Open > EasyEDA**, then save the
   footprint to your library.
2. Select the Zener in the schematic and click its **Footprint** property to open
   Footprint Manager. Alternatively, use **Tools > Footprint Manager**.
3. Choose the saved footprint under **Select > Work Space**, check the K/A pin
   mapping, and click **Update**.

You can also find the original footprint under **Library > Footprint** with the
name above, or open its library page below. Use the actual selected footprint in
Footprint Manager rather than just typing a name into the property.

Before fabrication, compare the physical diode with the footprint: the leads
must fit the holes and allow bends outside the glass body. This is a candidate
DO-35 footprint, not a mechanically confirmed Tronic part.

Sources:

- Tronic listing: https://tronic.lk/product/zener-diode-8-2v-12w
- EasyEDA library: https://easyeda.com/component/674eb866e74a499cb53dbfc5093abd4f
- Footprint data: https://lceda.cn/api/components/674eb866e74a499cb53dbfc5093abd4f
- Footprint Manager: https://docs.easyeda.com/en/Schematic/Footprint-Manager/
- Opening source files: https://docs.easyeda.com/en/Export/Export-EasyEDA-Source-File/
