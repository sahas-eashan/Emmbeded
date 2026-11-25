from pathlib import Path

import pymupdf
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
SOURCE_PDF = ROOT.parent / "Embedded_Review_3_Final.pdf"
STYLE_PDF = Path(r"C:\Users\Cyborg\Downloads\_Sep_week-03 VTLA Control for Human Interactive Manipulation.pdf")
PPTX_PATH = ROOT / "Bird_Repellent_Review3_Six_Slides.pptx"
ASSET_DIR = ROOT / "assets"
PHOTO_PATH = ASSET_DIR / "original_title_photo.png"
STYLE_BG_PATH = ASSET_DIR / "vtla_textured_background_clean.png"
STYLE_COVER_PATH = ASSET_DIR / "vtla_cover_background_clean.png"
STYLE_FONT_DIR = ASSET_DIR / "fonts"

SLIDE_W, SLIDE_H = 13.333, 7.5

# Palette sampled from the VTLA weekly-progress PDF.
BG = "F8F4F0"
BLACK = "14213D"
TEXT = "273043"
GRAY = "9AA6AD"
MID_GRAY = "586575"
LIGHT_GRAY = "EDF1F2"
RED = "185079"
CORAL = "2A7797"
PINK = "EAF5F7"
PALE_RED = "F2F8F9"
WHITE = "FFFFFF"
DISPLAY_FONT = "Arial"
BODY_FONT = "Arial"


def rgb(value):
    return RGBColor.from_string(value)


def set_fill(shape, color, transparency=0):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(color)
    if transparency:
        shape.fill.transparency = transparency


def set_line(shape, color=GRAY, width=1.4, transparency=0):
    shape.line.color.rgb = rgb(color)
    shape.line.width = Pt(width)
    if transparency:
        shape.line.transparency = transparency
    # An explicit empty effects list removes the default PowerPoint shadow.
    properties = shape._element.spPr
    if properties.find("{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst") is None:
        properties.append(OxmlElement("a:effectLst"))


def add_text(slide, x, y, w, h, text, size=16, color=TEXT, bold=False,
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.MIDDLE, margin=0.04,
             font=BODY_FONT):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgb(color)
    return shape


def add_box(slide, x, y, w, h, text, size=16, fill=WHITE, outline=GRAY,
            text_color=TEXT, bold=False, rounded=False, width=1.4):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    set_fill(shape, fill)
    set_line(shape, outline, width)
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.12)
    frame.margin_right = Inches(0.12)
    frame.margin_top = Inches(0.06)
    frame.margin_bottom = Inches(0.06)
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    paragraph = frame.paragraphs[0]
    paragraph.alignment = PP_ALIGN.CENTER
    run = paragraph.add_run()
    run.text = text
    run.font.name = BODY_FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgb(text_color)
    return shape


def process(slide, x, y, w, h, text, size=16, bold=False):
    return add_box(slide, x, y, w, h, text, size, WHITE, GRAY, TEXT, bold)


def red_process(slide, x, y, w, h, text, size=16):
    return add_box(slide, x, y, w, h, text, size, RED, RED, WHITE, True, width=1.7)


def terminator(slide, x, y, w, h, text, size=16):
    return add_box(slide, x, y, w, h, text, size, LIGHT_GRAY, GRAY, TEXT, False, True)


def decision(slide, x, y, w, h, text, size=14):
    shape = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(x), Inches(y), Inches(w), Inches(h))
    set_fill(shape, PINK)
    set_line(shape, RED, 1.5)
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.2)
    frame.margin_right = Inches(0.2)
    frame.margin_top = Inches(0.1)
    frame.margin_bottom = Inches(0.1)
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    paragraph = frame.paragraphs[0]
    paragraph.alignment = PP_ALIGN.CENTER
    run = paragraph.add_run()
    run.text = text
    run.font.name = BODY_FONT
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = rgb(TEXT)
    return shape


