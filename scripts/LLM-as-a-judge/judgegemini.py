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
    type = row['Variable_Types']
    instance = row['Instance']
    explanation = row['Explanation']
    rformat = "Correctness: Your score from 1-5 should be written here"

    user_prompt = f"""You are a strict expert judge evaluating natural language explanations of logical rules from a knowledge graph in terms of correctness. Your task is to assign a score from 1 to 5 for each explanation:

---
Definition of Correctness: How accurately does the explanation reflect the actual logic, meaning and semantic of the rule? You have to check all the triples, aka atoms, in the rule and check whether they are all correctly expressed in the explanation, and the logical flow makes sense too.

Scoring Guide:
- 5 = Fully correct — captures all logical implications of the rule.
- 4 = Mostly correct — main logic is right, with minor flaws or omissions.
- 3 = Partially correct — some correct elements, but key parts are wrong or missing.
- 2 = Mostly incorrect — major misinterpretation, with only partial relevance.
- 1 = Completely incorrect — misrepresents or contradicts the rule.

Think step by step and evaluate the explanation below using the provided rule, variable types, and one instance of the rule.
Each variable in the rule (e.g., ?a, ?b) has an associated type. These types describe what kind of real-world entity the variable might represent. For example, '?a': '/people/person' means that ?a could be a person.
Use these types and the instance of the rule to better understand the rule to help you judge the correctness of the explanation.
DO NOT GENERATE THE EXPLANATION. JUST COMPARE THE RULE WITH THE EXPLANATION PROVIDED TO YOU. 
---
Think step by step. Then respond the final score in this format: {rformat}

Q: 
**RULE:**  
?f /soccer/football_player_match_participation/team ?b ?a /soccer/football_match/players ?f => ?a /soccer/football_match/teams ?b

**VARIABLE TYPES:**  
'?b': '/soccer/football_team', '?a': '/soccer/football_match'

**EXAMPLE INSTANCE OF THE RULE:**  
78546592 /soccer/football_player_match_participation/team Borussia M‚Äö√Ñ√∂‚àö‚Ä†‚àö‚àÇ‚Äö√Ñ√∂‚àö‚Ä†‚àö√°nchengladbach Borussia Monchengladbach vs Mainz football match /soccer/football_match/players 78546592 => Borussia Monchengladbach vs Mainz football match /soccer/football_match/teams Borussia M‚Äö√Ñ√∂‚àö‚Ä†‚àö‚àÇ‚Äö√Ñ√∂‚àö‚Ä†‚àö√°nchengladbach

**GENERATED EXPLANATION:**  
If a team participates in a match, and that match has players that belong to another match, then the latter match also features that team.

A: 
Thought process: 
1. Are all constant and variable entities expressed in the explanation? yes. team, match, and play are all mentioned. 
2. Are all the relations expressed in the explanation? No, The team of player ?f is ?b and it is not mentioned.
3. Are all the triples(atoms) match semantically with the explanation? The first atom ?f /soccer/football_player_match_participation/team ?b is not mentioned and this wrong part is mentioned instead: If a team participates in a match
4. Is the logical flow of the explanation consistent with the logic of the rule? No, for example we only have one match in the rule but the explanation mentions "another" match

Correctness: 2
---
Q: 
**RULE:**  
{rule}

**VARIABLE TYPES:**  
{type}

**EXAMPLE INSTANCE OF THE RULE:**  
{instance}

**GENERATED EXPLANATION:**  
{explanation}

A:
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
df = pd.read_csv('judge_input.csv')
# Start measuring time
start_time = time.time()

df['evaluation'] = df.apply(call_gemini_api, axis=1)

# End measuring time and print the duration
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")

df.to_csv('judge_output.csv', index=False)

