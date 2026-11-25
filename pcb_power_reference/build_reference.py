"""Generate a review-only PCB power reference, PDF and PNG, without EDA claims."""
from pathlib import Path
import math
import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
import pymupdf

OUT = Path(__file__).resolve().parent
PDF = OUT / 'pcb_power_reference.pdf'
W, H = landscape(A3)
INK = colors.HexColor('#123142')
WIRE = colors.HexColor('#245E71')
MUTED = colors.HexColor('#526878')
LIGHT = colors.HexColor('#EAF0F3')
WARN = colors.HexColor('#FFF1D6')
c = canvas.Canvas(str(PDF), pagesize=(W, H))
c.setTitle('PCB power reference - parallel 5 V / 3.3 V buck regulators')
c.setAuthor('Project design reference')

def text(x,y,s,size=10,font='Helvetica',color=INK):
    c.setFillColor(color); c.setFont(font,size); c.drawString(x,y,s)

def center(x,y,s,size=10,font='Helvetica',color=INK):
    c.setFillColor(color); c.setFont(font,size); c.drawCentredString(x,y,s)

def line(x1,y1,x2,y2,width=1.4,color=WIRE):
    c.setStrokeColor(color); c.setLineWidth(width); c.line(x1,y1,x2,y2)

def dot(x,y):
    c.setFillColor(WIRE); c.circle(x,y,2.5,stroke=0,fill=1)

def ground(x,y):
    line(x,y,x,y-6); line(x-9,y-6,x+9,y-6)
    line(x-6,y-10,x+6,y-10); line(x-3,y-14,x+3,y-14)

def box(x,y,w,h,fill=None):
    c.setStrokeColor(colors.HexColor('#BCCBD3')); c.setLineWidth(.8)
    if fill: c.setFillColor(fill)
    c.roundRect(x,y,w,h,7,stroke=1,fill=bool(fill))

def panel(x,y,w,h,title):
    box(x,y,w,h)
    text(x+14,y+h-21,title,12,'Helvetica-Bold')

def capv(x,top,bottom,label,ycap=None):
    mid = (top+bottom)/2 if ycap is None else ycap
    line(x,top,x,mid+4); line(x-8,mid+4,x+8,mid+4)
    line(x-8,mid-4,x+8,mid-4); line(x,mid-4,x,bottom)
    if label:
        for i,s in enumerate(label): center(x,mid-21-11*i,s,8.5)

def rh(x1,x2,y,label,sub=''):
    left=(x1+x2)/2-21; right=left+42
    line(x1,y,left,y); line(right,y,x2,y)
    c.setStrokeColor(WIRE); c.setLineWidth(1.4); c.rect(left,y-6,42,12,stroke=1,fill=0)
    center((x1+x2)/2,y+15,label,10,'Helvetica-Bold')
    if sub: center((x1+x2)/2,y-22,sub,9)

def rv(x,top,bottom,label):
    mid=(top+bottom)/2
    line(x,top,x,mid+18); line(x,mid-18,x,bottom)
    c.setStrokeColor(WIRE); c.setLineWidth(1.4); c.rect(x-6,mid-18,12,36,stroke=1,fill=0)
    for i,s in enumerate(label): text(x+13,mid+5-12*i,s,9)

def inductor(x1,x2,y):
    lead=5; line(x1,y,x1+lead,y); line(x2-lead,y,x2,y)
    radius=(x2-x1-2*lead)/8
    for i in range(4):
        c.setStrokeColor(WIRE); c.setLineWidth(1.4)
        c.arc(x1+lead+i*radius*2,y-radius,x1+lead+(i+1)*radius*2,y+radius,0,180)

def net(x,y,name,up=True):
    text(x,y+8 if up else y-16,name,10,'Helvetica-Bold',WIRE)

def header(page,title,subtitle):
    text(36,H-43,title,23,'Helvetica-Bold')
    text(36,H-63,subtitle,10.5,color=MUTED)
    box(36,H-107,W-72,29,WARN)
    text(47,H-96,'REFERENCE DESIGN - check load budget, regulator thermal limits and ADC power sequencing before fabrication.',11,'Helvetica-Bold')
    line(36,48,W-36,48,.8,colors.HexColor('#BCCBD3'))
    text(36,31,'20 Sep 2026  |  Drawing reference only; not an EasyEDA project, simulation or fabrication approval.',9,color=MUTED)
    text(W-105,31,f'Sheet {page} / 2',9,color=MUTED)

