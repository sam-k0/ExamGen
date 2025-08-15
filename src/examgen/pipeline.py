import dspy
import typing
from . import signatures

class QuestionGenerator(dspy.Module):

    def __init__(self, callbacks=None):
        super().__init__(callbacks)

        self.structure_text = dspy.ChainOfThought(signature=signatures.SplitFileContent)
        self.extract_questions = dspy.ChainOfThought(signature=signatures.PreprocessQuestions)
        self.generate_questions = dspy.ChainOfThought(signature=signatures.GenerateQuestions)

    def forward(self, input_text:str, num_questions:int, language="English", question_types:list[str] = []):
        """process all given notes"""

        #Structure text and preprocess cause it could be nasty from OCR or pdf notes
        structured_text = self.structure_text(
            input_content=input_text
            )
        
        # Extract questions and split into rows
        # output_context:str -> Any domain related context
        # output_content:list[str] -> previous questions
        extracted_questions = self.extract_questions(
            input_prompt = "Examine input_context and provide output_context and output_content.",
            input_context = structured_text.output_content # type: ignore
        )

        # Generate new questions
        # output_content:list[str]
        generated_questions = self.generate_questions(
            input_content=extracted_questions.output_content,  # type: ignore
            input_context=extracted_questions.output_context,  # type: ignore
            num_questions=num_questions,
            language=language,
            question_types=question_types,
            input_prompt = "Examine given input_context and input_content to generate new possible questions to study."
        )

        return dspy.Prediction(
            new_questions = generated_questions.output_content # type: ignore
        )
    


        
