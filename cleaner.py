import pandas as pd
import re

def clean_value(value):
    """Clean basic formatting problems"""

    if pd.isna(value):
        return None

    value=str(value).strip()

    #Treat em dash as missing
    if value == "-":
        return None

    #Replace line breaks with spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip()

def clean_email(email):
    """Validate and normalize an email address."""

    if email is None:
        return None , False

    email = email.lower().strip()

    #Basic email validation 
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(pattern , email):
        return email , False


    return email , True


def clean_phone(phone):
    """Normalize phone formatting"""

    if phone is None:
        return None , False

    phone = re.sub(r"\s+", " ", str(phone).strip())

    #check that the phone contains only digits, spaces and +
     
    if not re.match(r"^\+?[0-9 ]+$", phone):
        return phone, False

    return phone, True

def clean_dataset(input_file , output_file):
    df = pd.read_excel(input_file)

    #Clean every cell
    for column in df.columns:
        df[column] = df[column].apply(clean_value)

    #Clean emails
    if "Email" in df.columns:
        results = df["Email"].apply(clean_email)
        df["Email"] = results.apply(lambda x: x[0])
        df["Email Valid"] = results.apply(lambda x: x[1])


    #Clean phones
    if "Phone" in df.columns:
        results= df["Phone"].apply(clean_phone)
        df["Phone"] = results.apply(lambda x: x[0])
        df["Phone Valid"] = results.apply(lambda x: x[1])


    #Detect duplicate registration numbers
    if "Registration No." in df.columns:
        df["Duplicate Registration"] = (
            df["Duplicate Registration No."]
            .duplicated(keep=False)
            &df["Registration No."].notna()
        )
    else:
        df["Duplicate Registration"]= False
    # Calculate a basic confidence score
    df["Confidence"] = 1.0

    if "Email Valid" in df.columns:
        df.loc[df["Email Valid"] == False, "Confidence"] -= 0.25

    if "Phone Valid" in df.columns:
        df.loc[df["Phone Valid"] == False, "Confidence"] -= 0.25

    if "Duplicate Registration" in df.columns:
        df.loc[
            df["Duplicate Registration"] == True,
            "Confidence"
        ] -= 0.15

    # Keep confidence between 0 and 1
    df["Confidence"] = df["Confidence"].clip(0, 1)

    #Save Result
    df.to_excel(output_file , index=False)

    return df