def buck(x,y,ref,part,lcsc,vout,ind,cref,lref):
    panel(x,y,549,245,f'{vout} regulator  |  {ref} {part}  |  {lcsc}')
    # Named VIN_BAT connects to the protected battery rail on this sheet.
    vin=y+166; sw=y+142
    line(x+30,vin,x+218,vin); net(x+30,vin,'VIN_BAT')
    for xx in (x+72,x+135): dot(xx,vin)
    capv(x+72,vin,y+78,None,y+133); ground(x+72,y+78)
    capv(x+135,vin,y+78,None,y+133); ground(x+135,y+78)
    text(x+84,y+115,cref+'A',8.5); text(x+147,y+115,cref+'B',8.5)
    text(x+84,y+104,'10 uF',8.5); text(x+147,y+104,'100 nF',8.5)
    text(x+14,y+50,'CIN: 10 uF + 100 nF; both 25 V X7R',9)
    # Symbol location does not imply footprint ordering; every terminal is numbered.
    box(x+218,y+101,108,94,LIGHT)
    text(x+228,y+163,'3  VIN',10,'Helvetica-Bold')
    text(x+228,y+128,'2  EN',10,'Helvetica-Bold')
    text(x+276,y+176,'BST  6',10,'Helvetica-Bold')
    text(x+278,y+139,'SW  5',10,'Helvetica-Bold')
    text(x+282,y+112,'FB  1',10,'Helvetica-Bold')
    text(x+287,y+82,'4  GND',10,'Helvetica-Bold')
    line(x+195,vin,x+195,y+131); line(x+195,y+131,x+218,y+131); dot(x+195,vin)
    line(x+272,y+101,x+272,y+66); ground(x+272,y+66)
    line(x+326,y+179,x+356,y+179)
    capv(x+356,y+179,sw,None,y+163); dot(x+356,sw)
    text(x+341,y+205,cref+'C  100 nF',9)
    line(x+326,sw,x+382,sw)
    inductor(x+382,x+442,sw)
    center(x+412,y+171,lref+'  '+ind,9,'Helvetica-Bold')
    line(x+442,sw,x+530,sw); net(x+497,sw,vout)
    # FB returns to output AFTER L, not to SW.
    line(x+326,y+115,x+452,y+115); line(x+452,y+115,x+452,sw); dot(x+452,sw)
    text(x+352,y+102,'FB = output after L',8.5)
    for xx,suffix in ((x+480,'D'),(x+522,'E')):
        dot(xx,sw); capv(xx,sw,y+66,None,y+106); ground(xx,y+66)
        center(xx,y+84,cref+suffix,8.5)
    text(x+440,y+37,'2 x 22 uF / 10 V X7R',9)
    text(x+14,y+35,'Shielded inductor: Isat >= 3.5 A; Irms >= 2.7 A;',9)
    text(x+14,y+21,'DCR < 100 mOhm. Check effective capacitance under DC bias.',9)

header(1,'Battery power and measurement reference','Parallel fixed-output buck regulators. Assumed rectangular 9 V battery, protected input <= 10 V. Common GND throughout.')

