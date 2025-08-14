import dspy
import typing
from . import tools, pdfextract, signatures, pipeline


k,u = tools.load_secrets()
LM = dspy.LM('ollama_chat/gemma3:4b', api_base=u, api_key=k)
dspy.configure(lm=LM)

def main():
    print("Hello, world!")

