# ExamGen

Generates exam questions from provided PDF documents containing notes, summaries, and other educational materials.

## Settings
- SHOW_QUESTIONS: If set to `True`, the generated questions will be printed to the console.
- LANGUAGE: The language in which the questions should be generated (e.g., "English", "Korean").
- QUESTION_TYPES: Types of questions to generate (e.g., "multiple choice", "short answer").
- NUM_QUESTIONS: The number of questions to generate.
- OUTPUT_PDF: The file path where the generated PDF will be saved.
- FONTPATH: (optional) Override font for special characters. Leave to `""` if not needed.

## Setup

Provide a `.env` file in the root directory with the following variables:
```
URL=https://subdomain.domain.whatever
KEY=apikey
LLM=ollama_chat/yourmodel:8b
```
If you do not use a hosted model, refer to [this guide](https://dspy.ai/).

This uses Poetry. 

1. Install dependencies: `poetry install`
2. Run module: `poetry run examgen`

## Dependencies
- "dspy (>=3.0.1,<4.0.0)",
- "pypdf (>=6.0.0,<7.0.0)",
- "reportlab (>=4.4.3,<5.0.0)",
- "python-dotenv (>=1.1.1,<2.0.0)",
- "crossfiledialog (>=1.0.0,<2.0.0)"

On Linux, you may be missing fonts depending on your language.
For Korean, that is `fonts-nanum`. (`sudo apt install fonts-nanum`)