# INPUT / REVERSE POLARITY PROTECTION
panel(36,592,W-72,127,'Input disconnect and reverse-polarity protection')
box(53,629,62,48,LIGHT)
text(64,680,'J1 BATTERY',9,'Helvetica-Bold')
text(60,660,'1  +',10,'Helvetica-Bold'); text(60,638,'2  -',10,'Helvetica-Bold')
line(115,663,180,663)
line(180,663,205,663); line(205,663,230,677); line(235,663,280,663)
c.setStrokeColor(WIRE); c.circle(205,663,2,stroke=1,fill=0); c.circle(235,663,2,stroke=1,fill=0)
center(217,686,'S1 SPST',10,'Helvetica-Bold')
line(94,629,94,616); ground(94,616)
# Q1 rotated P-channel MOSFET: D on battery side, S on protected side.
line(280,663,300,663); line(300,663,300,651)
line(356,651,356,663); line(356,663,434,663)
for a,b in ((300,315),(321,335),(341,356)): line(a,651,b,651,2)
line(307,641,349,641,1.8); line(328,641,328,634)
c.setStrokeColor(WIRE); c.circle(328,631,3,stroke=1,fill=0)
line(328,628,328,624)
rh(328,434,624,'R1  100 kOhm')
line(434,624,434,614); ground(434,614)
text(283,649,'D',10,'Helvetica-Bold'); text(362,649,'S',10,'Helvetica-Bold'); text(310,622,'G',10,'Helvetica-Bold')
text(273,675,'3',9,'Helvetica-Bold'); text(370,675,'2',9,'Helvetica-Bold'); text(313,610,'1',9,'Helvetica-Bold')
# Intrinsic body diode: anode at D, cathode at S; left -> right.
line(300,663,300,684); line(300,684,320,684)
p=c.beginPath(); p.moveTo(320,677); p.lineTo(334,684); p.lineTo(320,691); p.close()
c.setStrokeColor(WIRE); c.drawPath(p,stroke=1,fill=0)
line(336,676,336,692); line(336,684,356,684); line(356,684,356,663)
dot(300,663); dot(356,663)
text(468,681,'Q1 AO3401A  |  C15127  |  SOT-23',11,'Helvetica-Bold')
text(468,664,'Pin 3 drain = switched battery +; pin 2 source = VIN_BAT.',10)
text(468,649,'Pin 1 gate -> 100 kOhm -> GND. Body diode points D -> S.',10)
text(468,633,'The reversed D/S orientation is intentional for polarity protection.',10,'Helvetica-Bold')
line(434,663,448,663); net(403,663,'VIN_BAT')
# Input bulk drawn separately on named net to avoid clutter at Q1.
line(986,670,1099,670); net(992,676,'VIN_BAT')
capv(1037,670,628,None,651); ground(1037,628)
text(1060,652,'C1 optional',9,'Helvetica-Bold'); text(1060,639,'47 uF / 25 V',9)
text(988,610,'Place near input connector.',8.5)

buck(36,332,'U3','AP63205WU-7','C2071056','+5V','4.7 uH','C2','L1')
buck(605,332,'U4','AP63203WU-7','C780769','+3V3','3.9 uH','C3','L2')

# ADC DIVIDER
panel(36,88,549,226,'Battery measurement  |  ESP32 GPIO35 / ADC1_CH7')
line(59,246,108,246); net(58,246,'VIN_BAT')
rh(108,262,246,'R2  100 kOhm','1%')
dot(262,246); line(262,246,471,246); net(340,249,'BAT_ADC')
rv(262,232,164,['R3','27 kOhm','1%']); line(262,246,262,232); ground(262,164)
dot(371,246); capv(371,246,164,['C4','100 nF'],211); ground(371,164)
box(471,224,94,47,LIGHT); text(480,253,'ESP32',10,'Helvetica-Bold'); text(480,238,'GPIO35',10)
text(460,209,'WROOM module pad 7',9)
text(51,134,'VIN_BAT = VADC x 127 / 27  (nominal ratio 4.7037).',10,'Helvetica-Bold')
text(51,118,'9 V -> 1.913 V at ADC; 10 V -> 2.126 V at ADC.',10)
text(51,102,'Configure and calibrate the ADC; this measures the protected input rail.',9)

panel(605,88,549,226,'Scope, sequencing and PCB placement')
notes=[
 '5 V sensor/audio rail only. 10 W LED removed from current design.',
 'Each buck IC is rated 2 A; available battery/system power is unverified.',
 'Do not assume a rectangular 9 V battery can deliver either rail rating.',
 'S1 disconnects the supply and battery divider together.',
 'Do not independently disable ESP32 3.3 V while its divider remains live.',
 'ADC power-up/down sequencing and any required isolation need review.',
 'Place VIN ceramic decoupling immediately at each buck VIN/GND pair.',
 'Keep SW copper small; route FB away from SW and inductors.',
 'Keep BAT_ADC away from inductors; place C4 beside the ESP32 input.',
 'Add 10 uF + 100 nF beside ESP32; follow its supply/layout guide.',
 'Recommended U4 replaces AMS1117; do not populate both on +3V3.',
]
for i,s in enumerate(notes): text(619,278-i*16,s,9.7)
c.showPage()

header(2,'Pin map, values and design review','Supporting details for the exact nets shown on sheet 1. Part availability and footprint validation remain assembly checks.')

def table(x,y,width,headers,rows,colwidths,row_h=25):
    c.setFillColor(LIGHT); c.rect(x,y-row_h,width,row_h,stroke=0,fill=1)
    xx=x
    for h,cw in zip(headers,colwidths): text(xx+8,y-17,h,10,'Helvetica-Bold'); xx+=cw
    yy=y-row_h
    for row in rows:
        line(x,yy,x+width,yy,.5,colors.HexColor('#CAD5DB'))
        xx=x
        for s,cw in zip(row,colwidths): text(xx+8,yy-17,str(s),9.7); xx+=cw
        yy-=row_h
    line(x,yy,x+width,yy,.5,colors.HexColor('#CAD5DB'))
    return yy

