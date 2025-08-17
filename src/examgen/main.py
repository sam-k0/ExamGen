import dspy
from . import tools, pdfextract, signatures, pipeline
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, make_response
import tempfile
import webbrowser
from hashlib import md5

SHOW_QUESTIONS = False
# FONTPATH defines a font override if your language is not supported by default fonts
# This will most likely be the case for any non-Ascii contained characters.
# If you do not use any problematic characters, set FONTPATH to an empty string ""
# FONTPATH = ""
FONTPATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

load_dotenv()
LM = dspy.LM(model=os.getenv("LLM") or "", api_base=os.getenv("URL"), api_key=os.getenv("KEY"))
dspy.configure(lm=LM)

app = Flask(__name__,template_folder="templates")

def process(pdf_file:str, num_q:int, lang:str, types:list):
    pdf_content = pdfextract.FileContent()
    pdf_content.read_file(pdf_file)
    all_text = pdf_content.get_all_text()

    print(f"Read {len(pdf_content.text_pages)} pages.")

    # Generate
    gen = pipeline.QuestionGenerator()
    result = gen(
        input_text=all_text,
        num_questions=num_q,
        language=lang,
        question_types=types
    ) # type: ignore

    nq:list[str] = result.new_questions  # type: ignore
    t:str = result.topic # type: ignore
    print(f"Generated {len(nq)} questions for topic {t}")

    if SHOW_QUESTIONS:
        for q in nq:
            print(q, end="\n-\n")

    #save pdf with hash name
    hash = md5(all_text[:20].encode()).hexdigest()
    out_path = f"pdfs/output_{hash}.pdf"
    if os.path.exists(out_path):
        os.remove(out_path)

    pdfextract.write_pdf(out_path, nq, t,FONTPATH)
    print(f"Saved output pdf to {out_path}")
    return out_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' in request.files:
            pdf_file = request.files['pdf_file']

            with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
                pdf_file.save(tmp)
                tmp_path = tmp.name
            
                # options
                try:
                    num_questions = int(request.form.get('questionsnumber', 5))  # Default to 5 if not provided
                    language_select = request.form.get('langdropdown', 'English')  # Default to English if not provided

                    qtypes = [] # question types
                    if 'multiple_choice' in request.form:
                        qtypes.append(signatures.QuestionType.MULTIPLE_CHOICE.value)
                    if 'true_false' in request.form:
                        qtypes.append(signatures.QuestionType.TRUE_FALSE.value)
                    if 'short_answer' in request.form:
                        qtypes.append(signatures.QuestionType.SHORT_ANSWER.value)

                    if not qtypes:
                        qtypes = [signatures.QuestionType.MULTIPLE_CHOICE.value,
                                  signatures.QuestionType.TRUE_FALSE.value,
                                  signatures.QuestionType.SHORT_ANSWER.value]

                    dlpath = process(pdf_file=tmp_path, num_q=num_questions, lang=language_select, types=qtypes)
                    response = make_response(open(dlpath, 'rb').read())
                    response.headers['Content-Disposition'] = f'attachment; filename={os.path.basename(dlpath)}'

                    return response
                except Exception as e:
                    print(f"Error processing PDF: {e}")
                    return render_template('index.html', error=str(e) + ". Please revise inputs.")

        return render_template('index.html')

    return render_template('index.html')

def main():
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)
    