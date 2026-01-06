import os

import chromadb
import dotenv
from chromadb.config import Settings
from fastapi import APIRouter

dotenv.load_dotenv()
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION")


client = chromadb.HttpClient(
    host=CHROMA_HOST, port=CHROMA_PORT, settings=Settings(allow_reset=True)
)

router = APIRouter()


@router.post("/init")
def init():
    if any(c.name == COLLECTION_NAME for c in client.list_collections()):
        client.delete_collection(COLLECTION_NAME)
    col = client.create_collection(COLLECTION_NAME)
    col.add(
        ids=["1", "2", "3"],
        documents=[
            "Chroma is a simple, open-source vector database.",
            "LlamaIndex streamlines RAG pipelines.",
            "RAG retrieves relevant chunks to ground LLM response.",
        ],
        metadatas=[{"src": "chroma"}, {"src": "llamaindex"}, {"src": "rag"}],
    )

    return {"ok": True}
