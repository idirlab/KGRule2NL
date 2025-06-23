import pandas as pd

# Load the CSV file (replace 'input.csv' with your file path)
df = pd.read_csv('output-gemini-all100.csv')

# Define the extraction function
def extract_explanation(text):
    if isinstance(text, str):
        marker = "The explanation for this rule is:"
        if marker in text:
            return text.split(marker, 1)[1].strip()
    return ""

# Apply the function to the 'explanation' column
df['exp2'] = df['explanation'].apply(extract_explanation)

# Save the updated DataFrame to a new CSV
df.to_csv('parsed-output-gemini-all100.csv', index=False)
