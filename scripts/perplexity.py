import pandas as pd
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# load pre-trained GPT-2 model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
model.eval()

# function to compute perplexity for a sentence
def compute_perplexity(sentence):
    # Tokenize and encode the input sentence
    inputs = tokenizer(sentence, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        perplexity = torch.exp(loss)
    return perplexity.item()

def main():
    # read rules and their explanations 
    df = pd.read_csv('filtered_rules_explanation.csv')

    # add new columns for perplexity scores
    df['perplexity1_s'] = df['explanation1_s'].apply(compute_perplexity)
    print("done")
    df['perplexity2_y'] = df['explanation2_y'].apply(compute_perplexity)
    print("done")
    df.to_csv('filtered_rules_explanation_perp.csv', index=False)

if __name__ == "__main__":
    main()