def _add_arrowhead(connector):
    line_element = connector.line._get_or_add_ln()
    for node in line_element.findall("{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd"):
        line_element.remove(node)
    tail = OxmlElement("a:tailEnd")
    tail.set("type", "triangle")
    tail.set("w", "sm")
    tail.set("len", "sm")
    line_element.append(tail)


def segment(slide, p1, p2, color=BLACK, width=1.6, arrow=False):
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(p1[0]), Inches(p1[1]), Inches(p2[0]), Inches(p2[1])
    )
    set_line(connector, color, width)
    if arrow:
        _add_arrowhead(connector)
    return connector


def path(slide, points, color=BLACK, width=1.6, arrow=True):
    for idx in range(len(points) - 1):
        segment(slide, points[idx], points[idx + 1], color, width, arrow and idx == len(points) - 2)


def branch_label(slide, x, y, label, color=MID_GRAY):
    add_text(slide, x, y, 0.7, 0.28, label, 12, color, True, PP_ALIGN.CENTER, margin=0)


def connector_ref(slide, x, y, letter, label, align=PP_ALIGN.LEFT):
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.42), Inches(0.42))
    set_fill(circle, RED)
    set_line(circle, RED, 1)
    frame = circle.text_frame
    frame.clear()
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    p = frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = letter
    r.font.name = BODY_FONT
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = rgb(WHITE)
    if label:
        if align == PP_ALIGN.LEFT:
            add_text(slide, x + 0.5, y - 0.02, 2.6, 0.46, label, 11, MID_GRAY, True, PP_ALIGN.LEFT, margin=0)
        else:
            add_text(slide, x - 2.65, y - 0.02, 2.55, 0.46, label, 11, MID_GRAY, True, PP_ALIGN.RIGHT, margin=0)
    return circle


def slide_base(slide, cover=False):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(BG)
    background = extract_style_background(cover)
    if background and background.exists():
        slide.shapes.add_picture(str(background), 0, 0, width=Inches(SLIDE_W), height=Inches(SLIDE_H))


def slide_header(slide, title):
    add_text(slide, 0.47, 0.5, 12.35, 0.7, title.upper(), 36, RED, False, margin=0, font=DISPLAY_FONT)


def section_label(slide, x, y, w, text, size=18):
    add_text(slide, x, y, w, 0.36, text, size, RED, True, PP_ALIGN.LEFT, margin=0, font=DISPLAY_FONT)


def footer(slide, number):
    add_text(slide, 12.25, 7.13, 0.45, 0.16, f"{number}/6", 8, RED, False, PP_ALIGN.RIGHT, margin=0)


def extract_style_background(cover=False):
    target = STYLE_COVER_PATH if cover else STYLE_BG_PATH
    if target.exists():
        return target
    ASSET_DIR.mkdir(exist_ok=True)
    if not STYLE_PDF.exists():
        return None
    document = pymupdf.open(STYLE_PDF)
    page = document[0 if cover else 7]
    # Keep the original gradient and paper images; remove text and vector marks.
    # Restore the sampled source page fill behind the preserved image layers.
    page.add_redact_annot(page.rect, fill=None)
    page.apply_redactions(images=0, graphics=2, text=0)
    page.draw_rect(page.rect, color=None, fill=(0.9843, 0.9647, 0.9451), overlay=False)
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(4 / 3, 4 / 3), alpha=False)
    pixmap.save(target)
    document.close()
    return target


def extract_style_fonts():
    """Extract the embedded VTLA fonts so PowerPoint can embed the exact typefaces."""
    expected = {
        221: STYLE_FONT_DIR / "CanvaSans-Regular.ttf",
        222: STYLE_FONT_DIR / "CanvaSans-Medium.ttf",
        223: STYLE_FONT_DIR / "CanvaSans-Bold.ttf",
    }
    if all(path.exists() for path in expected.values()):
        return list(expected.values())
    if not STYLE_PDF.exists():
        return []
    STYLE_FONT_DIR.mkdir(parents=True, exist_ok=True)
    document = pymupdf.open(STYLE_PDF)
    for xref, path in expected.items():
        font = document.extract_font(xref)
        path.write_bytes(font[3])
    return list(expected.values())


