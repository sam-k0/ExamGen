import dspy
from dspy.clients import openai
from . import tools, pdfextract, signatures, pipeline
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, make_response
from hashlib import md5
import time
import requests
import logging


logging.getLogger("dspy").setLevel(logging.DEBUG)

DOCKERIZED = os.getenv("DOCKERIZED", "false") == "true"
# FONTPATH defines a font override if your language is not supported by default fonts
# This will most likely be the case for any non-Ascii contained characters.
# If you do not use any problematic characters, set FONTPATH to an empty string ""
# FONTPATH = ""
FONTPATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf" if not DOCKERIZED else "/usr/share/fonts/noto/NotoSansCJK-Regular.ttc"

PDF_MAX_AGE_DAYS = 7


load_dotenv()

MODEL = os.getenv("LLM", "ollama_chat/gemma3:27b")
URL = os.getenv("URL")
KEY = os.getenv("KEY")
MAXTOKENS = int(os.getenv("MAXTOKENS", "5000"))
LM = dspy.LM(model=MODEL, api_base=URL, api_key=KEY, max_tokens=MAXTOKENS)

print("Using", MODEL, "at", URL, "key length:", len(KEY) if KEY else "*ignored*")
print(dspy.__version__)

dspy.configure(lm=LM)

app = Flask(__name__,template_folder="templates")

def cleanup_old_pdfs(max_age_days=PDF_MAX_AGE_DAYS):
    """Delete PDFs older than max_age_days from the pdfs directory."""
    pdfs_dir = "pdfs"
    if not os.path.exists(pdfs_dir):
        return
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    
    for filename in os.listdir(pdfs_dir):
        # dont delete gitkeep files
        if filename.startswith(".gitkeep"):
            continue

        filepath = os.path.join(pdfs_dir, filename)
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                    print(f"Deleted old PDF: {filepath}")
                except Exception as e:
                    print(f"Error deleting {filepath}: {e}")

def pdf_exists(pdf_file:str):
    """Check if a PDF file exists in the pdfs directory."""
    return os.path.exists(os.path.join("pdfs", pdf_file)) 

@app.before_request
def cleanup_on_startup():
    cleanup_old_pdfs()

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

    # nq: New Questions
    # qa: Question answers
    # t: Topic
    nq:list[str] = result.new_questions  # type: ignore
    qa:dict[str,str] = result.answers # type: ignore
    t:str = result.topic # type: ignore
    ctx:str = result.context #type: ignore


    for k,v in qa.items():
        print(f"Question: {k}")
        print(f"Answer: {v}")

    print(f"Generated {len(nq)} questions for topic {t}")
    return nq,qa,t, ctx
    
def make_pdf(qa:dict[str,str], all_text:str, t:str):
    #save pdf with hash name
    hash = md5(all_text[:20].encode()).hexdigest()
    out_path = f"pdfs/output_{hash}.pdf"
    if os.path.exists(out_path):
        os.remove(out_path)

    pdfextract.write_pdf_with_answers(out_path, qa, t,FONTPATH)
    print(f"Saved output pdf to {out_path}")
    return out_path

# build html quiz from dict of questions and answers
def build_html_quiz(qa:dict[str, str]):
    template = """
<p id="question" name="question"><b>{questionstr}</b></p>
<label for="sanswer{questionid}">Your answer:</label>
<input type="text" id="sanswer{questionid}" name="sanswer{questionid}" required>
<input type="hidden" id="canswer{questionid}" name="canswer{questionid}" value="{answer}">
<input type="hidden" id="question{questionid}" name="question{questionid}" value="{questionstr}">
<br><br>
"""

    output_html:str = ""
    c:int = 0
    for question, correct_answer in qa.items():
        c += 1
        output_html += template.format(questionid = c, questionstr = question, answer=correct_answer)
    return output_html

