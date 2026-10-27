from cleaner import clean_dataset

input_file = "data/messy/test_dataset.xlsx"
output_file = "data/cleaned/cleaned_dataset.xlsx"


df = clean_dataset(input_file , output_file)

print("Cleaning completed")
print(f"Rows processed: {len(df)}")
print(f"Output saved to: {output_file}")
