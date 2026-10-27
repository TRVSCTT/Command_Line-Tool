import pandas as pd
import re
INPUT_FILE = "data/messy/test_dataset.xlsx" 
OUTPUT_FILE = "data/cleaned/cleaned_dataset.xlsx"



def normalize_text(value): 
    """Expected normalization for ordinary text fields."""
    if pd.isna(value):
      return None

    value = str(value).strip()

    if value == "—":
       return None

    return re.sub(r"\s+", " ", value).strip()


def expected_email(value): 
    """Return expected normalized email and validity."""
    value = normalize_text(value)

    if value is None:
      return None, False

    value = value.lower()

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return value, bool(re.match(pattern, value))

def expected_phone(value): 
    """Return expected normalized phone and validity."""
    value = normalize_text(value)

    if value is None:
       return None, False

    valid = bool(re.match(r"^\+?[0-9 ]+$", value))

    return value, valid

def evaluate():
    original = pd.read_excel(INPUT_FILE)
    cleaned = pd.read_excel(OUTPUT_FILE)

    total_checks = 0
    passed_checks = 0

    # ------------------------------------------------
    # 1. Check that the number of rows is unchanged
    # ------------------------------------------------

    total_checks += 1

    if len(original) == len(cleaned):
      passed_checks += 1

    # ------------------------------------------------
    # 2. Check email cleaning
    # ------------------------------------------------

    for index, original_email in enumerate(original["Email"]):

       expected_value, expected_valid = expected_email(original_email)

       actual_value = cleaned.loc[index, "Email"]
       actual_valid = cleaned.loc[index, "Email Valid"]

       total_checks += 2

       if pd.isna(expected_value):
        value_correct = pd.isna(actual_value)
       else:
        value_correct = str(actual_value) == expected_value

       if value_correct:
        passed_checks += 1

       if bool(actual_valid) == expected_valid:
        passed_checks += 1

    # ------------------------------------------------
    # 3. Check phone cleaning
    # ------------------------------------------------

    for index, original_phone in enumerate(original["Phone"]):

      expected_value, expected_valid = expected_phone(original_phone)

      actual_value = cleaned.loc[index, "Phone"]
      actual_valid = cleaned.loc[index, "Phone Valid"]

      total_checks += 2

      if pd.isna(expected_value):
        value_correct = pd.isna(actual_value)
      else:
        value_correct = str(actual_value) == expected_value

      if value_correct:
        passed_checks += 1

      if bool(actual_valid) == expected_valid:
        passed_checks += 1

    # ------------------------------------------------
    # 4. Check duplicate registrations
    # ------------------------------------------------

    registrations = original["Registration\nNo."]

    expected_duplicates = (
       registrations
       .replace("—", pd.NA)
       .duplicated(keep=False)
    )

    for index, expected_duplicate in enumerate(expected_duplicates):

      actual_duplicate = cleaned.loc[
        index,
        "Duplicate Registration"
      ]

      total_checks += 1

      if bool(actual_duplicate) == bool(expected_duplicate):
        passed_checks += 1

    # ------------------------------------------------
    # 5. Check confidence
    # ------------------------------------------------

    for value in cleaned["Confidence"]:

       total_checks += 1

       if 0 <= float(value) <= 1:
        passed_checks += 1

    # ------------------------------------------------
    # Final score
    # ------------------------------------------------

    accuracy = passed_checks / total_checks

    print("=" * 45)
    print("SPREADSHEET CLEANER EVALUATION")
    print("=" * 45)

    print(f"Checks passed : {passed_checks}")
    print(f"Total checks  : {total_checks}")
    print(f"Accuracy      : {accuracy:.2%}")

    print("=" * 45)
if __name__ == "__main__": 
  evaluate()