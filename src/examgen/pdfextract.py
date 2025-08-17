import pypdf
from reportlab.platypus import SimpleDocTemplate, Paragraph, ListFlowable, ListItem, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
import os

class FileContent:
    def __init__(self) -> None:
        self.text_pages = []
    
    # Read fpath and write in text_pages
    def read_file(self, fpath = ""):
        for p in pypdf.PdfReader(fpath).pages:
            self.text_pages.append(p.extract_text() or "")

    def get_all_text(self) -> str:
        return "\n".join(self.text_pages)
    


def write_pdf(fpath: str, content: list[str], topic = "", font_path=""):
    doc = SimpleDocTemplate(fpath, pagesize=letter)
    styles = getSampleStyleSheet()
    stylename = "Normal"

    # Use Korean font if specified and available
    if font_path != "" and os.path.exists(font_path):
        stylename = "KoreanNormal"
        pdfmetrics.registerFont(TTFont("NanumGothic", font_path))
        styles.add(ParagraphStyle(
            name="KoreanNormal",
            parent=styles["Normal"],
            fontName="NanumGothic",
            fontSize=12,
            leading=14
        ))
    else:
        print(f"Using fallback font as {font_path} does not exist.")

    story = []
    story.append(Paragraph(topic + f" ({len(content)})", styles[stylename].clone('Title', fontSize=18, leading=22)))
    story.append(Spacer(1, 0.25 * inch))  # space after title

    for item in content:
        # Bullet point for question
        bullet = ListFlowable(
            [ListItem(Paragraph(item, styles[stylename]))], # type: ignore
            bulletType='bullet'
        )
        story.append(bullet)

        # Answer label
        story.append(Paragraph("Answer:", styles[stylename]))
        story.append(Spacer(1, 12))

    doc.build(story)