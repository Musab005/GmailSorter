# verify_db.py

import os
import chromadb
from cognitive_inbox import config


def verify_chroma_database():
    """
    Connects to the local ChromaDB and prints statistics for verification.
    """
    db_path = config.CHROMA_DB_PATH
    collection_name = config.CHROMA_COLLECTION

    print("--- Starting ChromaDB Verification ---")

    if not os.path.exists(db_path):
        print(f"\nERROR: Database path does not exist: '{db_path}'")
        return

    print(f"\n[1/3] Connecting to database at: '{db_path}'...")
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name=collection_name)
        print("Successfully connected to the collection.")
    except Exception as e:
        print(f"\nERROR: Failed to connect to the collection '{collection_name}'.")
        print(f"Details: {e}")
        return

    print("\n[2/3] Fetching database statistics...")
    try:
        count = collection.count()
        print(f" ✅ Total document chunks in the database: {count}")
    except Exception as e:
        print(f"ERROR: Could not get a count from the database. Error: {e}")
        return

    print("\n[3/3] Fetching 5 sample documents for a sanity check...")
    try:
        sample = collection.get(
            limit=5,
            include=["metadatas", "documents"]
        )

        if not sample or not sample.get('ids'):
            print(" Could not retrieve any sample documents. The database might be empty.")
            return

        for i, doc_id in enumerate(sample['ids']):
            print(f"\n--- Sample {i + 1} ---")
            metadata = sample['metadatas'][i]
            document_text = sample['documents'][i][:200] + "..."  # Preview first 200 chars

            print(f"   ID: {doc_id}")
            print(f"   Metadata: {metadata}")
            print(f"   Document Preview: \"{document_text}\"")

        print("\n  Sanity check passed. Documents and metadata appear to be structured correctly.")

    except Exception as e:
        print(f"ERROR: Could not get samples from the database. Error: {e}")

    print("\n--- Verification Complete ---")


if __name__ == '__main__':
    verify_chroma_database()