text(36,711,'BUCK REGULATOR PIN MAP - same pinout for U3 and U4',12,'Helvetica-Bold')
table(36,699,680,['Pin','Name','Connection'],[
 ['1','FB','Directly to its output after inductor: +5V (U3) or +3V3 (U4)'],
 ['2','EN','VIN_BAT; both rails enabled together while battery switch is on'],
 ['3','VIN','VIN_BAT; each IC has its own local input capacitors'],
 ['4','GND','Common GND; compact, low-impedance return'],
 ['5','SW','Inductor input and lower terminal of 100 nF bootstrap capacitor'],
 ['6','BST','Upper terminal of 100 nF bootstrap capacitor'],
 ],[55,65,560])
text(744,711,'SELECTED REGULATORS',12,'Helvetica-Bold')
for i,s in enumerate([
 'U3: AP63205WU-7, fixed 5 V',
 'LCSC C2071056; L1 = 4.7 uH',
 'U4: AP63203WU-7, fixed 3.3 V',
 'LCSC C780769; L2 = 3.9 uH',
 'Both SOT-26 / TSOT-26 package family.',
 'Confirm manufacturer package drawing',
 'against the chosen PCB footprint.',
 ]): text(744,687-i*20,s,10)

text(36,491,'SUPPLY / DIVIDER NET MAP',12,'Helvetica-Bold')
table(36,479,W-72,['Node or device','Exact connection / purpose'],[
 ['J1 pin 1','Battery positive -> S1 -> Q1 drain, pin 3'],
 ['J1 pin 2','Common GND'],
 ['Q1 source, pin 2','VIN_BAT: feeds both buck VIN / EN pairs and the ADC divider'],
 ['Q1 gate, pin 1','100 kOhm to GND; Q1 = AO3401A / LCSC C15127'],
 ['BAT_ADC','100 kOhm from VIN_BAT; 27 kOhm and 100 nF to GND'],
 ['ESP32 module pad 7','GPIO35 / ADC1_CH7; input only; connect to BAT_ADC'],
 ['+5V','Sensor / audio supply reference; excludes the 10 W LED'],
 ['+3V3','ESP32 and compatible 3.3 V loads; 10 uF + 100 nF beside ESP32'],
 ],[200,W-272],22)

panel(36,126,548,143,'Components and assumptions to verify')
for i,s in enumerate([
 'Assumed input range: project 9 V battery; maximum <= 10 V.',
 'Per buck: CIN 10 uF / 25 V X7R + 100 nF / 25 V X7R.',
 'Per buck: COUT 2 x 22 uF / 10 V X7R; CBST 100 nF.',
 'Verify usable capacitor value after DC bias, temperature and tolerance.',
 'Check L1/L2 current rating, saturation margin, DCR and temperature rise.',
 'Load budget, battery sag/runtime and board thermal performance are open.',
 ]): text(50,231-i*17,s,9.5)

panel(605,126,549,143,'Existing AMS1117-3.3 review - not in the recommended circuit')
for i,s in enumerate([
 'U2 C2992570: reported IQ 4 mA typical / 8 mA maximum.',
 '10 mA minimum load is specified for guaranteed regulation conditions.',
 'Its vendor reference calls for 10 uF tantalum IN and 22 uF tantalum OUT.',
 'Capacitor technology / ESR must follow the exact vendor datasheet.',
 'These constraints make it a poor deep-sleep battery choice here.',
 'Replace U2 with U4; do not connect both regulators to the same +3V3 rail.',
 ]): text(619,231-i*17,s,9.5)

text(36,108,'Manufacturer source: Diodes Incorporated AP63200 / AP63201 / AP63203 / AP63205 datasheet',9,'Helvetica-Bold')
url='https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf'
text(36,93,url,8.5,color=WIRE); c.linkURL(url,(36,90,600,103),relative=0)
text(36,73,'Review status: reference topology only. Verify all purchased-part datasheets, symbols, footprints and sequencing before release.',9,color=MUTED)
c.save()

with pymupdf.open(PDF) as doc:
    for i,page in enumerate(doc):
        page.get_pixmap(matrix=pymupdf.Matrix(1.8,1.8),alpha=False).save(OUT / f'pcb_power_reference_page_{i+1}.png')
print(PDF)
for p in sorted(OUT.glob('*.png')): print(p)