def extract_title_photo():
    if PHOTO_PATH.exists():
        return PHOTO_PATH
    ASSET_DIR.mkdir(exist_ok=True)
    document = pymupdf.open(SOURCE_PDF)
    page = document[0]
    candidates = []
    for image in page.get_images(full=True):
        xref, width, height = image[0], image[2], image[3]
        ratio = width / max(height, 1)
        if ratio > 1.25:
            candidates.append((width * height, xref))
    if not candidates:
        return None
    xref = max(candidates)[1]
    extracted = document.extract_image(xref)
    temp = ASSET_DIR / f"title_photo.{extracted['ext']}"
    temp.write_bytes(extracted["image"])
    if temp.suffix.lower() == ".png":
        temp.replace(PHOTO_PATH)
    else:
        pix = pymupdf.Pixmap(str(temp))
        pix.save(PHOTO_PATH)
    return PHOTO_PATH


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    blank = prs.slide_layouts[6]
    notes = []

    # 1 — VTLA cover artwork, title scale, alignment and blue palette.
    slide = prs.slides.add_slide(blank)
    slide_base(slide, cover=True)
    add_text(slide, 0.85, 0.55, 11.65, 0.92,
             "Bird Repellent System for Indoor\nand Swimming Pool Areas",
             26, RED, True, PP_ALIGN.CENTER, margin=0, font=DISPLAY_FONT)
    add_text(slide, 0.7, 2.13, 8.2, 1.2, "FIRMWARE",
             64, RED, False, margin=0, font=DISPLAY_FONT)
    add_text(slide, 0.7, 3.2, 9.8, 1.3, "FLOWCHARTS",
             78, RED, False, margin=0, font=DISPLAY_FONT)
    add_text(slide, 0.78, 4.58, 9.3, 0.32,
             "ESP32-WROOM-32E  ·  Interrupt Handling and Power Management",
             13, RED, True, margin=0, font=DISPLAY_FONT)
    add_text(slide, 0.76, 5.16, 4.0, 0.48, "REVIEW 03", 26, RED, True, margin=0, font=DISPLAY_FONT)
    add_text(slide, 0.76, 5.9, 6.2, 0.31, "220148G   Eashan S.G.S", 16, RED, True, margin=0)
    add_text(slide, 0.76, 6.22, 6.2, 0.31, "220362G   Liyanage D.L.B.B", 16, RED, True, margin=0)
    add_text(slide, 0.76, 6.54, 6.2, 0.31, "220381M   Manawadu M.D", 16, RED, True, margin=0)
    notes.append(
        "Our project is a bird repellent system for indoor and swimming-pool areas. "
        "This review presents the complete firmware behavior, with special attention to interrupts and power management. "
        "The controller uses radar and sound as the required evidence, with PIR as supporting evidence, before it activates a short deterrent sound."
    )

    # 2 — complete firmware map.
    slide = prs.slides.add_slide(blank)
    slide_base(slide)
    slide_header(slide, "Complete Firmware Flowchart")
    terminator(slide, 4.1, 1.48, 3.25, 0.48, "Power on / reset", 16)
    process(slide, 4.1, 2.16, 3.25, 0.64, "Outputs OFF; initialize events and timers", 15)
    process(slide, 4.1, 3.02, 3.25, 0.62, "Sensor warm-up  ≈ 60 s", 16)
    process(slide, 4.1, 3.86, 3.25, 0.62, "A  ·  Check health and pending events", 15, True)
    decision(slide, 4.45, 4.72, 2.55, 0.98, "Power + inputs OK?", 14)
    path(slide, [(5.73, 1.96), (5.73, 2.16)])
    path(slide, [(5.73, 2.8), (5.73, 3.02)])
    path(slide, [(5.73, 3.64), (5.73, 3.86)])
    path(slide, [(5.73, 4.48), (5.73, 4.72)])

    section_label(slide, 0.72, 1.6, 2.7, "Event entry", 17)
    process(slide, 0.72, 2.08, 2.65, 0.65, "Radar / PIR GPIO event", 14)
    red_process(slide, 0.72, 2.98, 2.65, 0.65, "ISR records + notifies task", 13)
    path(slide, [(2.05, 2.73), (2.05, 2.98)])
    path(slide, [(3.37, 3.31), (3.72, 3.31), (3.72, 4.17), (4.1, 4.17)], RED, 1.6)

    process(slide, 0.72, 4.84, 2.65, 0.74, "Outputs OFF\nFault / battery recovery  ·  Slide 6", 14)
    branch_label(slide, 3.7, 5.16, "NO")
    path(slide, [(4.45, 5.21), (3.37, 5.21)])
    connector_ref(slide, 1.83, 5.96, "A", "Recovered → main checks", PP_ALIGN.LEFT)
    path(slide, [(2.05, 5.58), (2.05, 5.96)], RED, 1.5)

    process(slide, 7.95, 1.76, 3.0, 0.67, "Confirm activity with fresh samples", 15)
    decision(slide, 8.25, 2.72, 2.35, 0.95, "Confirm?", 11)
    branch_label(slide, 7.35, 4.95, "YES")
    path(slide, [(7.0, 5.21), (7.45, 5.21), (7.45, 2.1), (7.95, 2.1)])
    path(slide, [(9.43, 2.43), (9.43, 2.72)])
    red_process(slide, 7.75, 4.18, 2.95, 0.78, "Deterrent burst + cooldown\nSlide 3", 14)
    branch_label(slide, 8.55, 3.79, "YES")
    path(slide, [(9.43, 3.67), (9.43, 4.18)], RED, 1.7)
    connector_ref(slide, 9.22, 5.34, "A", "")
    path(slide, [(9.43, 4.96), (9.43, 5.34)], RED, 1.5)

    decision(slide, 10.65, 2.72, 1.85, 0.95, "Sleep?", 11)
    branch_label(slide, 10.42, 2.92, "NO")
    path(slide, [(10.6, 3.2), (10.65, 3.2)])
    process(slide, 10.85, 4.18, 2.05, 0.78, "Light sleep + wake\nSlide 5", 13)
    branch_label(slide, 11.52, 3.79, "YES")
    path(slide, [(11.58, 3.67), (11.58, 4.18)])
    connector_ref(slide, 11.62, 5.34, "A", "")
    path(slide, [(11.83, 4.96), (11.83, 5.34)], RED, 1.5)
    connector_ref(slide, 12.75, 2.99, "A", "")
    branch_label(slide, 12.32, 2.76, "NO")
    path(slide, [(12.5, 3.2), (12.75, 3.2)])
    add_text(slide, 0.75, 6.65, 11.8, 0.32,
             "Connector A always returns to “Check health and pending events.”  The detailed paths appear on Slides 3–6.",
             12, MID_GRAY, True, PP_ALIGN.CENTER, margin=0)
    notes.append(
        "Power-on starts with the output disabled, followed by interface setup and about sixty seconds of sensor warm-up. "
        "Connector A represents the main checkpoint: health, pending events, and the current state are checked there. "
        "Unhealthy inputs enter the recovery flow. Healthy operation confirms fresh activity, then either runs the deterrent path or checks whether light sleep is allowed. "
        "The interrupt only creates a pending event; it does not directly start the sound."
    )

    # 3 — detection and output state machines.
    slide = prs.slides.add_slide(blank)
    slide_base(slide)
    slide_header(slide, "Detection and Deterrence")
    section_label(slide, 0.72, 1.36, 5.8, "Confirm activity", 18)
    section_label(slide, 6.92, 1.36, 5.6, "Output state", 18)
    segment(slide, (6.65, 1.42), (6.65, 6.85), LIGHT_GRAY, 1.2)

    process(slide, 1.15, 1.86, 4.35, 0.52, "Motion event or 100 ms active check", 15)
    process(slide, 1.15, 2.62, 4.35, 0.58, "Read radar, PIR and a fresh 50 ms audio block", 14)
    decision(slide, 1.9, 3.43, 2.85, 0.98, "Radar AND\nsound?", 13)
    path(slide, [(3.33, 2.38), (3.33, 2.62)])
    path(slide, [(3.33, 3.2), (3.33, 3.43)])

    process(slide, 0.72, 4.66, 2.1, 0.62, "Reset count", 15)
    branch_label(slide, 1.43, 4.3, "NO")
    path(slide, [(1.9, 3.92), (1.77, 3.92), (1.77, 4.66)])
    connector_ref(slide, 1.56, 5.57, "A", "")
    path(slide, [(1.77, 5.28), (1.77, 5.57)], RED, 1.5)
    add_text(slide, 0.72, 6.08, 1.75, 0.24, "Return to monitoring", 10, MID_GRAY, True, PP_ALIGN.CENTER, margin=0)

    process(slide, 3.55, 4.66, 2.3, 0.62, "Increment consecutive count", 14)
    branch_label(slide, 4.36, 4.3, "YES")
    path(slide, [(4.75, 3.92), (4.7, 3.92), (4.7, 4.66)])
    decision(slide, 3.45, 5.42, 2.25, 0.92, "Count = 3?", 12)
    path(slide, [(4.7, 5.28), (4.7, 5.35), (4.575, 5.35), (4.575, 5.42)])
    connector_ref(slide, 3.05, 6.35, "A", "")
    branch_label(slide, 2.55, 5.82, "NO")
    path(slide, [(3.45, 5.88), (3.26, 5.88), (3.26, 6.35)])
    add_text(slide, 0.72, 6.55, 2.2, 0.2, "Next 100 ms check", 10, MID_GRAY, True, PP_ALIGN.CENTER, margin=0)
    connector_ref(slide, 5.93, 5.68, "B", "")
    branch_label(slide, 5.5, 5.48, "YES")
    path(slide, [(5.7, 5.88), (5.93, 5.88)], RED, 1.7)

    connector_ref(slide, 6.98, 1.88, "B", "")
    red_process(slide, 8.55, 1.78, 3.05, 0.68, "Start deterrent burst  ·  maximum 3 s", 14)
    path(slide, [(7.4, 2.09), (8.55, 2.09)], RED, 1.7)
    process(slide, 8.55, 2.72, 3.05, 0.58, "Service events and health", 15)
    path(slide, [(10.08, 2.46), (10.08, 2.72)])
    decision(slide, 7.25, 3.58, 2.0, 0.92, "Fault?", 14)
    decision(slide, 10.25, 3.58, 2.15, 0.92, "Time up?", 12)
    path(slide, [(10.08, 3.3), (10.08, 3.54), (8.25, 3.54), (8.25, 3.58)])
    branch_label(slide, 9.38, 3.58, "NO")
    path(slide, [(9.25, 4.04), (10.25, 4.04)])
    process(slide, 6.92, 4.82, 2.65, 0.66, "Outputs OFF  →  Slide 6", 14, True)
    branch_label(slide, 7.2, 4.42, "YES")
    path(slide, [(8.25, 4.5), (8.25, 4.82)], RED, 1.6)
    red_process(slide, 9.95, 4.82, 2.75, 0.66, "Outputs OFF  ·  15 s cooldown", 14)
    branch_label(slide, 11.62, 4.42, "YES")
    path(slide, [(11.33, 4.5), (11.33, 4.82)], RED, 1.6)
    # Burst not ended loops back to servicing via a clean outer edge.
    branch_label(slide, 12.36, 3.58, "NO")
    path(slide, [(12.4, 4.04), (12.78, 4.04), (12.78, 2.98), (11.6, 2.98)])
    process(slide, 9.95, 5.78, 2.75, 0.62, "Clear count and re-arm", 15)
    path(slide, [(11.33, 5.48), (11.33, 5.78)])
    connector_ref(slide, 11.12, 6.43, "A", "")
    path(slide, [(11.33, 6.4), (11.33, 6.43)], RED, 1.5)
    add_text(slide, 7.0, 6.68, 3.85, 0.2, "Cooldown suppresses another burst.", 10, MID_GRAY, True, PP_ALIGN.CENTER, margin=0)
    notes.append(
        "A candidate requires radar and valid sound together; PIR provides supporting evidence. "
        "The count increments only on consecutive positive checks, and a negative check resets it. "
        "Three positives start a burst limited to three seconds. While it plays, the task continues servicing events and health. "
        "A fault stops the output and enters recovery. A normal end turns the output off, holds a fifteen-second cooldown, clears the count, and returns to monitoring."
    )

    # 4 — interrupt handoff.
    slide = prs.slides.add_slide(blank)
    slide_base(slide)
    slide_header(slide, "Interrupt Handling")
    section_label(slide, 1.0, 1.38, 5.1, "Interrupt service routine (ISR)", 21)
    section_label(slide, 7.65, 1.38, 4.7, "Main firmware task", 21)
    process(slide, 1.0, 2.02, 4.75, 0.72, "Radar / PIR signal changes", 17)
    process(slide, 1.0, 3.12, 4.75, 0.72, "Record the event source", 17)
    red_process(slide, 1.0, 4.22, 4.75, 0.72, "Notify the main task", 17)
    process(slide, 1.0, 5.32, 4.75, 0.72, "Return immediately", 17)
    path(slide, [(3.38, 2.74), (3.38, 3.12)])
    path(slide, [(3.38, 3.84), (3.38, 4.22)])
    path(slide, [(3.38, 4.94), (3.38, 5.32)])

    process(slide, 7.65, 2.02, 4.75, 0.72, "Receive pending event", 17)
    process(slide, 7.65, 3.12, 4.75, 0.72, "Read fresh sensor values", 17)
    process(slide, 7.65, 4.22, 4.75, 0.72, "Apply the current-state rules", 17)
    add_box(slide, 7.65, 5.32, 4.75, 0.72, "Continue through connector A", 17, PINK, RED, TEXT, True)
    path(slide, [(10.03, 2.74), (10.03, 3.12)])
    path(slide, [(10.03, 3.84), (10.03, 4.22)])
    path(slide, [(10.03, 4.94), (10.03, 5.32)])
    # Only one cross-lane handoff arrow.
    path(slide, [(5.75, 4.58), (6.68, 4.58), (6.68, 2.38), (7.65, 2.38)], RED, 1.8)
    add_text(slide, 0.95, 6.42, 11.55, 0.28,
             "ISR rule: capture → notify → return.  No sensor fusion, delays, or playback control inside the ISR.",
             12, MID_GRAY, True, PP_ALIGN.CENTER, margin=0)
    add_text(slide, 1.0, 6.83, 11.45, 0.22,
             "Timing targets:  50 ms audio blocks   ·   100 ms active detection checks   ·   1 s health checks while awake",
             11, RED, True, PP_ALIGN.CENTER, margin=0)
    notes.append(
        "The interrupt service routine performs only three operations: record the event source, notify the main task, and return. "
        "The main task receives the pending event, acquires fresh sensor values, and applies the rules for the current state. "
        "This prevents delays, sound analysis, or playback control from running inside the interrupt handler. "
        "A GPIO wake from light sleep is shown separately on the power-management slide."
    )

    # 5 — power management with a cancellation check before sleep.
    slide = prs.slides.add_slide(blank)
    slide_base(slide)
    slide_header(slide, "Power Management and Wake-up")
    connector_ref(slide, 0.72, 1.82, "A", "")
    add_text(slide, 0.72, 2.27, 1.35, 0.25, "Main checks", 11, MID_GRAY, True, PP_ALIGN.LEFT, margin=0)
    add_text(slide, 2.2, 1.29, 3.3, 0.22, "healthy  ·  idle  ·  no work  ·  cooldown complete", 10, MID_GRAY, True, PP_ALIGN.CENTER, margin=0)
    decision(slide, 2.25, 1.52, 3.15, 1.08, "Sleep\nallowed?", 14)
    path(slide, [(1.14, 2.03), (2.25, 2.03)])
    process(slide, 0.72, 3.16, 2.8, 0.68, "Continue active state  →  A", 14)
    branch_label(slide, 2.02, 2.72, "NO")
    path(slide, [(3.825, 2.6), (3.825, 2.86), (2.12, 2.86), (2.12, 3.16)])

    process(slide, 5.82, 1.67, 2.75, 0.72, "Outputs OFF; finish DFPlayer / UART command", 14)
    branch_label(slide, 5.42, 1.72, "YES")
    path(slide, [(5.4, 2.06), (5.82, 2.06)])
    process(slide, 9.05, 1.67, 3.1, 0.72, "Pause microphone; arm GPIO-level + RTC wake", 14)
    path(slide, [(8.57, 2.06), (9.05, 2.06)])
    decision(slide, 9.3, 2.85, 2.6, 1.02, "Event or input\nactive?", 12)
    path(slide, [(10.6, 2.39), (10.6, 2.85)])

    process(slide, 9.1, 4.34, 3.0, 0.66, "Cancel sleep; resume microphone", 14)
    branch_label(slide, 11.5, 4.0, "YES")
    path(slide, [(11.9, 3.36), (12.42, 3.36), (12.42, 4.67), (12.1, 4.67)])
    process(slide, 9.1, 5.36, 3.0, 0.66, "Read fresh sensors  →  A", 14)
    path(slide, [(10.6, 5.0), (10.6, 5.36)])

    red_process(slide, 5.18, 3.12, 2.7, 0.68, "Enter light sleep", 16)
    branch_label(slide, 8.2, 3.0, "NO")
    path(slide, [(9.3, 3.36), (8.42, 3.36), (8.42, 3.46), (7.88, 3.46)], RED, 1.7)
    process(slide, 4.68, 4.34, 3.7, 0.66, "Motion GPIO level OR RTC timer wakes CPU", 14)
    path(slide, [(6.53, 3.8), (6.53, 4.34)])
    process(slide, 4.68, 5.36, 3.7, 0.66, "Resume microphone; read fresh sensors  →  A", 14)
    path(slide, [(6.53, 5.0), (6.53, 5.36)])

    add_box(slide, 0.72, 6.45, 11.45, 0.48,
            "Radar and PIR remain powered   ·   microphone capture pauses   ·   sound alone cannot wake the ESP32",
            12, PINK, RED, MID_GRAY, True)
    notes.append(
        "Sleep admission requires a healthy system, no pending work, completed burst and cooldown, quiet motion inputs, and the configured idle interval. "
        "The firmware switches outputs off, completes pending audio commands, pauses microphone capture, and arms GPIO-level and RTC wake sources. "
        "It performs a final check: an event or active input cancels sleep. Otherwise, light sleep begins. "
        "Motion or the RTC timer wakes the CPU, after which the microphone resumes and fresh data is acquired before returning to connector A."
    )

    # 6 — recoverable faults and watchdog reset are deliberately separate.
    slide = prs.slides.add_slide(blank)
    slide_base(slide)
    slide_header(slide, "Fault Protection and Recovery")
    section_label(slide, 0.72, 1.38, 7.0, "Faults detected by running firmware", 19)
    process(slide, 0.72, 1.95, 2.25, 0.58, "Low / invalid battery", 14)
    process(slide, 0.72, 2.8, 2.25, 0.58, "Missing / stale sensor data", 14)
    process(slide, 0.72, 3.65, 2.25, 0.58, "Audio output fault", 14)
    red_process(slide, 3.75, 2.55, 2.5, 1.0, "Outputs OFF\nActuation inhibited", 16)
    path(slide, [(2.97, 2.24), (3.35, 2.24), (3.35, 2.88), (3.75, 2.88)], RED, 1.5)
    path(slide, [(2.97, 3.09), (3.75, 3.09)], RED, 1.5)
    path(slide, [(2.97, 3.94), (3.35, 3.94), (3.35, 3.32), (3.75, 3.32)], RED, 1.5)
    decision(slide, 7.0, 2.55, 2.15, 1.0, "Valid?", 13)
    path(slide, [(6.25, 3.05), (7.0, 3.05)])
    process(slide, 6.9, 4.35, 2.35, 0.65, "Periodic recheck", 14)
    branch_label(slide, 8.8, 3.82, "NO")
    path(slide, [(8.08, 3.55), (8.08, 4.35)])
    path(slide, [(9.25, 4.68), (9.62, 4.68), (9.62, 3.05), (9.15, 3.05)])
    process(slide, 9.9, 2.65, 2.55, 0.8, "Cooldown; clear counters; re-arm  →  A", 14, True)
    branch_label(slide, 9.3, 1.82, "YES")
    path(slide, [(8.075, 2.55), (8.075, 2.18), (11.175, 2.18), (11.175, 2.65)], RED, 1.6)
    add_text(slide, 9.76, 3.82, 2.8, 0.95,
             "Battery: above recovery threshold\nSensors: fresh valid frame\nAudio: restart + self-check",
             11, MID_GRAY, False, PP_ALIGN.LEFT, MSO_ANCHOR.TOP, margin=0.02)

    section_label(slide, 0.72, 5.2, 2.3, "Watchdog path", 17)
    process(slide, 2.8, 5.22, 2.25, 0.64, "Main task stalls", 14)
    red_process(slide, 5.55, 5.22, 2.7, 0.64, "Configured watchdog reset", 14)
    process(slide, 8.75, 5.22, 2.65, 0.64, "Power-on / reset  →  Slide 2", 14)
    path(slide, [(5.05, 5.54), (5.55, 5.54)], RED, 1.6)
    path(slide, [(8.25, 5.54), (8.75, 5.54)], RED, 1.6)
    add_text(slide, 1.0, 6.1, 11.25, 0.35,
             "A stalled task cannot execute the software fault path; the configured watchdog restarts the controller.",
             11, MID_GRAY, True, PP_ALIGN.CENTER, margin=0)
    add_box(slide, 0.72, 6.58, 11.45, 0.42,
            "Choose battery limits, idle delay, wake period and acoustic thresholds during hardware calibration.",
            11, PALE_RED, CORAL, MID_GRAY, True)
    notes.append(
        "Fault handling keeps the output off. Low or invalid battery readings, stale sensor data, and audio faults converge on the inhibited state. "
        "The firmware rechecks the relevant recovery condition and stays inhibited until it is valid. Then it completes cooldown, clears counters, re-arms, and returns to connector A. "
        "The watchdog path is separate: if the main task stalls, that task cannot execute the normal software recovery flow, so the configured watchdog resets the controller and returns through power-on."
    )

    for index, slide in enumerate(prs.slides, start=1):
        add_notes(slide, notes[index - 1])

    prs.save(PPTX_PATH)
    return PPTX_PATH


if __name__ == "__main__":
    print(build_deck())
