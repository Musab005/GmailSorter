from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import os
import uuid


def create_chunks():
    # chunk_size: Defines the maximum size of each chunk (in characters).
    # A good starting point is between 500 and 1000 characters.
    # chunk_overlap: Defines how many characters should overlap between consecutive chunks.
    # A good starting point is 100 to 200 characters.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""],  # Order of splitting
    )

    scripts_dir = os.path.dirname(__file__)
    app_dir = os.path.dirname(scripts_dir)
    project_root_dir = os.path.dirname(app_dir)
    data_raw_dir = os.path.join(project_root_dir, 'data/raw')
    data_processed_dir = os.path.join(project_root_dir, 'data/processed')
    email_csv_path = os.path.join(data_raw_dir, 'extracted_emails.csv')
    df = pd.read_csv(email_csv_path)

    chunks_mapping = {
        "chunk_id": [],
        "email_id": [],
        "from": [],
        "date": [],
        # "email_label": [],
        "email_subject": [],
        "chunk_text": []
    }

    print("Starting to chunk...")
    for index, row in df.iterrows():
        text = row.get("text")

        # Skip if text is missing or NaN
        if not isinstance(text, str) or pd.isna(text) or text.strip() == "":
            print(f"Skipping text: {text} at email id: {row.get('id')}, subject: {row.get('subject')}")
            continue

        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            chunks_mapping["chunk_id"].append(str(uuid.uuid4()))
            chunks_mapping["email_id"].append(row["id"])
            chunks_mapping["from"].append(row["from"])
            chunks_mapping["date"].append(row["date"])
            # chunks_mapping["email_label"].append(row["label"])
            chunks_mapping["email_subject"].append(row["subject"])
            chunks_mapping["chunk_text"].append(chunk)

    df = pd.DataFrame(chunks_mapping)
    df.to_csv(f"{data_processed_dir}/chunks.csv", index=False)

    print("Finished chunking!")


if __name__ == '__main__':
    create_chunks()
