import os
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict, ClassLabel
from transformers import AutoTokenizer
from src.logger import get_logger

logger = get_logger("prepare_data")

# Paths
scripts_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(scripts_dir)
extracted_emails_path = os.path.join(root_dir, "data/extracted_emails.csv")
names_txt_path = os.path.join(root_dir, "data/names.txt")
tokenized_dataset_path = os.path.join(root_dir, "data/tokenized_dataset")

# Sanity checks
assert os.path.exists(extracted_emails_path), "Email CSV not found!"
assert os.path.exists(names_txt_path), "Label names file not found!"

# Load and validate
df = pd.read_csv(extracted_emails_path)
assert "subject" in df.columns and "text" in df.columns and "label" in df.columns
df["subject"] = df["subject"].fillna("")
df["text"] = df["text"].fillna("")
logger.info(f"Loaded {len(df)} emails.")

dataset = Dataset.from_pandas(df)
new_features = dataset.features.copy()
new_features["label"] = ClassLabel(names_file=names_txt_path)
dataset = dataset.cast(new_features)

# Stratified splits
df = dataset.to_pandas()
train_val_df, test_df = train_test_split(df, test_size=0.1, stratify=df["label"], random_state=42)
train_df, val_df = train_test_split(train_val_df, test_size=0.1, stratify=train_val_df["label"], random_state=42)

logger.info(f"Split sizes - Train: {len(train_df)}, Validation: {len(val_df)}, Test: {len(test_df)}")

train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)
test_dataset = Dataset.from_pandas(test_df)

final_splits = DatasetDict({
    "train": train_dataset,
    "validation": val_dataset,
    "test": test_dataset
})

checkpoint = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)


def safe_str(x):
    return str(x) if x is not None else ""


def tokenize_function(examples):
    subjects = [safe_str(s) for s in examples["subject"]]
    texts = [safe_str(t) for t in examples["text"]]
    return tokenizer(subjects, texts, truncation=True)


logger.info("Tokenizing dataset...")
tokenized_datasets = final_splits.map(tokenize_function, batched=True)
tokenized_datasets.save_to_disk(tokenized_dataset_path)
logger.info(f"Saved tokenized dataset to {tokenized_dataset_path}")
