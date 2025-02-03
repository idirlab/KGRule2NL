# Natural Language Explanation of Logical Rules in Knowledge Graphs

We investigate the effectiveness of using OpenAI's GPT model to generate natural language explanations for logical rules. 
We mine the rules by the AMIE 3.5.1 rule discovery algorithm from the benchmark dataset FB15k-237, and two large-scale datasets, FB-CVT-REV and FB+CVT-REV. We generate these explanations using different types of prompts ( such as one-shot (by providing an example to the model), incorporating an instantiation of the rule, and including the types of variable entities in the rule) and validate their effectiveness through a thorough human annotation study. Our results indicate promising performance in terms of correctness and clarity of the explanations, though challenges remain for future work.

All our scripts and data are available in this repository. 



