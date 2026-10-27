import os 
from dotenv import load_dotenv
import json 
from anthropic import Anthropic

load_dotenv()

MODEL_NAMES = {

    "haiku": "claude-haiku-4-5",

    "sonnet": "claude-sonnet-4-5",

    "opus": "claude-opus-4-5"

}

MODEL_NAME = MODEL_NAMES["sonnet"]

client = Anthropic(api_key= os.getenv("ANTHROPIC_API_KEY"))


def set_model(model):

    global MODEL_NAME

    if model not in MODEL_NAMES:

        raise ValueError(

            "Model must be haiku, sonnet, or opus"

        )

    MODEL_NAME = MODEL_NAMES[model]
SYSTEM_PROMPT = """ 
You are a spreadsheet data-cleaning assistant.
Your job is to inspect one spreadsheet record and identify formatting problems, invalid values, and missing values.
Rules:
Do not invent information.
Remove unnecessary whitespace and line breaks.
Normalize email addresses to lowercase.
Mark malformed emails as invalid.
Normalize phone formatting without inventing digits.
Mark suspicious or invalid values for review.
Preserve uncertain original values.
Return ONLY valid JSON. """


def clean_row(row):
    prompt = f"""
Clean and validate this spreadsheet row.

Input row: {
    json.dumps(row, ensure_ascii=False, default=str)}

Return JSON using exactly this structure:

{{ 
    "cleaned_row": {{ 
        "ID": "...", 
        "Company Name": "...", 
        "Registration No.": "...", 
        "Tax ID": "...", 
        "Email": "...", 
        "Phone": "...", 
        "Country": "...", 
        "Industry": "..." 
    }},
    "issues": [], 
    "confidence": 0.0 }}

The confidence must be a number between 0 and 1.
Do not invent missing information. """
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
           {"role": "user", "content": prompt}
       ]
    )

    text = response.content[0].text.strip()
    if text.startswith("```"): 
        text = text.split("\n", 1)[1] 
        text = text.rsplit("```", 1)[0].strip()

    result = json.loads(text)


    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }
    return result, usage