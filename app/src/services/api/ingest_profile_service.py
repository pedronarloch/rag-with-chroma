from datetime import datetime
from typing import Any

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from model.connection import get_chroma_collection
from model.utils import sha256_of_json


class ProfileIngestService:

    def __init__(self):
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

    def upsert_profile_obj(self, data_profile: dict[str, Any]) -> str:
        collection = get_chroma_collection()
        content_hash = sha256_of_json(data_profile)
        fields = self.parse_profile_object(data_profile)

        doc_id = fields["profile_id"]
        summary = self.build_semantic_summary(fields)

        metadata = {
            **fields,
            "content_sha256": content_hash,
            "embedding_version": "v1",
            "source": "pooled_profiles",
            "ingested_at": datetime.now().isoformat() + "Z",
        }

        existing = collection.get(ids=[doc_id])

        if existing and existing.get("ids"):
            meta0 = (existing.get("metadatas") or [{}])[0] or {}
            if meta0.get("content_sha256") == content_hash:
                print(f"[skip] unchanged profile_id={doc_id}")
                return doc_id
            else:
                print(f"[update] content changed for profile_id={doc_id}; re-embedding")

        doc = Document(
            text=summary,
            metadata=metadata,
            doc_id=doc_id,
        )

        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        VectorStoreIndex.from_documents(
            documents=[doc],
            storage_context=storage_context,
        )

        print(f"[upserted] profile_id={doc_id}")
        return doc_id
