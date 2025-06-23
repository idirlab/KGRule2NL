import pandas as pd
import time 
from google import genai
from google.genai import types
import os

pd.set_option('display.max_colwidth', None)

# Use Gemini Flash model
client = genai.Client()

# Define a function to call the API on a rule 
def call_gemini_api(row, max_retries=5):
    
    rule = row['Rule']
    instance = row['Instance']
    rformat = "Each variable and its type should be itemized in a numbered list here."
    user_prompt = f"""
    You are given a symbolic rule from a knowledge graph, along with one example instance of that rule. Your task is to guess the most likely real-world type of each **variable entity** in the rule.

---

**Definition: Variable Entity**
In the rule, variable entities are represented by symbols like `?a`, `?b`, `?f`, etc. These are placeholders that refer to real-world entities. Your job is to infer what kind of thing each variable represents (e.g., person, gene, city, book, football match) based on:

1. The structure of the rule (subject–predicate–object triples).
2. The **relation labels** used in those triples (e.g., `/film/film/director`).
3. The provided **example instance** that fills in actual values for those variables.

---

**Instructions:**

1. First, identify and list the variable entities in the rule.
2. Then, for each variable, guess its most likely real-world type based on the **example instance**, **rule structure**, and **relation labels**.
3. Output your answer as a **numbered list**, where each item corresponds to one variable and includes:
   - The variable name (e.g., ?a)
   - Your guessed type (e.g., "football player")

---
**RULE:**  
{rule}

**EXAMPLE INSTANCE OF THE RULE:**  
{instance}

---

Now follow the instructions and provide your answer in the following format: {rformat}
 """


    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=512
            )
        )
        time.sleep(5)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Load the rules into a Pandas df 
df = pd.read_csv('outputg.csv')
# Start measuring time
start_time = time.time()

df['type'] = df.apply(call_gemini_api, axis=1)

# End measuring time and print the duration
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")

df.to_csv('outputgtype.csv', index=False)

