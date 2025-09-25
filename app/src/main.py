import os

from fastapi import FastAPI, HTTPException
import dotenv
import chromadb
from chromadb.config import Settings


dotenv.load_dotenv()

app = FastAPI(title="Rag App")

CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT"))
COLLECTION_NAME = "demo"


client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(allow_reset=True)
)



@app.get("/health")
def health():
    try:
        client.heartbeat()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/init")
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
        metadatas=[{"src": "chroma"}, {"src": "llamaindex"}, {"src": "rag"}]
    )

    return {"ok": True}


@app.get("/search")
def search(q: str, n: int=3):
    col = client.get_or_create_collection(COLLECTION_NAME)
    res = col.query(query_texts=[q], n_results=n)

    return res