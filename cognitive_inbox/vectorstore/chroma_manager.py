# cognitive_inbox/vectorstore/chroma_manager.py

import chromadb
from cognitive_inbox import config

# Define the name for our collection. Using a constant makes it easy to reference.
COLLECTION_NAME = "gmail_embeddings"


def get_chroma_collection():
    """
    Initializes a persistent ChromaDB client and gets or creates a collection.

    This function acts as a singleton provider for the ChromaDB collection.
    It ensures that we are always working with the same persistent database
    located at the path specified in our config.

    Returns:
        chromadb.Collection: The ChromaDB collection object to interact with.
    """
    # 1. Initialize the ChromaDB client with persistence.
    #    The client will save its data to the specified directory.
    client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)

    # 2. Get or create the collection.
    #    If a collection with COLLECTION_NAME already exists, it will be loaded.
    #    If not, it will be created.
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    print(f"Successfully connected to ChromaDB. Collection '{COLLECTION_NAME}' is ready.")
    return collection
