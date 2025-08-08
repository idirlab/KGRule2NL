import pandas as pd
from openai import OpenAI
import time 
pd.set_option('display.max_colwidth', None)

# Initialize OpenAI client
client = OpenAI()

# Define a function to call the API on a rule to judge
def call_openai_api(row):
    rule = row['Rule']
    type = row['Variable_Types']
    instance = row['Instance']
    explanation = row['Explanation2']
    rformat = "1.Correctness: Your score from 1-5 should be written here, 2.Clarity: Your score from 1-5 should be written here"

    system_prompt = f""" You are an expert evaluator of knowledge graph rule explanations. Your job is to assess how well a generated explanation captures the logic of a rule (correctness) and how easy it is to read (clarity). You will be given a symbolic rule, variable types, an example instance of the rule, and a generated explanation. You must score the explanation on two metrics, each from 1 to 5, and respond in a strict, fixed format.
"""

    user_prompt = f"""You are an expert judge evaluating natural language explanations of logical rules from a knowledge graph. Your task is to assign two scores from 1 to 5 for each explanation:

---

**Metric 1: Correctness**

Definition: How accurately does the explanation reflect the actual logic, meaning and semantic of the rule? You have to check all the triples, aka atoms, in the rule and check whether they are all correctly expressed in the explanation, and the logical flow makes sense too.

Scoring Guide:
- 5 = Fully correct — captures all logical implications of the rule.
- 4 = Mostly correct — main logic is right, with minor flaws or omissions.
- 3 = Partially correct — some correct elements, but key parts are wrong or missing.
- 2 = Mostly incorrect — major misinterpretation, with only partial relevance.
- 1 = Completely incorrect — misrepresents or contradicts the rule.

---

**Metric 2: Clarity**

Definition: How easy is the explanation to read and understand on its own?

Scoring Guide:
- 5 = Very clear — well-written, natural, and easy to follow.
- 4 = Mostly clear — understandable with slight awkwardness.
- 3 = Somewhat clear — readable but contains unclear or odd phrasing.
- 2 = Hard to read — confusing structure or vague wording.
- 1 = Very unclear — incoherent or poorly written.

---
Think step by step and evaluate the explanation below using the provided rule, variable types, and one instance of the rule.
Each variable in the rule (e.g., ?a, ?b) has an associated list of possible types. These types describe what kind of real-world entity the variable might represent. For example, '?a': ['/people/person', '/sports/athlete'] means that ?a could be a person or an athlete.
Use the most relevant types to this rule, and the instance of the rule to better understand what each variable likely refers to and to help you judge the correctness of the explanation.


---
Think step by step, and explain your answer. Then respond the final scores **only** in this format: {rformat}

Q: 
**RULE:**  
?f /soccer/football_player_match_participation/team ?b ?a /soccer/football_match/players ?f => ?a /soccer/football_match/teams ?b

**VARIABLE TYPES:**  
{{'?b': "['/sports/sports_team', '/soccer/football_team', '/business/sponsored_recipient']", '?a': "['/soccer/football_match', '/time/event']"}}

**EXAMPLE INSTANCE OF THE RULE:**  
78546592 /soccer/football_player_match_participation/team Borussia M‚Äö√Ñ√∂‚àö‚Ä†‚àö‚àÇ‚Äö√Ñ√∂‚àö‚Ä†‚àö√°nchengladbach Borussia Monchengladbach vs Mainz football match /soccer/football_match/players 78546592 => Borussia Monchengladbach vs Mainz football match /soccer/football_match/teams Borussia M‚Äö√Ñ√∂‚àö‚Ä†‚àö‚àÇ‚Äö√Ñ√∂‚àö‚Ä†‚àö√°nchengladbach

**GENERATED EXPLANATION:**  
If a team participates in a match, and that match has players that belong to another match, then the latter match also features that team.
A: 
Thought process: 
1. Based on the list of varuable types and the instance of the rule variable ?f refers to a player, variable ?b refers to a team, and variable ?a refers to a match.
2. The rule says if ?b is team of player ?f and ?f is one of the players of match ?a, then ?b is one of the teams of the match ?a. 
3. The generated explanation is "If a team participates in a match, and that match has players that belong to another match, then the latter match also features that team."
4. The first part "If a team participates in a match" is relatively wrong. because this is the conclusion of the rule and should not be stated as "if". The second part, "that match has players that belong to another match", is partially correct but "another match" is wrong and was never mentioned in the rule. The last part, "the latter match also features that team" is partially correct. But not completely. Because we are only talking about one match. the "latter" is wrong. 
5. Since the first triple or atom of the rule is never mentioned, and the other two atoms are partially correct, the explanation is mostly incorrect. So the correctness score is 2. 

In terms of clarity, it relatively reads smooth. However, at some part it gets confusing and awkward by repeatedly mentioning "match". So the score is 4. 

1.Correctness: 2, 2.Clarity: 4
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

    completion = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {
              "role": "system",
              "content": system_prompt
            },
            {
              "role": "user",
              "content": user_prompt
            }
        ]
    )
    return completion.choices[0].message.content

# Load the rules into a Pandas df 
df = pd.read_csv('input.csv')
# Start measuring time
start_time = time.time()

df['judgement'] = df.apply(call_openai_api, axis=1)

# End measuring time and print the duration
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")

df.to_csv('output.csv', index=False)

