# Spreadsheet Cleaner
A command-line tool for cleaning and validating spreadsheet data with Python and Claude models. It processes an Excel dataset and compares Claude Haiku, Sonnet, and Opus for measured accuracy and cost.

## Features

- Normalize whitespace and line breaks
- Normalize email addresses to lowercase and flag malformed emails
- Normalize phone-number spacing and flag suspicious values
- Detect duplicate registration numbers
- Preserve missing or uncertain values rather than inventing data
- Produce cleaned results and confidence scores
- Track model token usage, estimated API cost, and evaluation accuracy

## Project Structure

spreadsheet-cleaner/ 
├── data/ 
│ ├── messy/test_dataset.xlsx 
│ └── cleaned/ 
├── tests/ground_truth.json 
├── main.py 
├── cleaner.py 
├── evaluator.py 
├── models.py 
├── run_claude.py 
├── evaluate_claude.py 
├── cost.py 
├──requirements.txt 
├──.env  
├──.gitignore 
└── README.md

## Setup

Requirements: Python and an Anthropic API key for Claude-based processing.
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt

Create a `.env` file in the project root:

ANTHROPIC_API_KEY=your_api_key_here

Keep the real API key private. Never commit a file to GitHub.

Run the Deterministic Cleaner

python main.py

Place the input workbook atst copy it:
1. Create a file cal The default output isour PDF to a proper GitHub README.md.

Run the Claude Benchmark

python run_claude.py haiku
python run_claude.py sonnet
python run_claude.py opus

python evaluate_claude.py haiku
python evaluate_claude.py sonnet
python evaluate_claude.py opus

Run commands from the project root and ensure the input workbook and expected result files exist.

Benchmark Results

Measured on the project dataset using 112 evaluation checks per model. Costs are estimates based on the pricing assumptions used by the project scripts.

Model          Checks   Accuracy   Input   Output     Total        Total Cost      Cost/100 Rows
Claude Haiku   77/112   68.75%     6,707   3,703     10,410         $0.025222        $0.126110
Claude Sonnet  53/112   47.32%     6,707   3,595     10,302         $0.024682        $0.123410
Claude Opus    53/112   47.32%     6,707   3,575     10,282         $0.024582        $0.122910

Recommendation

Claude Haiku is recommended based on this benchmark. It achieved 68.75% accuracy, 21.43 percentage points higher than Sonnet and Opus. Its measured cost per 100 rows was slightly higher: $0.126110, compared with $0.123410 for Sonnet and $0.122910 for Opus.

Sonnet and Opus each passed 53 of 112 checks. This is the measured result for this dataset and evaluation procedure; it does not necessarily mean their outputs were identical. Results may differ with other datasets, prompts, evaluation rules, or model pricing.



Limitations

- Accuracy reflects this dataset and these evaluation checks, not universal model performance
- Ambiguous values should be flagged for human review rather than guessed
- API costs change with pricing, prompt size, output size, and usage. Check current Anthropic pricing before budgeting.


