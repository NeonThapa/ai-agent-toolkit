import json
import numpy as np
import faiss
from google.cloud import storage

# --- CONFIGURATION ---
BUCKET_NAME = "rag-source-documents"
# The full path to the file inside your GCS bucket
VECTOR_FILE_IN_BUCKET = "vector-search-inputs/vector_search_input.json" 
INDEX_OUTPUT_FILE = "local_app_index.faiss"    # The name for our local index

def build_index_from_gcs():
    """Reads vectors directly from GCS and builds a local FAISS index."""
    try:
        # Initialize the GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(VECTOR_FILE_IN_BUCKET)

        print(f"Downloading {VECTOR_FILE_IN_BUCKET} from GCS bucket {BUCKET_NAME}...")
        # Download the file content as a string
        file_content = blob.download_as_string()
        
        # Decode the byte string and split into individual lines
        lines = file_content.decode('utf-8').splitlines()
        vectors_data = [json.loads(line) for line in lines]
        print("File downloaded and parsed successfully.")

    except Exception as e:
        print(f"❌ ERROR: Failed to download or parse file from GCS. Error: {e}")
        print("Please ensure the bucket name and file path are correct and you have the right permissions.")
        return

    if not vectors_data:
        print("❌ ERROR: No vectors found in the input file.")
        return

    # --- (The rest of the script is the same as before) ---
    
    # Extract embeddings and convert to a NumPy array
    dimension = 768 # Assumes your embedding model's dimension
    embeddings = np.array([item['embedding'] for item in vectors_data]).astype('float32')
    
    print(f"Found {len(embeddings)} vectors with dimension {dimension}.")

    # Build the FAISS index
    print("Building FAISS index...")
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save the index to a file
    print(f"Saving index to {INDEX_OUTPUT_FILE}...")
    faiss.write_index(index, INDEX_OUTPUT_FILE)
    
    print("\n✅ Success! Your local FAISS index has been created directly from GCS data.")

if __name__ == "__main__":
    # Ensure you have the necessary libraries installed:
    # pip install faiss-cpu numpy google-cloud-storage
    build_index_from_gcs()