# To Reload Later:
# You (or a deployment service like Vertex AI) can load the model and tokenizer like this:
# from transformers import AutoModelForSequenceClassification, AutoTokenizer
# model = AutoModelForSequenceClassification.from_pretrained(model_path)
# tokenizer = AutoTokenizer.from_pretrained(model_path)

from transformers import AutoTokenizer
import os


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(scripts_dir, ".."))
    model_path = os.path.abspath(os.path.join(root_dir, "BERT_model"))
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    tokenizer.save_pretrained(model_path)


if __name__ == "__main__":
    main()
