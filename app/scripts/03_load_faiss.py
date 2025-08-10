import faiss
import numpy as np
import pandas as pd
import pickle
import os

scripts_dir = os.path.dirname(__file__)
app_dir = os.path.dirname(scripts_dir)
vectorstore_dir = app_dir + '/vectorstore'
FAISS_INDEX_PATH = f'{vectorstore_dir}/index.faiss'
METADATA_PATH = f'{vectorstore_dir}/metadata.pkl'
project_root_dir = os.path.dirname(app_dir)
data_raw_dir = os.path.join(project_root_dir, 'data/raw')
data_processed_dir = os.path.join(project_root_dir, 'data/processed')

print("Loading data...")
df_chunks = pd.read_csv(f'{data_processed_dir}/chunks.csv')
embeddings = np.load(f'{data_processed_dir}/email_embeddings.npy')

# Ensure the embeddings are in a C-contiguous array of type float32, which FAISS requires
embeddings = np.ascontiguousarray(embeddings.astype('float32'))

assert len(df_chunks) == len(embeddings), "Mismatch between chunks and embeddings count."
print(f"Loaded {len(df_chunks)} chunks and embeddings.")

print("Creating FAISS index...")

d = embeddings.shape[1]

# brute-force L2 distance search.
index = faiss.IndexFlatL2(d)
index.add(embeddings)

print(f"Index created successfully. Total vectors in index: {index.ntotal}")

# CREATE METADATA MAPPING
# need to store the text and original source info separately, create a list of dictionaries where the index of the list
# corresponds to the ID in the FAISS index.
metadata = df_chunks[['chunk_text', 'email_id', 'email_subject']].to_dict('records')
print("Metadata mapping created.")

print("Saving FAISS index and metadata...")

faiss.write_index(index, FAISS_INDEX_PATH)

with open(METADATA_PATH, 'wb') as f:
    pickle.dump(metadata, f)

print(f"Index saved to: {FAISS_INDEX_PATH}")
print(f"Metadata saved to: {METADATA_PATH}")

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
