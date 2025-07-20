# The wrapper class for the fine-tuned BERT model.

# To use the fine-tuned BERT model with LangChain, need to create a
# simple wrapper class. This class will inherit from LangChain's Embeddings
# base class and implement the embedding logic using my model.

import torch
from typing import List
from transformers import AutoTokenizer, AutoModel
from langchain_core.embeddings import Embeddings


class CustomBertEmbedder(Embeddings):
    """
    A custom LangChain embedder that uses a fine-tuned BERT model from Hugging Face.

    This class handles the tokenization, model inference, and pooling necessary
    to generate sentence-level embeddings for documents and queries.
    """
    def __init__(self, model_path: str):
        # 1. Set the device (use GPU if available, otherwise CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # 2. Load the tokenizer and model from the specified path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path)

        # 3. Move the model to the selected device
        self.model.to(self.device)

        # 4. Set the model to evaluation mode (important for consistent outputs)
        self.model.eval()

    # Mean Pooling Function to get a single sentence embedding
    def _mean_pooling(self, model_output, attention_mask):
        # The model output is the last_hidden_state
        token_embeddings = model_output[0]

        # Expand attention mask to match the dimensions of token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

        # Sum embeddings where attention mask is 1, and divide by the number of such tokens
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        return sum_embeddings / sum_mask

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of documents.
        """
        # We don't need to calculate gradients for inference, so this saves memory and computation
        with torch.no_grad():
            # 1. Tokenize the batch of texts
            model_inputs = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                return_tensors="pt"
            ).to(self.device)

            # 2. Get model outputs
            model_outputs = self.model(**model_inputs)

            # 3. Perform mean pooling to get sentence embeddings
            sentence_embeddings = self._mean_pooling(model_outputs, model_inputs['attention_mask'])

            # 4. Move embeddings to CPU and convert to a list of lists
            return sentence_embeddings.cpu().tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Generates an embedding for a single query text.
        """
        # For a single query, we can just call embed_documents with a list containing one item
        # This reuses the same batch-processing logic for simplicity.
        document_embeddings = self.embed_documents([text])
        return document_embeddings[0]
