"""Draw the main-PCB connector circuit for an external DFPlayer Mini module."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import pymupdf

OUT = Path(__file__).resolve().parent
PDF = OUT / "dfplayer_circuit.pdf"
c = canvas.Canvas(str(PDF), pagesize=(1200, 900))
c.setTitle("DFPlayer Mini connector circuit - ESP32 and PAM8403")
INK = colors.HexColor("#16344A")
WIRE = colors.HexColor("#157968")
PALE = colors.HexColor("#EFF5F7")
MUTED = colors.HexColor("#526877")


def text(x, y, value, size=12, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, value)


def wire(*points):
    c.setStrokeColor(WIRE)
    c.setLineWidth(1.7)
    p = c.beginPath()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    c.drawPath(p)


def dot(x, y):
    c.setFillColor(WIRE)
    c.circle(x, y, 3, fill=1, stroke=0)


def box(x, y, w, h):
    c.setStrokeColor(colors.HexColor("#ADC4CD"))
    c.setFillColor(PALE)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=1)


def ground(x, y):
    wire((x, y), (x, y-8))
    for step, width in ((8, 12), (13, 8), (18, 4)):
        wire((x-width, y-step), (x+width, y-step))


def arrow(x, y, direction=1):
    wire((x-7*direction, y+5), (x, y), (x-7*direction, y-5))


def capacitor(x, top, bottom, ref, value, polarized=False):
    mid = (top+bottom)/2
    wire((x, top), (x, mid+4))
    wire((x-12, mid+4), (x+12, mid+4))
    wire((x-12, mid-4), (x+12, mid-4))
    wire((x, mid-4), (x, bottom))
    if polarized:
        text(x-29, mid+12, "+", 16, True)
    text(x+19, mid+7, ref, 11, True)
    text(x+19, mid-10, value, 11)


text(40, 855, "DFPlayer Mini: power, UART and audio", 25, True)
text(40, 830, "External ready-made module | ESP32-WROOM-32 | Existing PAM8403 amplifier module", 13)
text(40, 790, "DRAW THIS ON YOUR PCB", 14, True)
text(812, 790, "EXTERNAL DFPLAYER MINI", 14, True)

# Connector and module are logical pin blocks, not physical placement drawings.
box(640, 525, 55, 220)
text(580, 762, "J_DF: 4-pin connector", 13, True)
box(810, 475, 340, 300)
text(827, 747, "DFPlayer Mini", 18, True)
text(827, 724, "Connect by the module's printed labels", 11)
rows = [(1, 700, "VCC  (module pin 1)"),
        (2, 650, "GND  (module pin 7 or 10)"),
        (3, 600, "RX     (module pin 2)"),
        (4, 550, "TX     (module pin 3)")]
for pin, y, label in rows:
    text(659, y+8, str(pin), 12, True)
    wire((640, y), (695, y), (810, y))
    text(827, y-4, label, 13, True)
    dot(665, y)
text(827, 504, "Unused control pins: leave open", 11)

# 5 V bypass capacitors. The GND symbols represent the same board ground.
text(55, 714, "+5V regulated", 14, True)
wire((55, 700), (640, 700))
for x in (235, 435):
    dot(x, 700)
capacitor(235, 700, 649, "C_DF1", "100nF (0.1uF), 0805")
capacitor(435, 700, 649, "C_DF2", "100uF, 25V", True)
ground(235, 649)
ground(435, 649)
wire((602, 650), (640, 650))
ground(602, 650)

# UART directions refer to ESP32, not to the connector pin number.
text(55, 612, "GPIO17 / ESP TX", 13, True)
text(55, 580, "ESP32 module pad 28", 10)
wire((55, 600), (283, 600))
c.setStrokeColor(WIRE)
c.rect(283, 594, 54, 12, fill=0, stroke=1)
wire((337, 600), (640, 600))
text(285, 616, "R_DF1", 11, True)
text(350, 586, "1k, 0805", 11)
arrow(755, 600, 1)

text(55, 562, "GPIO16 / ESP RX", 13, True)
text(55, 530, "ESP32 module pad 27", 10)
wire((55, 550), (640, 550))
arrow(755, 550, -1)

text(45, 489, "One common GND for ESP32, DFPlayer and amplifier.", 12, True)
text(45, 468, "Place bypass capacitors close to J_DF; retain local decoupling at the DFPlayer.", 11)
text(45, 445, "Cable ends follow labels above. Connector pin 3 goes to module RX pin 2.", 11)

# Separate audio view: the same external DFPlayer feeds the existing amplifier.
wire((40, 416), (1160, 416))
text(40, 392, "EXTERNAL AUDIO CONNECTIONS - SAME DFPLAYER MODULE", 14, True)
box(55, 195, 280, 160)
text(72, 327, "DFPlayer Mini", 16, True)
text(72, 302, "DAC_L (pin 5)", 12, True)
text(72, 264, "GND", 12, True)
text(72, 225, "SPK1 / SPK2: leave unused", 11)
box(620, 195, 300, 160)
text(637, 327, "PAM8403 module", 16, True)
text(637, 302, "L / L_IN", 12, True)
text(637, 264, "Input GND", 12, True)
wire((335, 300), (620, 300))
wire((335, 260), (620, 260))
text(385, 315, "Analogue audio cable", 11)

# Amplifier supply is explicit and independent of the analogue input cable.
text(420, 224, "+5V", 12, True)
wire((455, 225), (620, 225))
text(637, 221, "VCC / +", 12, True)
text(420, 190, "GND", 12, True)
wire((455, 190), (555, 190), (555, 207), (620, 207))
text(637, 203, "Power GND", 10)

text(872, 299, "L+", 12, True)
text(872, 259, "L-", 12, True)
box(1040, 243, 115, 75)
text(1050, 283, "Speaker", 13, True)
wire((920, 300), (1040, 300))
wire((920, 260), (1040, 260))
text(935, 219, "Neither wire goes to GND", 10)

text(45, 157, "J_DF: Tronic TA0422 / XH-4PX-150MM. R_DF1: RU0043. C_DF1: CP0043. C_DF2: CA0195.", 11, True)
text(45, 134, "Also place 100nF + 100uF at the PAM8403 supply; use the ready-made module's analogue input.", 11)
text(45, 112, "C_DF2 is polarized: positive to +5V, negative to GND. All four J_DF pins are used.", 11)
text(45, 90, "Firmware UART: 9600 baud, 8N1, RX = GPIO16, TX = GPIO17. Use unique R/C/J references in your project.", 11)
text(45, 58, "Source: DFRobot DFR0299 documentation and manufacturer pin table; Diodes PAM8403 datasheet. See companion guide for links.", 10, color=MUTED)
text(45, 39, "Pin-wiring reference, not a physical module layout or an imported EasyEDA project. Connector footprint must match the purchased part.", 10, color=MUTED)
c.showPage()

# A directly usable list of actual EasyEDA catalogue entries, distinct from retail SKUs.
text(40, 850, "DFPlayer circuit: exact EasyEDA library names", 25, True)
text(40, 824, "Click a blue component name to open its EasyEDA page, then use Open in Editor.", 13)
text(40, 793, "Select Symbol for library searches. Module symbols can show external wiring; their footprints are not on the main PCB.", 12)
entries = [
    ("External DFPlayer module", "DFPlayer Mini", "DFPlayer Mini", "https://easyeda.com/component/DFPlayer_Mini-5dc49a1020904ea4b2f1a24056d818e6"),
    ("J_DF: 4-pin, 2.54mm", "XH2.54-4P_C9900010451", "CONN-TH_XH2.54-4P-1", "https://easyeda.com/component/5181c02118d34f8b87505d73950466a3"),
    ("R_DF1: 1k resistor", "0805W8F1001T5E", "R0805", "https://easyeda.com/component/8aebd62994a05a89b2fc1c520ce2e64f"),
    ("C_DF1: 100nF, 50V", "CL21B104KBCNNNC", "C0805", "https://easyeda.com/component/c58e33efcd08c9c01df888e6a177ba93"),
    ("C_DF2: 100uF, 25V", "100uF 25V SMD", "CAPAE660X800N", "https://easyeda.com/component/ce76aea22f6445788a2582a1bbb24b79"),
    ("External amplifier reference", "AMPLIFIER-PAM8403", "AMPLIFIER-PAM8403", "https://easyeda.com/component/c39b9ae17ad0475fab86e6e84e910dd8"),
]
text(45, 747, "Circuit item", 13, True)
text(350, 747, "Exact component name", 13, True)
text(820, 747, "Linked package", 13, True)
for i, (purpose, title, package, url) in enumerate(entries):
    y = 700-i*63
    text(45, y, purpose, 12)
    text(350, y, title, 14, True, colors.HexColor("#1260A4"))
    text(820, y, package, 12)
    c.linkURL(url, (348, y-4, 800, y+18), relative=0)
    c.setStrokeColor(colors.HexColor("#D6E1E6"))
    c.setLineWidth(.6)
    c.line(40, y-19, 1155, y-19)
text(45, 312, "J_DF uses FOUR pins: +5V, GND, DFPlayer RX and DFPlayer TX.", 15, True)
text(45, 287, "Tronic reference: TA0422 / XH-4PX-150MM. Match the actual purchased header's footprint.", 12)
text(45, 265, "Listed footprint verified: 2.54 mm pitch, 7.62 mm pin span, 1.10 mm holes; check housing fit.", 12)
text(45, 230, "Tronic purchases: TA0422 connector; RU0043 resistor; CP0043 100nF; CA0195 100uF.", 12, True)
text(45, 207, "Generic Tronic parts are not confirmed to be the same brand as the library entries. Check the electrolytic pads too.", 12)
text(45, 171, "Verified via EasyEDA API: connector, resistor and both capacitors have a symbol plus linked footprint.", 11)
text(45, 150, "Module titles/packages verified from public EasyEDA entries; their full pin-to-pad mapping is not reviewed.", 11)
text(45, 111, "DFPlayer contributor: cKDVP7pjB. 100uF capacitor contributor: Prado1.", 11)
text(45, 90, "These are real EasyEDA library entries. Import and placement in your running editor have not been tested.", 11)
c.showPage()
c.save()
doc = pymupdf.open(PDF)
doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(OUT / "dfplayer_circuit.png")
doc[1].get_pixmap(matrix=pymupdf.Matrix(1.25, 1.25), alpha=False).save(OUT / "dfplayer_easyeda_parts.png")
print(PDF)
print(OUT / "dfplayer_circuit.png")
