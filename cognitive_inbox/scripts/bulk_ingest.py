# bulk_ingest.py

import time
from langchain.text_splitter import RecursiveCharacterTextSplitter

from cognitive_inbox.data_ingestion import email_parser
from cognitive_inbox.embeddings import custom_bert_embedder
from cognitive_inbox.vectorstore import chroma_manager
from cognitive_inbox import config


def run_bulk_ingestion():
    """
    Orchestrates the entire bulk ingestion process from Gmail to ChromaDB.
    """
    print("--- Starting Bulk Email Ingestion ---")

    # --- 1. Initialization ---
    print("\n[Step 1/5] Initializing services and models...")

    gmail_service = email_parser.get_gmail_service()
    if not gmail_service:
        print("Failed to get Gmail service. Aborting.")
        return

    print("Fetching Gmail label mapping...")
    label_map = email_parser.get_label_map(gmail_service)
    if not label_map:
        print("Could not fetch label map. Labels will not be ingested.")

    print("Loading custom embedding model...")

    embedder = custom_bert_embedder.CustomBertEmbedder(
        model_path=config.EMBEDDING_MODEL_PATH
    )

    print("Connecting to vector store...")
    chroma_collection = chroma_manager.get_chroma_collection()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    print("Initialization complete.")

    # --- 2. Fetch Email IDs ---
    print("\n[Step 2/5] Fetching all email IDs from your inbox...")
    message_ids = email_parser.list_message_ids(gmail_service)
    if not message_ids:
        print("No emails found. Aborting.")
        return
    print(f"Found {len(message_ids)} total emails to process.")

    # --- 3. Process and Ingest Emails in Batches ---
    print("\n[Step 3/5] Parsing, chunking, embedding, and storing emails...")
    batch_size = 50
    total_chunks = 0

    for i in range(0, len(message_ids), batch_size):
        batch_ids = message_ids[i:i + batch_size]

        documents_to_add = []
        metadatas_to_add = []
        ids_to_add = []

        print(f"\n--- Processing batch {i // batch_size + 1}/{(len(message_ids) // batch_size) + 1} ---")

        for msg_id in batch_ids:
            parsed_email = email_parser.parse_email(
                gmail_service, label_map=label_map, message_id=msg_id
            )

            if parsed_email and parsed_email['body']:

                clean_metadata = {
                    "source_email_id": parsed_email.get('id', 'unknown_id'),
                    "subject": parsed_email.get('subject') or "",
                    "from": parsed_email.get('from') or "",
                    "date": parsed_email.get('date') or 0.0,  # Replace None with 0.0 for float
                    "labels": parsed_email.get('labels') or ""
                }

                chunks = text_splitter.split_text(parsed_email['body'])

                for j, chunk in enumerate(chunks):
                    documents_to_add.append(chunk)

                    metadatas_to_add.append(clean_metadata)

                    ids_to_add.append(f"{clean_metadata['source_email_id']}_{j}")

        if documents_to_add:
            print(f"Generating embeddings for {len(documents_to_add)} chunks...")
            embeddings_to_add = embedder.embed_documents(documents_to_add)

            chroma_collection.add(
                embeddings=embeddings_to_add,
                documents=documents_to_add,
                metadatas=metadatas_to_add,
                ids=ids_to_add
            )

            total_chunks += len(documents_to_add)
            print(f"Processed {len(batch_ids)} emails, added {len(documents_to_add)} chunks to the database.")

        time.sleep(1)

    # --- 4. Verification ---
    print("\n[Step 4/5] Verifying ingestion...")
    count = chroma_collection.count()
    print(f"Verification complete. The database now contains {count} document chunks.")

    print("\n[Step 5/5] --- Bulk Ingestion Finished ---")


if __name__ == '__main__':
    run_bulk_ingestion()
