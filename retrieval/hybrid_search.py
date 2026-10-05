from retrieval.vector_search import (
    search_collection,
    COMPANY_COLLECTION,
)

from retrieval.bm25_search import search_bm25

from ingestion.document_loader import load_directory
from ingestion.chunker import chunk_documents


RRF_K = 60

# Evaluation showed semantic retrieval performs better
# on the current compliance dataset.
VECTOR_WEIGHT = 0.70
BM25_WEIGHT = 0.30


def chunk_key(result: dict) -> str:
    metadata = result["metadata"]

    return (
        f"{metadata.get('source')}"
        f"::{metadata.get('page', '')}"
        f"::{metadata.get('chunk_index')}"
    )


def apply_source_diversity(
    results: list[dict],
    top_k: int,
    max_chunks_per_source: int = 2,
) -> list[dict]:
    """
    Prevent one document from occupying too many
    positions in the final retrieval results.
    """

    selected = []
    source_counts = {}

    for result in results:
        source = result["metadata"].get("source")

        current_count = source_counts.get(source, 0)

        if current_count >= max_chunks_per_source:
            continue

        selected.append(result)

        source_counts[source] = current_count + 1

        if len(selected) >= top_k:
            break

    return selected


def hybrid_search(
    query: str,
    top_k: int = 5,
    candidate_k: int = 10,
    max_chunks_per_source: int | None = 2,
):
    # -------------------------------------------------
    # 1. Semantic vector retrieval
    # -------------------------------------------------

    vector_results = search_collection(
        COMPANY_COLLECTION,
        query,
        top_k=candidate_k,
    )

    # -------------------------------------------------
    # 2. BM25 lexical retrieval
    # -------------------------------------------------

    company_documents = load_directory("data/company_docs")
    company_chunks = chunk_documents(company_documents)

    bm25_results = search_bm25(
        query,
        company_chunks,
        top_k=candidate_k,
    )

    # -------------------------------------------------
    # 3. Weighted Reciprocal Rank Fusion
    # -------------------------------------------------

    fused = {}

    for result in vector_results:
        key = chunk_key(result)

        if key not in fused:
            fused[key] = {
                "text": result["text"],
                "metadata": result["metadata"],
                "rrf_score": 0.0,
                "vector_rank": None,
                "bm25_rank": None,
                "vector_similarity": None,
                "bm25_score": None,
            }

        fused[key]["vector_rank"] = result["rank"]

        fused[key]["vector_similarity"] = result.get(
            "similarity"
        )

        fused[key]["rrf_score"] += (
            VECTOR_WEIGHT
            / (RRF_K + result["rank"])
        )

    for result in bm25_results:
        key = chunk_key(result)

        if key not in fused:
            fused[key] = {
                "text": result["text"],
                "metadata": result["metadata"],
                "rrf_score": 0.0,
                "vector_rank": None,
                "bm25_rank": None,
                "vector_similarity": None,
                "bm25_score": None,
            }

        fused[key]["bm25_rank"] = result["rank"]

        fused[key]["bm25_score"] = result.get(
            "score"
        )

        fused[key]["rrf_score"] += (
            BM25_WEIGHT
            / (RRF_K + result["rank"])
        )

    # -------------------------------------------------
    # 4. Sort candidates by fused score
    # -------------------------------------------------

    ranked_results = sorted(
        fused.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    # -------------------------------------------------
    # 5. Encourage document-source diversity
    # -------------------------------------------------

    if max_chunks_per_source is None:
        return ranked_results[:top_k]

    final_results = apply_source_diversity(
        ranked_results,
        top_k=top_k,
        max_chunks_per_source=max_chunks_per_source,
    )

    return final_results


if __name__ == "__main__":

    query = (
        "An investigator needs to determine who authenticated "
        "to a system and which administrator changed it."
    )

    print("QUERY:")
    print(query)

    print("\nHYBRID RESULTS:\n")

    results = hybrid_search(
        query,
        top_k=5,
        candidate_k=15,
    )

    for rank, result in enumerate(results, start=1):

        print("=" * 80)

        print("Final Rank:", rank)

        print(
            "Source:",
            result["metadata"].get("source"),
        )

        print(
            "Chunk:",
            result["metadata"].get("chunk_index"),
        )

        print(
            "Vector Rank:",
            result["vector_rank"],
        )

        print(
            "BM25 Rank:",
            result["bm25_rank"],
        )

        print(
            "Vector Similarity:",
            result["vector_similarity"],
        )

        print(
            "BM25 Score:",
            result["bm25_score"],
        )

        print(
            "Weighted RRF Score:",
            round(result["rrf_score"], 6),
        )

        print()

        print(result["text"][:500])

        print()