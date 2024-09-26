import pandas as pd
from openai import OpenAI
import time 
pd.set_option('display.max_colwidth', None)

# Initialize OpenAI client
client = OpenAI()

# Define a function to call the API on a rule 
def call_openai_api(rule):
    rformat = "The explanation for this rule is: Your explanation should be stated here"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "As a helpful, respectful, and harmless assistant, help me generate natural language explanation for a logical rule from my knowledge graph. \
             For your information, the relationships between entities in my knowledge graph have a specific format. For example in the relationship '/award/award_category/winners', \
             'award' is the general domain of the relationship, 'award_category' is the type of the relationship, and 'winners' is the label of the relationship. \
             Some relationships are concatenation of two relations and thus have the following format: '/domain1/type1/label1./domain2/type2/label2'. \
             You do not need to mention the domain and the type explicitly but use them to better understand the rule."},
            {"role": "user", "content": f"""Generate a concise, clear, accurate, and readable natural language explanation for the following rule from my knowledge graph: {rule}\
             provide the explanation in the following format: {rformat}. For example when the input is \
             'Grammy Award for Best Contemporary Jazz Album /award/award_category/winners./award/award_honor/ceremony ?a => ?a /time/event/instance_of_recurring_event Grammy Awards', \
             the output should be 'The explanation for this rule is: When Grammy Award for Best Contemporary Jazz Album is awarded in an award ceremony “a”, then award ceremony “a”  is an instance of the recurring event, Grammy Awards' """ }
        ]
    )
    return completion.choices[0].message.content

# Load the rules into a Pandas df 
df = pd.read_csv('output_rules_imp_sort.csv')

# Start measuring time
start_time = time.time()

# Apply the function to each cell in the 'Rule' column
df['explanation'] = df['Rule'].apply(call_openai_api)

# End measuring time and print the duration
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")

df.to_csv('output_rules_imp_sort_one.csv', index=False)

