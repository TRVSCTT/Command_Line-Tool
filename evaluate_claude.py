import json

import re

import sys

import pandas as pd

INPUT_FILE = "data/messy/test_dataset.xlsx"

def normalize_value(value):

    """Normalize whitespace and treat em dash as missing."""

    if pd.isna(value):

        return None

    value = str(value).strip()

    if value == "—":

        return None

    value = re.sub(r"\s+", " ", value)

    return value.strip()

def is_valid_email(email):

    """Check basic email format."""

    if not email:

        return False

    return bool(

        re.match(

            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",

            str(email)

        )

    )

def is_valid_phone(phone):

    """Check phone contains only +, digits and spaces."""

    if not phone:

        return False

    return bool(

        re.match(

            r"^\+?[0-9 ]+$",

            str(phone)

        )

    )

def main():

    # ==========================================

    # MODEL ARGUMENT

    # ==========================================

    if len(sys.argv) != 2:

        print("Usage:")

        print("  python evaluate_claude.py haiku")

        print("  python evaluate_claude.py sonnet")

        print("  python evaluate_claude.py opus")

        return

    model = sys.argv[1].lower()

    if model not in ["haiku", "sonnet", "opus"]:

        print("Invalid model.")

        print("Choose: haiku, sonnet, or opus.")

        return

    results_file = (

        f"data/cleaned/{model}_cleaned.json"

    )

    # ==========================================

    # LOAD ORIGINAL DATASET

    # ==========================================

    print(f"Evaluating Claude {model.upper()}...")

    print(f"Results file: {results_file}")

    try:

        original = pd.read_excel(INPUT_FILE)

    except Exception as e:

        print(f"ERROR loading original dataset: {e}")

        return

    # Normalize original column names

    original.columns = [

        str(column).replace("\n", " ").strip()

        for column in original.columns

    ]

    # ==========================================

    # LOAD MODEL RESULTS

    # ==========================================

    try:

        with open(

            results_file,

            "r",

            encoding="utf-8"

        ) as file:

            results = json.load(file)

    except FileNotFoundError:

        print(

            f"\nERROR: {results_file} does not exist."

        )

        print(

            f"Run this first:\n"

            f"  python run_claude.py {model}"

        )

        return

    except json.JSONDecodeError as e:

        print(

            f"\nERROR: Invalid JSON in {results_file}"

        )

        print(e)

        return

    # ==========================================

    # BUILD EXPECTED DUPLICATE REGISTRATIONS

    # ==========================================

    registration_column = "Registration No."

    registrations = (

        original[registration_column]

        .apply(normalize_value)

    )

    duplicate_registrations = set(

        registrations[

            registrations.duplicated(keep=False)

            & registrations.notna()

        ]

    )

    # ==========================================

    # EVALUATION COUNTERS

    # ==========================================

    passed = 0

    total = 0

    email_checks = 0

    phone_checks = 0

    duplicate_checks = 0

    missing_checks = 0

    confidence_checks = 0

    failures = []

    # ==========================================

    # CHECK FUNCTION

    # ==========================================

    def check(condition, message, category):

        nonlocal passed, total

        total += 1

        if condition:

            passed += 1

        else:

            failures.append(

                {

                    "category": category,

                    "message": message

                }

            )

    # ==========================================

    # CHECK EVERY ROW

    # ==========================================

    for index, result in enumerate(results):

        row_number = index + 1# Safety check

        if "cleaned_row" not in result:

            check(

                False,

                f"Row {row_number}: missing cleaned_row",

                "structure"

            )

            continue

        cleaned_row = result["cleaned_row"]

        issues = result.get("issues", [])

        issues_text = json.dumps(

            issues,

            ensure_ascii=False

        ).lower()

        original_row = original.iloc[index]

        # ======================================

        # EMAIL

        # ======================================

        original_email = normalize_value(

            original_row.get("Email")

        )

        cleaned_email = normalize_value(

            cleaned_row.get("Email")

        )

        if original_email is not None:

            email_checks += 1

            # Expected normalized email

            expected_email = original_email.lower()

            check(

                cleaned_email == expected_email,

                (

                    f"Row {row_number}: "

                    f"email normalization incorrect"

                ),

                "email"

            )

            # If original email is invalid,

            # model must flag it.

            if not is_valid_email(original_email):

                email_checks += 1

                email_flagged = (

                    "email" in issues_text

                    and (

                        "invalid" in issues_text

                        or "malformed" in issues_text

                        or "verify" in issues_text

                        or "warning" in issues_text

                    )

                )

                check(

                    email_flagged,

                    (

                        f"Row {row_number}: "

                        f"invalid email was not flagged"

                    ),

                    "email"

                )

        # ======================================

        # PHONE

        # ======================================

        original_phone = normalize_value(

            original_row.get("Phone")

        )

        cleaned_phone = normalize_value(

            cleaned_row.get("Phone")

        )

        if original_phone is not None:

            # Expected phone after whitespace normalization

            expected_phone = re.sub(

                r"\s+",

                " ",

                original_phone

            ).strip()

            phone_checks += 1

            if is_valid_phone(original_phone):

                check(

                    cleaned_phone == expected_phone,

                    (

                        f"Row {row_number}: "

                        f"phone normalization incorrect"

                    ),

                    "phone"

                )

            else:

                phone_flagged = (

                    "phone" in issues_text

                    and (

                        "invalid" in issues_text

                        or "verify" in issues_text

                        or "warning" in issues_text

                        or "suspicious" in issues_text

                    )

                )

                check(

                    phone_flagged,

                    (

                        f"Row {row_number}: "

                        f"invalid phone was not flagged"

                    ),

                    "phone"

                )

        # ======================================

        # MISSING VALUES

        # ======================================

        for column in original.columns:

            original_value = normalize_value(

                original_row.get(column)

            )

            cleaned_value = normalize_value(

                cleaned_row.get(column)

            )

            if original_value is None:

                missing_checks += 1

                check(

                    cleaned_value is None,

                    (

                        f"Row {row_number}: "f"missing value in '{column}' "

                        f"was not preserved as missing"

                    ),

                    "missing"

                )

        # ======================================

        # DUPLICATE REGISTRATION

        # ======================================

        registration = normalize_value(

            original_row.get(registration_column)

        )

        if registration is not None:

            expected_duplicate = (

                registration in duplicate_registrations

            )

            model_duplicate = (

                bool(result.get("duplicate_registration"))

                or "duplicate" in issues_text

            )

            duplicate_checks += 1

            check(

                model_duplicate == expected_duplicate,

                (

                    f"Row {row_number}: "

                    f"duplicate registration flag incorrect "

                    f"(expected={expected_duplicate}, "

                    f"got={model_duplicate})"

                ),

                "duplicate"

            )

        # ======================================

        # CONFIDENCE

        # ======================================

        confidence = result.get("confidence")

        confidence_checks += 1

        check(

            isinstance(confidence, (int, float))

            and 0 <= confidence <= 1,

            (

                f"Row {row_number}: "

                f"invalid confidence value"

            ),

            "confidence"

        )

    # ==========================================

    # FINAL ACCURACY

    # ==========================================

    accuracy = (

        passed / total

        if total > 0

        else 0

    )

    # ==========================================

    # RESULTS

    # ==========================================

    print("\n")

    print("=" * 55)

    print(f"CLAUDE {model.upper()} FINAL EVALUATION")

    print("=" * 55)

    print(f"Checks passed : {passed}")

    print(f"Total checks  : {total}")

    print(f"Accuracy      : {accuracy:.2%}")

    print("\nCHECK BREAKDOWN")

    print("-" * 55)

    print(f"Email checks       : {email_checks}")

    print(f"Phone checks       : {phone_checks}")

    print(f"Duplicate checks   : {duplicate_checks}")

    print(f"Missing-value checks: {missing_checks}")

    print(f"Confidence checks  : {confidence_checks}")

    # ==========================================

    # FAILURES

    # ==========================================

    if failures:

        print("\nFAILURES")

        print("-" * 55)

        for failure in failures:

            print(

                f"[{failure['category'].upper()}] "

                f"{failure['message']}"

            )

    else:

        print("\nNo failed checks.")

    print("=" * 55)

if __name__ == "__main__":

    main()