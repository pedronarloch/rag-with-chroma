import os
import chromadb
from chromadb import Settings as ChromaSettings

def get_chroma_collection():
    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT"), 8000)
    collection_name = os.getenv("CHROMA_COLLECTION", "profiles_v1")
    client = chromadb.HttpClient(host=host, port=port, settings=ChromaSettings(allow_reset=False))

    return client.get_or_create_collection(collection_name, metadata={"hnsw:space": "cosine"})