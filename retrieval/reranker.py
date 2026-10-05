from sentence_transformers import CrossEncoder

from retrieval.hybrid_search import hybrid_search
from functools import lru_cache

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def load_reranker():
    print(f"Loading reranker once: {RERANKER_MODEL}")
    return CrossEncoder(RERANKER_MODEL)


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """
    Rerank candidate chunks using a CrossEncoder.
    """

    model = load_reranker()

    pairs = [
        [query, candidate["text"]]
        for candidate in candidates
    ]

    scores = model.predict(pairs)

    reranked = []

    for candidate, score in zip(candidates, scores):
        result = candidate.copy()
        result["reranker_score"] = float(score)

        reranked.append(result)

    reranked.sort(
        key=lambda item: item["reranker_score"],
        reverse=True,
    )

    return reranked[:top_k]


if __name__ == "__main__":

    query = "multi-factor authentication remote administrative access"

    print("QUERY:")
    print(query)

    print("\nGetting hybrid candidates...\n")

    candidates = hybrid_search(
        item["question"],
        top_k=20,
        candidate_k=20,
        max_chunks_per_source=None,
    )

    print("\nRERANKING...\n")

    results = rerank(
        query,
        candidates,
        top_k=3,
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
            "Reranker Score:",
            round(result["reranker_score"], 4),
        )

        print(
            "Previous RRF Score:",
            round(result["rrf_score"], 6),
        )

        print()

        print(result["text"][:500])

        print()