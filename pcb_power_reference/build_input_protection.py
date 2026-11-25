"""Draw the nominal-9-V input reverse-polarity protection wiring reference."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import pymupdf

OUT = Path(__file__).resolve().parent
PDF = OUT / "input_protection.pdf"
W, H = 1050, 710
c = canvas.Canvas(str(PDF), pagesize=(W, H))
c.setTitle("9 V input protection after SW3")
INK = colors.HexColor("#15354A")
WIRE = colors.HexColor("#176D66")
MUTED = colors.HexColor("#596F7D")
PALE = colors.HexColor("#EDF5F5")

def text(x, y, s, size=12, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, s)

def centered(x, y, s, size=12, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawCentredString(x, y, s)

def line(x1, y1, x2, y2, color=WIRE, width=2):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)

def dot(x, y):
    c.setFillColor(WIRE)
    c.circle(x, y, 3, stroke=0, fill=1)

def ground(x, y):
    line(x, y, x, y-8)
    line(x-12, y-8, x+12, y-8)
    line(x-8, y-13, x+8, y-13)
    line(x-4, y-18, x+4, y-18)
    centered(x, y-36, "GND", 11)

def triangle(points, color=WIRE):
    p = c.beginPath()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    p.close()
    c.setStrokeColor(color)
    c.setLineWidth(1.8)
    c.drawPath(p, fill=0, stroke=1)

text(40, 665, "9 V input protection after SW3", 25, True)
text(40, 640, "For protection against reversed supply polarity. Nominal 9 V input; retain the board's 10 V maximum.", 12)

# The jack's physical pin numbers cannot be determined from its generic symbol.
text(60, 515, "U4: verified positive contact", 12, True)
text(60, 495, "9 V supply +", 12)
line(72, 455, 220, 455)
c.setStrokeColor(WIRE)
c.setFillColor(colors.white)
c.circle(72, 455, 4, fill=1, stroke=1)
line(220, 455, 257, 477)
line(267, 455, 420, 455)
for x in (220, 267):
    c.circle(x, 455, 3, fill=1, stroke=1)
centered(245, 530, "SW3", 13, True)
centered(245, 510, "SPST", 11)
centered(342, 475, "BAT_SW", 12, True)

text(60, 388, "U4: verified return contact", 12, True)
line(72, 360, 115, 360)
c.setStrokeColor(WIRE)
c.setFillColor(colors.white)
c.circle(72, 360, 4, fill=1, stroke=1)
line(115, 360, 115, 331)
ground(115, 331)

# Rotated P-channel MOSFET: D input, S output, gate below.
line(420, 455, 420, 420)
line(500, 420, 500, 455)
for a, b in ((420, 441), (449, 471), (479, 500)):
    line(a, 420, b, 420, width=2.5)
line(426, 407, 494, 407, width=2.5)
line(460, 407, 460, 402)
c.setStrokeColor(WIRE)
c.setFillColor(colors.white)
c.circle(460, 398, 4, fill=1, stroke=1)
line(460, 394, 460, 320)
text(384, 429, "3 D", 12, True)
text(511, 429, "S 2", 12, True)
text(473, 376, "G 1", 12, True)
centered(460, 576, "Q1  AO3401A", 16, True)
centered(460, 555, "P-channel MOSFET | SOT-23", 12)
centered(460, 535, "LCSC C15127", 11)

# Intrinsic body diode, explicitly labelled as internal (not an added part).
line(420, 455, 420, 487, MUTED, 1.4)
line(420, 487, 446, 487, MUTED, 1.4)
triangle([(446, 479), (461, 487), (446, 495)], MUTED)
line(463, 477, 463, 497, MUTED, 1.4)
line(463, 487, 500, 487, MUTED, 1.4)
line(500, 487, 500, 455, MUTED, 1.4)
centered(460, 507, "internal diode", 10, color=MUTED)
dot(420, 455)
dot(500, 455)

line(500, 455, 970, 455)
dot(650, 455)
text(824, 478, "BAT_P", 16, True, WIRE)
text(787, 430, "Protected battery rail", 12)
text(787, 407, "To AP63205 VIN (3), EN (2)", 12)
text(787, 387, "and its input capacitors", 12)
text(787, 367, "Battery ADC divider also starts here", 11)

# Zener: cathode at source rail, anode at gate. Bent cathode bar points up.
line(650, 455, 650, 377)
line(638, 383, 638, 377)
line(638, 377, 662, 377)
line(662, 377, 662, 371)
triangle([(638, 350), (662, 350), (650, 374)])
line(650, 350, 650, 320)
line(460, 320, 650, 320)
dot(460, 320)
text(672, 390, "K / band", 11, True)
text(672, 344, "A", 11, True)
text(547, 282, "DZ1  8.2 V Zener", 13, True)
text(547, 263, "BZT52C8V2-7-F | C500790", 11)
text(547, 244, "K to source; A to gate", 11)

# Gate pull-down resistor.
line(460, 320, 460, 289)
c.setStrokeColor(WIRE)
c.setLineWidth(2)
c.rect(453, 251, 14, 38, stroke=1, fill=0)
line(460, 251, 460, 224)
ground(460, 224)
text(340, 274, "R5  100 kOhm", 12, True)
text(330, 255, "0805 | C149504", 11)
text(300, 236, "0805W8F1003T5E", 10)

# Concise connections and BOM directly on the drawing.
line(40, 168, 1010, 168, colors.HexColor("#B8CBD1"), .8)
text(40, 145, "MOVE BAT_P to the source/output side of Q1. Use a different net name (BAT_SW) before Q1.", 12, True)
text(40, 124, "AO3401A pin map: 1 = gate, 2 = source, 3 = drain. Orient by pin numbers when placing the EasyEDA symbol.", 11)
text(40, 103, "U4: check the actual jack datasheet. The third contact is usually switched; leave it unused unless needed.", 11)
text(40, 82, "The Zener protects the MOSFET gate; BAT_P remains approximately the battery voltage, not 8.2 V.", 11)
text(40, 48, "Drawing reference for a single battery supply; not an EasyEDA project or a simulated/bench-tested circuit.", 10, color=MUTED)
text(40, 31, "Basis: AO3401A datasheet; Diodes BZT52Cxx datasheet; TI SNOAA23A, Figure 2.", 10, color=MUTED)
c.showPage()
c.save()
doc = pymupdf.open(PDF)
doc[0].get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6), alpha=False).save(OUT / "input_protection.png")
print(PDF)
print(OUT / "input_protection.png")
