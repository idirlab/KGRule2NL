import pandas as pd
from openai import OpenAI
import time 
pd.set_option('display.max_colwidth', None)

# Initialize OpenAI client
client = OpenAI()

# Define a function to call the API on a rule 
def call_openai_api(row):
    rule = row['Rule']
    type = row['Variable_Types']
    rformat = "The explanation for this rule is: Your explanation should be stated here"

    system_prompt = """You are an expert in semantic knowledge graphs. Your job is to translate logical rules from a knowledge graph into concise, clear, accurate, and meaningful English sentences.

In these rules, relations follow specific formats:
- '/domain/type/label' (e.g., '/award/award_category/winners': which means who are the winners? or which works are winners?)
- Concatenated relations: '/domain1/type1/label1-/domain2/type2/label2'

You do not need to mention domains or types of the relations explicitly in your output, but use them to infer the most specific and relevant real-world interpretation of the rule. 

Also, each variable entity in the rule is typed — for example, '?a': ['/film/film', '/award/competition'] — and your explanation should select the **most contextually appropriate type** based on the relationships and their domains.
Avoid generic words like 'entity'; use specific terms like 'film', 'person', 'TV episode', etc."""


    user_prompt = f"""Let's think step by step to generate an accurate and clear explanation for this rule. Return each step's output. 
Q: ?b /biology/genomic_locus/annotation ?a => ?a /biology/gene/locus ?b
**Step 1**: Parse the rule and identify the constant entities (which can be None), variable entities, and relations. 

**Step 2**: For each variable entity, first identify its list of types from the provided list:  
{{'?b': "['/biology/genomic_locus']", '?a': "['/biology/gene']"}}. Then, based on the majority domain or semantic theme of the relationships in the rule, choose THE MOST contextually appropriate type for each variable entity. 

**Step 3**: Try to understand each RDF triple, subject_entity relation object_entity, one by one. Use the types and relations to understand them better. 

**Step 4**: Use all the information above to infer what the rule is implying. 

**Step 5**: Write a CONCISE, CLEAR, ACCURATE, and MEANINGFUL explanation of the rule in this format:  
{rformat}
A: 
**Step 1**: 
- Constant entities: 
    - None
- Variable entities: 
    - ?b 
    - ?a
- Relations: 
    - /biology/genomic_locus/annotation
    - /biology/gene/locus

**Step 2**:
- ?b: /biology/genomic_locus
- ?a: /biology/gene

**Step 3**:
1. Subject: ?b, Relation: '/biology/genomic_locus/annotation', Object: ?a.
Interpretation: The annotation of genomis_locus ?b is gene ?a. 
2. Subject: ?a, Relation: '/biology/gene/locus', Object: ?b.
Interpretation: The locus of gene ?a is genomic_locus ?b. 

**Step 4**:
If the annotation of genomis_locus ?b is gene ?a, then the locus of gene ?a is genomic_locus ?b. 

**Step 5**:
The explanation for this rule is: If a gene is an annotation of a genomic locus, then that gene is located at that genomic locus.

Q: ?b /event/speech_or_presentation/speaker_s-/event/speech_or_presentation/presented_work ?f ?a /event/speech_or_presentation/type_or_format_of_presentation-/event/speech_or_presentation/presented_work ?f => ?a /event/speech_or_presentation/type_or_format_of_presentation-/event/speech_or_presentation/speaker_s ?b
**Step 1**: Parse the rule and identify the constant entities (which can be None), variable entities, and relations. 

**Step 2**: For each variable entity, first identify its list of types from the provided list:  
{{'?b': "['/event/public_speaker', '/business/board_member', '/people/person']", '?f': "['/event/presented_work', '/book/written_work']", '?a': "['/event/type_of_public_presentation']"}}. Then, based on the majority domain or semantic theme of the relationships in the rule, choose THE MOST contextually appropriate type for each variable entity. 

**Step 3**: Try to understand each RDF triple, subject_entity relation object_entity, one by one. Use the types and relations to understand them better. 

**Step 4**: Use all the information above to infer what the rule is implying. 

**Step 5**: Write a CONCISE, CLEAR, ACCURATE, and MEANINGFUL explanation of the rule in this format:  
{rformat}
A: 
**Step 1**: 
- Constant entities: 
    - None
- Variable entities: 
    - ?b 
    - ?f
    - ?a
- Relations: 
    - /event/speech_or_presentation/speaker_s-/event/speech_or_presentation/presented_work
    - /event/speech_or_presentation/type_or_format_of_presentation-/event/speech_or_presentation/presented_work
    - /event/speech_or_presentation/type_or_format_of_presentation-/event/speech_or_presentation/speaker_s

**Step 2**:
- ?b: /event/public_speaker
- ?f: /event/presented_work
- ?a: /event/type_of_public_presentation

**Step 3**:
1. Subject: ?b, Relation: '/event/speech_or_presentation/speaker_s-/event/speech_or_presentation/presented_work', Object: ?f.
Interpretation: The public speaker ?b is the speaker or presenter of presented work ?f. 
2. Subject: ?a, Relation: '/event/speech_or_presentation/type_or_format_of_presentation-/event/speech_or_presentation/presented_work', Object: ?f.
Interpretation: ?a is the type or format of presentation of presented work ?f. 
3. Subject: ?a, Relation: '/event/speech_or_presentation/type_or_format_of_presentation-/event/speech_or_presentation/speaker_s', Object: ?b.
Interpretation: Type or format of speaker ?b's presentation is type or format ?a.

**Step 4**:
If the public speaker ?b is the speaker or presenter of presented work ?f and ?a is the type or format of presentation of presented work ?f then type or format of speaker ?b's presentation is type or format ?a. 

**Step 5**:
The explanation for this rule is: If a person is the speaker of a work that was presented in a certain format, then they delivered their presentation in that same format.

Q: {rule} 
**Step 1**: Parse the rule and identify the constant entities (which can be None), variable entities, and relations. 

**Step 2**: For each variable entity, first identify its list of types from the provided list:  
{type}. Then, based on the majority domain or semantic theme of the relationships in the rule, choose THE MOST contextually appropriate type for each variable entity. 

**Step 3**: Try to understand each RDF triple, subject_entity relation object_entity, one by one. Use the types and relations to understand them better. 

**Step 4**: Use all the information above to infer what the rule is implying. 

**Step 5**: Write a CONCISE, CLEAR, ACCURATE, and MEANINGFUL explanation of the rule in this format:  
{rformat}
A: 
"""

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", #"gpt-4o-mini", #
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

df['explanation'] = df.apply(call_openai_api, axis=1)

# End measuring time and print the duration
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")

df.to_csv('output.csv', index=False)

