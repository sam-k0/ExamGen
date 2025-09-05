import dspy
from enum import Enum

class QuestionType(Enum):
    MULTIPLE_CHOICE = "Multiple Choice"
    TRUE_FALSE = "True/False"
    SHORT_ANSWER = "Short Answer"


# Receives a string of read questions and structures them into a list of text rows
class SplitFileContent(dspy.Signature):
    input_content:str = dspy.InputField(
        desc="Unordered input text that was extracted from a student's pdf file.\
              May contain information like notes, previous exam questions or other.\
              Text may be missing some characters or words due to OCR being used.")

    output_content:str = dspy.OutputField(
        desc="Fixed and preprocessed information and notes, with missing characters filled in to fit the overall context."
        )

# Preprocesses Text and splits into rows
class PreprocessQuestions(dspy.Signature):
    input_prompt:str = dspy.InputField(
        desc="General prompt for this task. May contain more specialised information to pay attention to."
        )
    input_context:str = dspy.InputField(
        desc="Domain-related information, contains student's notes, previous exam questions, slides and other information."
        )
    
    output_context:str = dspy.OutputField(
        desc="All domain-related relevant context, structured, and preprocessed to be used to provide context to generate new possible exam questions."
        )
    output_content:list[str] = dspy.OutputField(
        desc="A list of previous exam or training questions foudn in the input context, to be used as a style hint for how possible new questions may be formulated."
        )

# Generates new questions based on input questions
class GenerateQuestions(dspy.Signature):
    input_content:list[str] = dspy.InputField(
        desc="Prior exam questions found in notes, giving guidance on how to formulate new questions."
        )
    input_context:str = dspy.InputField(
        desc="All relevant domain-related context found in student's notes. New questions can incorporate or ask any of this given context."
        )

    input_prompt:str = dspy.InputField(
        desc="General prompt for this task. May contain more specialised info to pay attention to."
        )
    
    num_questions:int = dspy.InputField(
        desc="Number of new questions to generate. Follow this precisely."
        )
    
    language:str = dspy.InputField(
        desc="Language to use for generated questions. \
            Please only stick to that language, exceptions can be specific keywords. \
            If for example the language is Korean, only use hangeul characters and no latin characters."
        )
    
    question_types:list[str] = dspy.InputField(
        desc="List of question types to generate. Guidelines are:\
            - Multiple Choice: A question with several answer options, only one of which is correct. You MUST provide the answer options in your generated response.\
            - True/False: A statement that the student must identify as true or false.\
            - Short Answer: A question that requires a brief, written response.\
                If all three types are selected, you MUST provide questions for each type."
        )

    output_content:list[str] = dspy.OutputField(
        desc="Newly generated possible exam questions."
        )
    
    
    topic:str= dspy.OutputField(
        desc="Short Title for the generated set of questions."
    )


class GenerateAnswers(dspy.Signature): 
    input_content:list[str] = dspy.InputField(
        desc="Previously generated questions about the given context."
    )

    input_context:str = dspy.InputField(
        desc = "All relevant domain-related context found in student's notes.\
            Use this information to generate correct answers for the given questions."
    )

    input_question_types:list[str] = dspy.InputField(
        desc="List of question types. The given input questions and this question_types list are in correct order, so you can match them directly."
        )

    input_prompt:str=dspy.InputField(
        desc="Generic prompt for your current task. Please follow given instructions closely."
    )

    output_content:dict[str, str] = dspy.OutputField(
        desc= "Dictionary of [Question,Answer] key-value pairs.\
            The key must be the generated question, while the value should be the fitting answer for that question."
    )

class BatchGradeAnswers(dspy.Signature):
    input_content:dict[str,tuple[str,str]] = dspy.InputField(
        desc="Dictionary of [Question,[generatedAnswer, StudentAnswer]] key-value pairs.\
            The key is the question, while the value is the student's given answer."
    )
    input_context:str = dspy.InputField(
        desc="All relevant domain-related context found in student's notes.\
            Use this information to generate correct answers for the given questions."
    )
    input_prompt:str = dspy.InputField(
        desc="Generic prompt for your current task. Please follow given instructions closely."
    )
    output_content:dict[str, tuple[bool, str]] = dspy.OutputField(
        desc="Dictionary of [Question,IsCorrect] key-value pairs.\
            The key is the question, while the value is a tuple of bool for correct or incorrect, and str is the reasoning why it was graded that way."
    )
