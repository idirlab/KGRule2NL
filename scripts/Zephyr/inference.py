"""
Inference script: Load trained model and generate outputs for test set
"""

from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq
from peft import PeftModel
from datasets import Dataset
import pandas as pd
import torch
from torch.utils.data import DataLoader
import os

# ------------------ Clear CUDA cache ------------------

torch.cuda.empty_cache()

# ------------------ Load the fine-tuned model and tokenizer ------------------

base_model_name = "HuggingFaceH4/zephyr-7b-beta"
finetuned_model_path = "/rule2text/bzephyr_finetuned"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(finetuned_model_path)

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

print("Loading PEFT adapters...")
model = PeftModel.from_pretrained(base_model, finetuned_model_path)

# Ensure model is in eval mode
model.eval()

# ------------------ Load test data ------------------

print("Loading test data...")
test_df = pd.read_excel("/rule2text/btest.xlsx")
test_dataset = Dataset.from_pandas(test_df)

# ------------------ Tokenization function for inference (prompt only) ------------------

def tokenize_for_inference(example):
    prompt = example['prompt']
    
    # Only tokenize the prompt for inference
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

# Tokenize test dataset
print("Tokenizing test data...")
tokenized_test = test_dataset.map(
    tokenize_for_inference, 
    batched=False, 
    remove_columns=['prompt']  # Remove prompt column but keep explanation if it exists
)

# ------------------ Set up data loader ------------------

# Create a dataset with only the fields the model needs
# Ensure only numeric columns are included in DataLoader
columns_to_keep = ['input_ids', 'attention_mask']
model_input_dataset = tokenized_test.remove_columns(
    [col for col in tokenized_test.column_names if col not in columns_to_keep]
)


data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True
)

test_loader = DataLoader(
    model_input_dataset,
    batch_size=2,  # Adjust based on your GPU memory
    collate_fn=data_collator
)

# ------------------ Generate outputs ------------------

print("Generating explanations...")
generated_texts = []

with torch.no_grad():
    for batch_idx, batch in enumerate(test_loader):
        print(f"Processing batch {batch_idx + 1}/{len(test_loader)}")
        
        input_ids = batch['input_ids'].to(model.device)
        attention_mask = batch['attention_mask'].to(model.device)
        
        # Generate outputs
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=512,
            do_sample=False,  # Use greedy decoding for consistent results
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
            temperature=1.0,
            repetition_penalty=1.1
        )
        
        # Extract only the generated part (remove input prompt)
        generated = outputs[:, input_ids.shape[1]:]
        texts = tokenizer.batch_decode(generated, skip_special_tokens=True)
        generated_texts.extend(texts)

print(f"Generated {len(generated_texts)} explanations")

# ------------------ Save generated outputs ------------------

print("Saving results...")

# Save just the generated texts
with open("/rule2text/btest_generated_explanations.txt", "w", encoding='utf-8') as f:
    for text in generated_texts:
        f.write(text.strip() + "\n")

# Save detailed results with prompts for analysis
results_df = pd.DataFrame({
    'generated_explanation': [text.strip() for text in generated_texts]
})

results_df.to_excel("/rule2text/btest_results_detailed.xlsx", index=False)

print("Results saved to:")
print("- test_generated_explanations.txt (generated texts only)")
print("- test_results_detailed.xlsx (full comparison)")
