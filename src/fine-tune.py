import os
# import torch
from transformers import Trainer, TrainingArguments, EarlyStoppingCallback, AutoModelForSequenceClassification, \
    AutoTokenizer
from sklearn.metrics import accuracy_score
from datasets import load_from_disk
from src.logger import get_logger

logger = get_logger("fine_tune")

# logger.info(f"CUDA Available: {torch.cuda.is_available()}")

scripts_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(scripts_dir)
tokenized_dataset_path = os.path.join(root_dir, "data/tokenized_dataset")
model_output_path = os.path.join(root_dir, "models/bert-finetuned")

loaded_datasets = load_from_disk(tokenized_dataset_path)
logger.info("Loaded tokenized dataset.")

checkpoint = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=51)


def compute_metrics(p):
    preds = p.predictions.argmax(-1)
    labels = p.label_ids
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}


# Define training arguments
training_args = TrainingArguments(
    output_dir=os.path.join(root_dir, "results"),
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=10,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    greater_is_better=True,
    logging_dir=os.path.join(root_dir, "logs"),
    logging_strategy="epoch",
    report_to="wandb"  # change to "none" if needed
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=loaded_datasets["train"],
    eval_dataset=loaded_datasets["validation"],
    processing_class=tokenizer,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
)

logger.info("Starting training...")
trainer.train()

logger.info("Evaluating on test set...")
test_results = trainer.evaluate(eval_dataset=loaded_datasets["test"])
for k, v in test_results.items():
    logger.info(f"{k}: {v:.4f}")

# Save best BERT_model
logger.info(f"Saving BERT_model to {model_output_path}...")
trainer.save_model(model_output_path)
tokenizer.save_pretrained(model_output_path)
logger.info("Model and tokenizer saved.")
