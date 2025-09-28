from datetime import datetime
from typing import Any

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.src.model.connection import get_chroma_collection
from app.src.model.utils import sha256_of_json


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
            extra_info={"raw_json": data_profile},
        )

        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        VectorStoreIndex.from_documents(
            documents=[doc],
            storage_context=storage_context,
        )

        print(f"[upserted] profile_id={doc_id}")
        return doc_id

    def parse_profile_object(self, data_profile: dict[str, Any]):
        """Parse the JSON into a structured dictionary.

        Args:
            - data_profile (dict[str, Any]): The raw data profile JSON
        Returns:
            - profile_id, snapshot_id, use_case_id, profile_type, created_at, updated_at
            - high-signal numeric fields used for metadata and summary
        """
        profile_id = data_profile.get("profileId")
        snapshot_id = data_profile.get("snapshotId")
        use_case_id = data_profile.get("useCaseId")
        profile_type = data_profile.get("profileType")
        created_at = data_profile.get("createdAt")
        updated_at = data_profile.get("updatedAt")

        data = data_profile.get("data", {})
        dq = data.get("data_quality", {})
        trend = data.get("trend", {})

        tts_cov = dq.get("target_time_series", {}).get("coverage", {})
        cov_checks = tts_cov.get("checks", [])
        history = self._get_check(cov_checks, "history_length")
        exposure = self._get_check(cov_checks, "exposure_availability")

        resolution = history.get("details", {}).get("resolution") if history else None
        min_hist = (
            history.get("details", {}).get("min_history_length") if history else None
        )
        max_hist = (
            history.get("details", {}).get("max_history_length") if history else None
        )
        avg_hist = (
            history.get("details", {}).get("avg_history_length") if history else None
        )
        items_analyzed = (
            history.get("details", {}).get("items_analyzed") if history else None
        )

        default_exposure_rate = (
            exposure.get("details", {}).get("default_exposure_rate")
            if exposure
            else None
        )

        exposure_variance = (
            exposure.get("details", {}).get("overall_exposure_variance")
            if exposure
            else None
        )

        # Target time series → plausibility (zeros)

        tgt_pl = dq.get("target_time_series", {}).get("plausibility", {}) or {}
        pl_checks = tgt_pl.get("checks", []) or []
        zeros = self._get_check(pl_checks, "zero_target_values")
        overall_zero_ratio = (
            zeros.get("details", {}).get("overall_zero_ratio") if zeros else None
        )
        high_zero_count = None
        if zeros and zeros.get("findings"):
            f0 = zeros["findings"][0]
            high_zero_count = f0.get("affected_count")

        # Trend metrics
        stat = (
            data.get("data", {}).get("trend", {}).get("statistical_metrics", {}) or {}
        )
        r2_mean = stat.get("r_squared", {}).get("mean")
        strong_trends_count = stat.get("r_squared", {}).get("strong_trends_count")
        item_dist = trend.get("item_distribution", {}) or {}
        upward = item_dist.get("upward_trend")
        downward = item_dist.get("downward_trend")
        no_trend = item_dist.get("no_trend")
        total_items = item_dist.get("total_items")

        return {
            "profile_id": profile_id,
            "snapshot_id": snapshot_id,
            "use_case_id": use_case_id,
            "profile_type": profile_type,
            "created_at": created_at,
            "updated_at": updated_at,
            "resolution": resolution,
            "min_history_length": min_hist,
            "max_history_length": max_hist,
            "avg_history_length": avg_hist,
            "items_analyzed": items_analyzed,
            "default_exposure_rate": default_exposure_rate,
            "exposure_variance": exposure_variance,
            "overall_zero_ratio": overall_zero_ratio,
            "high_zero_items_count": high_zero_count,
            "trend_r2_mean": r2_mean,
            "strong_trends_count": strong_trends_count,
            "upward_items": upward,
            "downward_items": downward,
            "no_trend_items": no_trend,
            "total_items": total_items,
        }

    def _get_check(
        self, checks: dict[str, Any], attribute_to_check: str
    ) -> dict | None:
        for c in checks:
            if c.get("check") == attribute_to_check:
                return c
        return None

    def build_semantic_summary(self, fields: dict[str, Any]) -> str:
        return (
            f"Profile {fields['profile_id']} (type={fields['profile_type']}) "
            f"snapshot={fields['snapshot_id']} use_case={fields['use_case_id']}. "
            f"{fields['total_items']} items at {fields['resolution']} with "
            f"history_min/max/avg={fields['min_history_length']}/{fields['max_history_length']}/{fields['avg_history_length']}. "
            f"Zero ratio={fields['overall_zero_ratio']}; high-zero items={fields['high_zero_items_count']}. "
            f"Exposure default rate={fields['default_exposure_rate']} variance={fields['exposure_variance']}. "
            f"Trend: R2_mean={fields['trend_r2_mean']}, strong_trends={fields['strong_trends_count']}, "
            f"counts(up={fields['upward_items']}, down={fields['downward_items']}, none={fields['no_trend_items']}). "
            f"Timestamps created={fields['created_at']} updated={fields['updated_at']}."
        )


if __name__ == "__main__":
    ...
