"""Generate an explicit pin-wiring reference for the 5 V radar load switch."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import pymupdf

OUT = Path(__file__).resolve().parent
PDF = OUT / "radar_power_switch_tronic.pdf"
c = canvas.Canvas(str(PDF), pagesize=(1100, 800))
c.setTitle("RCWL-0516 5 V power switch - Tronic parts")
INK = colors.HexColor("#16344A")
WIRE = colors.HexColor("#157968")
PALE = colors.HexColor("#EFF5F7")
MUTED = colors.HexColor("#516575")


def text(x, y, value, size=12, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, value)


def wire(*points):
    c.setStrokeColor(WIRE)
    c.setLineWidth(1.8)
    p = c.beginPath()
    p.moveTo(*points[0])
    for point in points[1:]:
        p.lineTo(*point)
    c.drawPath(p)


def dot(x, y):
    c.setFillColor(WIRE)
    c.circle(x, y, 3, stroke=0, fill=1)


def box(x, y, w, h):
    c.setStrokeColor(colors.HexColor("#AFC5CE"))
    c.setFillColor(PALE)
    c.roundRect(x, y, w, h, 6, stroke=1, fill=1)


def res_h(x1, x2, y, label):
    mid = (x1+x2)/2
    wire((x1, y), (mid-25, y))
    c.setStrokeColor(WIRE)
    c.rect(mid-25, y-6, 50, 12, stroke=1, fill=0)
    wire((mid+25, y), (x2, y))
    text(mid-34, y+17, label, 11)


def res_v(x, y1, y2, label):
    mid = (y1+y2)/2
    wire((x, y1), (x, mid+23))
    c.setStrokeColor(WIRE)
    c.rect(x-6, mid-23, 12, 46, stroke=1, fill=0)
    wire((x, mid-23), (x, y2))
    text(x+13, mid+4, label, 11)


def ground(x, y):
    wire((x, y), (x, y-9))
    wire((x-12, y-9), (x+12, y-9))
    wire((x-8, y-14), (x+8, y-14))
    wire((x-4, y-19), (x+4, y-19))


text(40, 755, "RCWL-0516: switched 5 V supply", 25, True)
text(40, 730, "Pin-wiring schematic | All resistors 0805 | GPIO27 HIGH = ON; LOW or floating = OFF", 13)

# Q2 is intentionally a labelled pin block, so package pin mapping is unambiguous.
box(410, 520, 230, 125)
text(426, 618, "Q2  FDN340P", 16, True)
text(426, 598, "P-channel | SOT-23 | DI0036", 11)
text(422, 566, "2 SOURCE", 11, True)
text(557, 566, "DRAIN 3", 11, True)
text(500, 532, "1 GATE", 11, True)
wire((130, 560), (410, 560))
text(130, 578, "+5V regulated", 13, True)
wire((640, 560), (960, 560))
text(720, 578, "5V_RADAR", 13, True)
dot(280, 560)
res_v(280, 560, 465, "R_PG 100k")
wire((280, 465), (525, 465))
wire((525, 520), (525, 400))
dot(525, 465)

# Gate driver.
box(425, 275, 200, 125)
text(440, 363, "Q3  FDV303N", 16, True)
text(440, 342, "N-channel | SOT-23", 11)
text(440, 325, "DI0094", 11)
text(501, 383, "3 DRAIN", 10, True)
text(435, 298, "1 GATE", 10, True)
text(501, 284, "2 SOURCE", 10, True)
wire((525, 275), (525, 229))
ground(525, 229)
text(549, 218, "GND", 11)
text(45, 318, "GPIO27", 13, True)
text(45, 298, "ESP pad 12", 11)
res_h(130, 330, 300, "R_DRV 1k")
wire((330, 300), (425, 300))
dot(345, 300)
res_v(345, 300, 229, "R_NG 100k")
ground(345, 229)

# Connector rail and supply capacitors.
box(900, 405, 155, 115)
text(912, 495, "J_RADAR", 14, True)
text(912, 474, "TA0007 / 3-way", 11)
text(912, 451, "1  5V_RADAR -> VIN", 10)
text(912, 433, "2  GND -> GND", 10)
text(912, 415, "3  OUT from radar", 10)
wire((960, 560), (960, 520))
for xpos, label in ((755, "100nF"), (833, "10uF")):
    dot(xpos, 560)
    wire((xpos, 560), (xpos, 521))
    wire((xpos-11, 521), (xpos+11, 521))
    wire((xpos-11, 514), (xpos+11, 514))
    wire((xpos, 514), (xpos, 490))
    ground(xpos, 490)
    text(xpos-20, 454, label, 10)

text(705, 374, "Radar signal connection", 14, True)
text(705, 351, "J_RADAR pin 3 -> 1k -> GPIO33 (pad 9)", 12)
text(705, 329, "GPIO33 -> 100k -> GND", 12)
text(705, 307, "GPIO33: input; no pull-up while radar is off.", 11)
text(705, 285, "RCWL 3V3 and CDS: leave unconnected.", 11)
text(705, 263, "All board and sensor grounds connect together.", 11)
text(705, 229, "Use the module's printed pin names;", 11, True)
text(705, 210, "connector numbering above is our PCB assignment.", 11)

wire((40, 172), (1060, 172))
text(40, 147, "Both MOSFETs: 1 = gate, 2 = source, 3 = drain. Match the symbol pins to the SOT-23 pads.", 12, True)
text(40, 124, "Use FDN340P only on this regulated 5 V rail. Keep AO3401A in the existing 9 V input-protection circuit.", 11)
text(40, 103, "Remove/rewire the old MOSFET directly between 3V3 and GND; that connection shorts the supply when enabled.", 11)
text(40, 82, "Selected: 3-pin, 2.54 mm pitch; Tronic TA0007 reference. Verify the purchased header against its PCB footprint.", 11)
text(40, 51, "Reference: onsemi FDN340P and FDV303N datasheets; SparkFun RCWL-0516 schematic. See the companion wiring guide for links.", 10, color=MUTED)
text(40, 32, "Wiring reference, not an EasyEDA project or a bench-tested circuit. Drawn 2026-09-20.", 10, color=MUTED)
c.showPage()
c.save()
doc = pymupdf.open(PDF)
doc[0].get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4), alpha=False).save(OUT / "radar_power_switch_tronic.png")
print(PDF)
print(OUT / "radar_power_switch_tronic.png")
