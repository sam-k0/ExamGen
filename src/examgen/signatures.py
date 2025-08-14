import dspy
import typing
import json

# Receives a string of read questions and structures them into a list of questions
class SplitFileContent(dspy.Signature):
    input_content:str = dspy.InputField(desc="Read file text")
    output_content:list[str] = dspy.OutputField(desc="structured output")
