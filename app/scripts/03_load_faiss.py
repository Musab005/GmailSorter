import os
import faiss
import numpy as np
import pandas as pd
import pickle

scripts_dir = os.path.dirname(__file__)
app_dir = os.path.dirname(scripts_dir)
vectorstore_dir = os.path.join(app_dir, 'vectorstore')
FAISS_INDEX_PATH = os.path.join(vectorstore_dir, 'index.faiss')
METADATA_PATH = os.path.join(vectorstore_dir, 'metadata.pkl')

project_root_dir = os.path.dirname(app_dir)
data_processed_dir = os.path.join(project_root_dir, 'data', 'processed')

print("Loading data...")
df_chunks = pd.read_csv(os.path.join(data_processed_dir, 'chunks.csv'))
embeddings = np.load(os.path.join(data_processed_dir, 'email_embeddings.npy'))
embeddings = np.ascontiguousarray(embeddings.astype('float32'))

assert len(df_chunks) == len(embeddings), "Mismatch between chunks and embeddings count."
print(f"Loaded {len(df_chunks)} chunks and embeddings.")

# Normalize vectors for cosine similarity search (which is equivalent to inner product on normalized vectors)
faiss.normalize_L2(embeddings)
d = embeddings.shape[1]
index = faiss.IndexIDMap(faiss.IndexFlatIP(d))
ids = np.arange(len(embeddings), dtype='int64')
index.add_with_ids(embeddings, ids)

print(f"Index created successfully. Total vectors in index: {index.ntotal}")

# metadata mapping
print("Creating metadata mapping...")
required_columns = ['chunk_text', 'email_id', 'date', 'email_subject', 'from']
metadata = df_chunks[required_columns].to_dict('records')
print("Metadata mapping created.")

faiss.write_index(index, FAISS_INDEX_PATH)

with open(METADATA_PATH, 'wb') as f:
    pickle.dump(metadata, f)

print(f"Index saved to: {FAISS_INDEX_PATH}")
print(f"Metadata saved to: {METADATA_PATH}")
print("Setup complete.")

# print("\n--- Verification ---")
# print("Loading index and metadata for a test query...")
#
# index = faiss.read_index(FAISS_INDEX_PATH)
#
# with open(METADATA_PATH, 'rb') as f:
#     loaded_metadata = pickle.load(f)
#
# model = SentenceTransformer('all-MiniLM-L6-v2')
# query_text = "Are there any bills due for Hydro Quebec?"
#
# print(f"\nPerforming test search for: '{query_text}'")
# query_embedding = model.encode([query_text])
#
# k = 3
# distances, indices = index.search(query_embedding.astype('float32'), k)
#
# print(f"Found {len(indices[0])} results:")
# for i, idx in enumerate(indices[0]):
#     meta = loaded_metadata[idx]
#     dist = distances[0][i]
#
#     print(f"\nResult {i + 1} (Distance: {dist:.4f}):")
#     print(f"  Subject: {meta['email_subject']}")
#     print(f"  Email ID: {meta['email_id']}")
#     print(f"  Text: {meta['chunk_text'][:200]}...")
