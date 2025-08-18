import dspy
from . import signatures

class QuestionGenerator(dspy.Module):
    def __init__(self, callbacks=None):
        super().__init__(callbacks)

        self.structure_text = dspy.ChainOfThought(signature=signatures.SplitFileContent)
        self.extract_questions = dspy.ChainOfThought(signature=signatures.PreprocessQuestions)
        self.generate_questions = dspy.ChainOfThought(signature=signatures.GenerateQuestions)
        self.generate_answers = dspy.ChainOfThought(signature=signatures.GenerateAnswers)

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

        # Generate answers for questions
        # output_content:dict[str,str]
        generated_answers = self.generate_answers(
            input_content=generated_questions.output_content, # type: ignore
            input_context=extracted_questions.output_context,  # type: ignore
            input_question_types = question_types, 
            input_prompt= "Read the previously generated questions and generate matching correct answers.\
                            For True / False questions, the generated answer must just be either literally 'True' or 'False'.\
                            For multiple Choice questions, the matching answer must just be the corresponding identifier, for example (A), (B), or (C), ...\
                            For Short Answer questions that allow for free text input, write a concise and short text that answers the questions as short as possible."                        
        )

        return dspy.Prediction(
            new_questions = generated_questions.output_content, # type: ignore
            answers = generated_answers.output_content, #type: ignore
            topic = generated_questions.topic # type: ignore
        )
    


        
