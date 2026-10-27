import pandas as pd

import json

import time

import sys

from models import clean_row, set_model

INPUT_FILE = "data/messy/test_dataset.xlsx"

def main():

    # Check model argument

    if len(sys.argv) != 2:

        print("Usage:")

        print("  python run_claude.py haiku")

        print("  python run_claude.py sonnet")

        print("  python run_claude.py opus")

        return

    model = sys.argv[1].lower()

    if model not in ["haiku", "sonnet", "opus"]:

        print("Invalid model.")

        print("Choose: haiku, sonnet, or opus")

        return

    # Configure selected model

    set_model(model)

    output_file = f"data/cleaned/{model}_cleaned.json"

    df = pd.read_excel(INPUT_FILE)

    # Normalize column names

    df.columns = [

        str(column).replace("\n", " ").strip()

        for column in df.columns

    ]

    results = []

    total_input_tokens = 0

    total_output_tokens = 0

    print(f"Processing {len(df)} rows with Claude {model.upper()}...\n")

    for index, row in df.iterrows():

        row_data = row.to_dict()

        print(f"Processing row {index + 1}/{len(df)}...")

        try:

            result, usage = clean_row(row_data)

            total_input_tokens += usage["input_tokens"]

            total_output_tokens += usage["output_tokens"]

            result["_usage"] = usage

            results.append(result)

        except Exception as e:

            print(f"ERROR on row {index + 1}: {e}")

            results.append({

                "cleaned_row": row_data,

                "issues": [

                    {

                        "field": "SYSTEM",

                        "severity": "error",

                        "message": str(e)

                    }

                ],

                "confidence": 0

            })

        time.sleep(0.5)

    # Save results

    with open(output_file, "w", encoding="utf-8") as file:

        json.dump(

            results,

            file,

            indent=2,

            ensure_ascii=False

        )

    # Pricing

    INPUT_PRICE_PER_MILLION = 1.00

    OUTPUT_PRICE_PER_MILLION = 5.00

    input_cost = (

        total_input_tokens / 1_000_000

    ) * INPUT_PRICE_PER_MILLION

    output_cost = (

        total_output_tokens / 1_000_000

    ) * OUTPUT_PRICE_PER_MILLION

    total_cost = input_cost + output_cost

    cost_per_100 = (total_cost / len(df)) * 100

    print("\nTOKEN USAGE")

    print("=" * 40)

    print(f"Model         : Claude {model.upper()}")

    print(f"Input tokens  : {total_input_tokens}")

    print(f"Output tokens : {total_output_tokens}")

    print(f"Total tokens  : {total_input_tokens + total_output_tokens}")

    print("\nCOST")

    print("=" * 40)

    print(f"Input cost    : ${input_cost:.6f}")

    print(f"Output cost   : ${output_cost:.6f}")

    print(f"Total cost    : ${total_cost:.6f}")

    print(f"Cost per 100 rows : ${cost_per_100:.6f}")

    print("\nClaude processing completed!")

    print(f"Results saved to: {output_file}")

if __name__ == "__main__":

    main()