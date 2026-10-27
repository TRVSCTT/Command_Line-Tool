from models import clean_row


test_row = {
    "ID": "TC-02",
    "Company Name": "BrightPath Traders",
    "Registration No.": "RC-771029",
    "Tax ID": "TIN-0044521",
    "Email": "brightpath@@mail",
    "Phone": "+234 802 555\n1122",
    "Country": "Nigeria",
    "Industry": "Retail"
}


result = clean_row(test_row)

print("MODEL RESULT")
print("=" * 40)

print(result)