import time

import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

from cognitive_inbox.data_ingestion import email_parser
from cognitive_inbox.embeddings import custom_bert_embedder
from cognitive_inbox import config


def run_bulk_ingestion(collection1):
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

    print("Loading custom embedding model... (This may take a moment)")
    # THIS IS THE EMBEDDER WE MUST USE
    custom_embedder = custom_bert_embedder.CustomBertEmbedder(
        model_path=config.EMBEDDING_MODEL_PATH
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    print("Initialization complete.")

    # --- 2. Fetch Email IDs ---
    print("\n[Step 2/5] Fetching all email IDs from your inbox...")
    message_ids = email_parser.list_message_ids(service=gmail_service, limit=10)
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
                chunks = text_splitter.split_text(parsed_email['body'])

                for j, chunk in enumerate(chunks):
                    documents_to_add.append(chunk)

                    metadatas_to_add.append({
                        "source_email_id": parsed_email['id'],
                        "subject": parsed_email['subject'],
                        "from": parsed_email['from'],
                        "date": parsed_email['date'],
                        "labels": parsed_email['labels']
                    })

                    ids_to_add.append(f"{parsed_email['id']}_{j}")

        if documents_to_add:
            print(f"Generating embeddings for {len(documents_to_add)} chunks...")
            embeddings_to_add = custom_embedder.embed_documents(documents_to_add)

            collection1.add(
                embeddings=embeddings_to_add,
                documents=documents_to_add,
                metadatas=metadatas_to_add,
                ids=ids_to_add
            )

            total_chunks += len(documents_to_add)
            print(f"Processed {len(batch_ids)} emails, added {len(documents_to_add)} chunks to the database.")

        time.sleep(1)

    # --- 4. Final Verification ---
    print("\n[Step 4/5] Verifying ingestion...")
    count = collection1.count()
    print(f"Verification complete. The database now contains {count} document chunks.")

    print("\n[Step 5/5] --- Bulk Ingestion Finished ---")


# TODO: check docs for how the query function works
# need to embed queries with custom model probably
def run_test_query(collection2):
    queries = ["Meezan bank newsletter", "Google account security", "Hydro quebec bill"]
    custom_embedder = custom_bert_embedder.CustomBertEmbedder(
        model_path=config.EMBEDDING_MODEL_PATH
    )
    embeddings = custom_embedder.embed_documents(queries)

    results = collection2.query(
        query_embeddings=embeddings,
        n_results=1
    )

    print(results)

    for i, query_results in enumerate(results["documents"]):
        print(f"\nQuery {i}")
        print("\n".join(query_results))


if __name__ == '__main__':
    print("Connecting to vector store...")
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name="test_email_collection")
    run_bulk_ingestion(collection)

    run_test_query(collection)
