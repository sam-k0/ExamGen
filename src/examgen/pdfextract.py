import pypdf
from reportlab.platypus import SimpleDocTemplate, Paragraph, ListFlowable, ListItem, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

class FileContent:
    def __init__(self) -> None:
        self.text_pages = []
    
    # Read fpath and write in text_pages
    def read_file(self, fpath = ""):
        for p in pypdf.PdfReader(fpath).pages:
            self.text_pages.append(p.extract_text() or "")

    def get_all_text(self) -> str:
        return "\n".join(self.text_pages)
    


def write_pdf(fpath: str, content: list[str], topic = ""):
    doc = SimpleDocTemplate(fpath, pagesize=letter)
    
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    pdfmetrics.registerFont(TTFont("NanumGothic", font_path))
    

    doc = SimpleDocTemplate(fpath, pagesize=letter)

    # Create a style that uses our Korean-capable font
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="KoreanNormal",
        parent=styles["Normal"],
        fontName="NanumGothic",
        fontSize=12,
        leading=14
    ))

    story = []
    story.append(Paragraph(topic, styles["KoreanNormal"].clone('Title', fontSize=18, leading=22)))
    story.append(Spacer(1, 0.25 * inch))  # space after title

    for item in content:
        # Bullet point for question
        bullet = ListFlowable(
            [ListItem(Paragraph(item, styles["KoreanNormal"]))], # type: ignore
            bulletType='bullet'
        )
        story.append(bullet)

        # Answer label
        story.append(Paragraph("Answer:", styles["KoreanNormal"]))
        story.append(Spacer(1, 12))

    doc.build(story)