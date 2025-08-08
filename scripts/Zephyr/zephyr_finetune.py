from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, BitsAndBytesConfig
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model
from datasets import Dataset, DatasetDict
import pandas as pd
import torch
import os

# ------------------ Clear CUDA cache before starting ------------------

torch.cuda.empty_cache()

# ------------------ Load Excel files and convert to DatasetDict ------------------

def load_excel_to_dataset(path):
    df = pd.read_excel(path)
    return Dataset.from_pandas(df)

dataset = DatasetDict({
    "train": load_excel_to_dataset("/rule2text/train.xlsx"),
    "validation": load_excel_to_dataset("/rule2text/valid.xlsx"),
    "test": load_excel_to_dataset("/rule2text/test.xlsx"),
})

# ------------------ Define model and tokenizer with 4-bit loading + QLoRA PEFT ------------------

model_name = "HuggingFaceH4/zephyr-7b-beta"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Ensure eos_token is defined
if tokenizer.eos_token is None:
    tokenizer.eos_token = tokenizer.pad_token

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto"
)

# Enable gradient checkpointing
model.gradient_checkpointing_enable()

# Prepare model for k-bit training (PEFT QLoRA)
model = prepare_model_for_kbit_training(model)

# Define and attach LoRA adapters (QLoRA style)
lora_config = LoraConfig(
    r=16, 
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],  
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# ------------------ Tokenization function ------------------

def tokenize_fn(example):
    prompt = example['prompt']
    explanation = example['explanation']
    explanation += tokenizer.eos_token

    # Tokenize prompt (without target special tokens)
    prompt_tokens = tokenizer(prompt, truncation=True, max_length=1024, padding=False, add_special_tokens=False)

    # Tokenize target with special tokens
    target_tokens = tokenizer(explanation, truncation=True, max_length=512, padding=False, add_special_tokens=True)

    input_ids = prompt_tokens['input_ids'] + target_tokens['input_ids']
    attention_mask = prompt_tokens['attention_mask'] + target_tokens['attention_mask']

    # Labels: mask prompt tokens with -100
    labels = [-100] * len(prompt_tokens['input_ids']) + target_tokens['input_ids']

    # Truncate to max model length
    max_length = 2048
    input_ids = input_ids[:max_length]
    attention_mask = attention_mask[:max_length]
    labels = labels[:max_length]

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }

# Tokenize datasets
tokenized_ds = dataset.map(tokenize_fn, batched=False, remove_columns=dataset["train"].column_names)


# ------------------ Training arguments ------------------

training_args = TrainingArguments(
    output_dir="/rule2text/zephyr_finetuned",
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    num_train_epochs=2,
    learning_rate=5e-5,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10,
    save_total_limit=1,
    fp16=torch.cuda.is_available(),
)

# ------------------ Define Trainer ------------------

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_ds["train"],
    eval_dataset=tokenized_ds["validation"],
    tokenizer=tokenizer,
)

# ------------------ Fine-tune ------------------

trainer.train()

# ------------------ Evaluate on test set ------------------

metrics = trainer.evaluate(tokenized_ds["test"])
print("Test evaluation metrics:", metrics)


# ------------------ Save final model ------------------

model.save_pretrained("/rule2text/zephyr_finetuned")
tokenizer.save_pretrained("/rule2text/zephyr_finetuned")
