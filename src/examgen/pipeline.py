import dspy
import typing
from . import signatures

class QuestionGenerator(dspy.Module):

    def __init__(self, callbacks=None):
        super().__init__(callbacks)

        self.structure_text = dspy.ChainOfThought(signature=signatures.SplitFileContent)