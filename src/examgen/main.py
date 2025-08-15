import dspy
from . import tools, pdfextract, signatures, pipeline
import os
from dotenv import load_dotenv

SHOW_QUESTIONS = False
LANGUAGE = "English"
QUESTION_TYPES = [
            signatures.QuestionType.MULTIPLE_CHOICE.value,
            signatures.QuestionType.TRUE_FALSE.value,
            signatures.QuestionType.SHORT_ANSWER.value
        ]
NUM_QUESTIONS = 20
OUTPUT_PDF = "pdfs/output.pdf"

# FONTPATH defines a font override if your language is not supported by default fonts
# This will most likely be the case for any non-Ascii contained characters.
# If you do not use any problematic characters, set FONTPATH to an empty string ""
# FONTPATH = ""
FONTPATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

load_dotenv()
LM = dspy.LM(model=os.getenv("LLM") or "", api_base=os.getenv("URL"), api_key=os.getenv("KEY"))
dspy.configure(lm=LM)

def main():
    # Somehow get pdf content here
    pdf_content = pdfextract.FileContent()
    pdf_content.read_file("pdfs/input_4.pdf")
    all_text = pdf_content.get_all_text()

    print(f"Read {len(pdf_content.text_pages)} pages.")

    gen = pipeline.QuestionGenerator()

    result = gen(
        input_text=all_text,
        num_questions=NUM_QUESTIONS,
        language=LANGUAGE,
        question_types=QUESTION_TYPES
    ) # type: ignore

    nq:list[str] = result.new_questions  # type: ignore
    t:str = result.topic # type: ignore
    print(f"Generated {len(nq)} questions for topic {t}")

    if SHOW_QUESTIONS:
        for q in nq:
            print(q, end="\n----\n")

    #save pdf 
    pdfextract.write_pdf(OUTPUT_PDF, nq, t,FONTPATH)
    print(f"Saved output pdf to {OUTPUT_PDF}")