import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, DataCollatorForSeq2Seq
from datasets import Dataset
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

# -----------------------
# Load Zephyr base model and tokenizer
# -----------------------

model_name = "HuggingFaceH4/zephyr-7b-beta"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Loading base model...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

model.eval()

# -----------------------
# Read input Excel as Dataset
# -----------------------

print("Reading test data...")
input_df = pd.read_excel("/rule2text/btest.xlsx")  

# Convert to HF Dataset
test_dataset = Dataset.from_pandas(input_df)

# -----------------------
# Tokenization function
# -----------------------

def tokenize_for_inference(example):
    prompt = example['prompt']
    prompt_tokens = tokenizer(
        prompt,
        truncation=True,
        max_length=1024,
        padding=False,
        add_special_tokens=True
    )
    return {
        "input_ids": prompt_tokens['input_ids'],
        "attention_mask": prompt_tokens['attention_mask']
    }

print("Tokenizing data...")
tokenized_test = test_dataset.map(
    tokenize_for_inference,
    batched=False,
    remove_columns=['prompt','explanation','id']
)

# -----------------------
# DataLoader setup
# -----------------------

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True
)

test_loader = DataLoader(
    tokenized_test,
    batch_size=2,  # adjust based on GPU
    collate_fn=data_collator
)

# -----------------------
# Generate outputs
# -----------------------

print("Generating explanations...")
generated_texts = []

with torch.no_grad():
    for batch_idx, batch in enumerate(tqdm(test_loader)):
        input_ids = batch['input_ids'].to(model.device)
        attention_mask = batch['attention_mask'].to(model.device)

        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=512,
            do_sample=False,
            temperature=1.0,          
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
            repetition_penalty=1.1
        )

        # Extract only generated text (remove prompt)
        generated = outputs[:, input_ids.shape[1]:]
        texts = tokenizer.batch_decode(generated, skip_special_tokens=True)
        generated_texts.extend([text.strip() for text in texts])

print(f"Generated {len(generated_texts)} explanations")

# -----------------------
# Save results
# -----------------------

input_df['generated_explanation_base'] = generated_texts
output_path = "/rule2text/btest_generated_explanations_base.xlsx" 
input_df.to_excel(output_path, index=False)

print(f"Saved generated explanations to {output_path}")
