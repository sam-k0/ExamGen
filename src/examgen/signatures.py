import dspy
import typing
import json
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
        desc="Number of new questions to generate."
        )
    
    language:str = dspy.InputField(
        desc="Language to use for generated questions."
        )
    
    question_types:list[str] = dspy.InputField(
        desc="List of question types to generate. Guidelines are:\
            - Multiple Choice: A question with several answer options, only one of which is correct.\
            - True/False: A statement that the student must identify as true or false.\
            - Short Answer: A question that requires a brief, written response."
        )

    output_content:list[str] = dspy.OutputField(
        desc="Newly generated possible exam questions."
        )


