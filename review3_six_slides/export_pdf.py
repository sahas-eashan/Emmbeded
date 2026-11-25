from pathlib import Path
import win32com.client


ROOT = Path(__file__).resolve().parent
PPTX = ROOT / "Bird_Repellent_Review3_Six_Slides.pptx"
PDF = ROOT / "Bird_Repellent_Review3_Six_Slides.pdf"


def export():
    application = win32com.client.DispatchEx("PowerPoint.Application")
    presentation = None
    try:
        presentation = application.Presentations.Open(str(PPTX.resolve()), WithWindow=False, ReadOnly=False)
        # ppSaveAsOpenXMLPresentation=24; the third argument requests font embedding.
        presentation.SaveAs(str(PPTX.resolve()), 24, True)
        if PDF.exists():
            PDF.unlink()
        presentation.SaveAs(str(PDF.resolve()), 32)
        print(f"slides={presentation.Slides.Count} pdf={PDF}")
    finally:
        if presentation is not None:
            presentation.Close()
        application.Quit()


if __name__ == "__main__":
    export()
