import dspy
import typing
from . import tools, pdfextract, signatures, pipeline

SHOW_QUESTIONS = False
LANGUAGE = "Korean"
QUESTION_TYPES = [
            signatures.QuestionType.MULTIPLE_CHOICE.value,
            signatures.QuestionType.TRUE_FALSE.value,
            signatures.QuestionType.SHORT_ANSWER.value
        ]
NUM_QUESTIONS = 20
OUTPUT_PDF = "pdfs/output.pdf"

k,u = tools.load_secrets()
LM = dspy.LM('ollama_chat/gemma3:27b', api_base=u, api_key=k)
dspy.configure(lm=LM)

def main():
    # Somehow get pdf content here
    pdf_content = pdfextract.FileContent()
    pdf_content.read_file("pdfs/test.pdf")
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
    print(f"Generated {len(nq)} questions.")

    if SHOW_QUESTIONS:
        for q in nq:
            print(q, end="\n----\n")

    #save pdf
    pdfextract.write_pdf(OUTPUT_PDF, nq)
    print(f"Saved output pdf to {OUTPUT_PDF}")