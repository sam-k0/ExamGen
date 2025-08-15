import dspy
import typing
from . import tools, pdfextract, signatures, pipeline


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

    result = gen(input_text=all_text, num_questions=5, language="Korean") # type: ignore
    nq:list[str] = result.new_questions  # type: ignore

    for q in nq:
        print(q)