# build html results from dict of graded questions and answers, student answers, and truths
def build_html_results(graded:dict[str, tuple[bool, str]], student_answers:list[str],truths:list[str]):
    template="""
<p id="question" name="question"><b>{questionstr}</b></p>
<label for="sanswer{questionid}">Your answer:</label>
<input type="text" id="sanswer{questionid}" name="sanswer{questionid}" value="{studentanswer}" disabled>
<p id="correctanswer" name="correctanswer" style="color: {color};">Correct answer was: {correctanswer}</p>
<p id="reasoning" name="reasoning">Reason: {reasoning}</p>
<br><br>
"""
    output_html = ""
    c = 0
    correct = 0
    for question, eval in graded.items():
        is_correct:bool = eval[0]
        reasoning:str = eval[1]
        sanswer:str = student_answers[c]
        canswer:str = truths[c]
        # format
        output_html += template.format(
            questionid = c,
            questionstr = question,
            studentanswer = sanswer,
            correctanswer = canswer,
            reasoning = reasoning,
            color = "green" if is_correct else "red"
        )
        correct += int(is_correct)
        c+=1
    return output_html, correct, len(truths)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('menu') == "index":
            if 'pdf_file' in request.files:
                pdf_file = request.files['pdf_file']
                # Save uploaded file to pdfs directory
                os.makedirs('pdfs', exist_ok=True)
                upload_filename = f"upload_{int(time.time())}_{md5(pdf_file.filename.encode()).hexdigest()}.pdf"
                upload_path = os.path.join('pdfs', upload_filename)

                if os.path.exists(upload_path):
                    os.remove(upload_path)

                pdf_file.save(upload_path)
                print(f"Uploaded PDF saved to: {upload_path}")
                
                # options
                try:
                    num_questions = int(request.form.get('questionsnumber', 5))  # Default to 5 if not provided
                    num_questions = 1 if num_questions < 1 else num_questions # make sure its above 0

                    language_select = request.form.get('langdropdown', 'English')  # Default to English if not provided
                    selected_options = request.form.getlist("options")  # list of checked values

                    print(selected_options)

                    qtypes = [] # question types
                    if 'qmulti' in selected_options:
                        qtypes.append(signatures.QuestionType.MULTIPLE_CHOICE.value)
                    if 'qbool' in selected_options:
                        qtypes.append(signatures.QuestionType.TRUE_FALSE.value)
                    if 'qwrite' in selected_options:
                        qtypes.append(signatures.QuestionType.SHORT_ANSWER.value)

                    print(qtypes)

                    if not qtypes:
                        qtypes = [signatures.QuestionType.MULTIPLE_CHOICE.value,
                                signatures.QuestionType.TRUE_FALSE.value,
                                signatures.QuestionType.SHORT_ANSWER.value]

                    nq,qa,t,ctx = process(pdf_file=upload_path, num_q=num_questions, lang=language_select, types=qtypes)

                    print(ctx)
                    # nq - new questions
                    # qa - question / correct answer
                    # t - topic
                    # ctx - context
                    response = None
                    if 'outputtype' not in selected_options: # pdf output
                        dlpath = make_pdf(qa, all_text="".join(nq), t=t) # build pdf here
                        response = make_response(open(dlpath, 'rb').read())
                        response.headers['Content-Disposition'] = f'attachment; filename={os.path.basename(dlpath)}'
                    else: # assemble quiz
                        html_content = build_html_quiz(qa)
                        response = render_template(
                            'quiz.html',
                            content=html_content,
                            topic=t,
                            num_questions=len(nq),
                            context=ctx)
                    return response
                
                except Exception as e:
                    print(f"Error processing PDF: {e}")
                    return render_template('index.html', error=str(e) + ". Please revise inputs.")

            return render_template('index.html')
        elif request.form.get('menu') == "quiz":
            # get num of questions
            num_questions = int(request.form.get("num_questions",1)) #type:ignore
            context = request.form.get("context","")
            
            questions = []
            studentanswers=[]
            groundtruths=[]

            for i in range(1, num_questions + 1): # build lists
                questions.append(request.form.get(f"question{i}"))
                studentanswers.append(request.form.get(f"sanswer{i}"))
                groundtruths.append(request.form.get(f"canswer{i}"))

            
            grading = pipeline.GradeAnswers()
            results = grading(
                input_questions=questions,
                input_truths=groundtruths,
                input_student_answers=studentanswers,
                input_context=context
            )

            # return template with grades
            graded:dict[str, tuple[bool, str]] = results.graded_results #type:ignore
            print("#"*10)
            print(graded)

            # Visualize results
            # results.html has args:
            # correct,num_questions,content
            htmlstr, correct, total = build_html_results(graded, studentanswers, groundtruths)
            return render_template('results.html',content=htmlstr,correct=correct,num_questions=total)

    return render_template('index.html')

def main():
    app.run(debug=True, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()