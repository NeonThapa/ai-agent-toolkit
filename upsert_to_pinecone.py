import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone
from google.cloud import storage

# --- CONFIGURATION ---
load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "tata-strive-rag"

BUCKET_NAME = "rag-source-documents"
VECTOR_FILE = "vector-search-inputs/vector_search_input.json"
METADATA_FILE = "vector-search-inputs/metadata_lookup.json"

def upsert_data():
    if not PINECONE_API_KEY:
        print("ERROR: PINECONE_API_KEY not found in .env file.")
        print("Please make sure you've added your Pinecone API key to the .env file.")
        return
        
    print("Initializing Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    print("✅ Pinecone initialized.")

    print("Loading data from Google Cloud Storage...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    # Load vectors
    blob_vectors = bucket.blob(VECTOR_FILE)
    vector_lines = blob_vectors.download_as_string().decode('utf-8').splitlines()
    vectors = {}
    for line in vector_lines:
        data = json.loads(line)
        vectors[data['id']] = data['embedding']
    print(f"✅ Loaded {len(vectors)} vectors from GCS.")

    # Load metadata
    blob_metadata = bucket.blob(METADATA_FILE)
    metadata = json.loads(blob_metadata.download_as_string())
    print(f"✅ Loaded metadata for {len(metadata)} chunks from GCS.")

    print("Preparing data for upsert...")
    vectors_to_upsert = []
    batch_size = 100

    for chunk_id, embedding in vectors.items():
        if chunk_id in metadata:
            meta = {
                "text": metadata[chunk_id].get('content', ''),
                "title": metadata[chunk_id].get('title', 'Unknown')
            }
            vectors_to_upsert.append({
                "id": chunk_id, 
                "values": embedding, 
                "metadata": meta
            })

    print(f"Upserting {len(vectors_to_upsert)} vectors in batches of {batch_size}...")
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i+batch_size]
        index.upsert(vectors=batch)
        print(f"✅ Upserted batch {i//batch_size + 1} of {(len(vectors_to_upsert)-1)//batch_size + 1}")

    print("\n🎉 Success! Data has been upserted to your Pinecone index.")
    stats = index.describe_index_stats()
    print(f"📊 Index stats: {stats}")

if __name__ == "__main__":
    upsert_data()