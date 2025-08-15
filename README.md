# ExamGen

Generates exam questions from provided PDF documents containing notes, summaries, and other educational materials.

## Settings
- SHOW_QUESTIONS: If set to `True`, the generated questions will be printed to the console.
- LANGUAGE: The language in which the questions should be generated (e.g., "English", "Korean").
- QUESTION_TYPES: Types of questions to generate (e.g., "multiple choice", "short answer").
- NUM_QUESTIONS: The number of questions to generate.
- OUTPUT_PDF: The file path where the generated PDF will be saved.

## Setup

Provide `baseurl.txt` and `key.txt` files in the root directory.

## Dependencies
- "dspy (>=3.0.1,<4.0.0)",
- "pypdf (>=6.0.0,<7.0.0)",
- "reportlab (>=4.4.3,<5.0.0)"