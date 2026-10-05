import json

from retrieval.vector_search import (
    search_collection,
    COMPANY_COLLECTION,
)

from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank


GOLDEN_FILE = "evaluation/golden_questions_hard.json"


def load_golden():
    with open(GOLDEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def source_list(results):
    return [
        result["metadata"].get("source")
        for result in results
    ]


def is_hit(expected_sources, retrieved_sources):
    return any(
        source in retrieved_sources
        for source in expected_sources
    )


def print_misses(title, misses):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    if not misses:
        print("\nNo misses.")
        return

    for item in misses:
        print(f"\nQ{item['id']:02d}: {item['question']}")

        print("Expected one of:")
        for source in item["expected_sources"]:
            print("   -", source)

        print("Retrieved:")
        for source in item["retrieved_sources"]:
            print("   -", source)


def main():
    golden = load_golden()

    vector_misses = []
    hybrid_misses = []
    rerank_misses = []

    for item in golden:
        question = item["question"]
        expected_sources = item["expected_sources"]

        # Vector Search
        vector_results = search_collection(
            COMPANY_COLLECTION,
            question,
            top_k=5,
        )

        # Hybrid Search
        hybrid_results = hybrid_search(
            question,
            top_k=5,
            candidate_k=10,
        )

        # Hybrid + Reranker
        candidates = hybrid_search(
            question,
            top_k=10,
            candidate_k=10,
            max_chunks_per_source=None,
        )

        reranked_results = rerank(
            question,
            candidates,
            top_k=5,
        )

        vector_sources = source_list(vector_results)
        hybrid_sources = source_list(hybrid_results)
        rerank_sources = source_list(reranked_results)

        if not is_hit(expected_sources, vector_sources):
            vector_misses.append(
                {
                    "id": item["id"],
                    "question": question,
                    "expected_sources": expected_sources,
                    "retrieved_sources": vector_sources,
                }
            )

        if not is_hit(expected_sources, hybrid_sources):
            hybrid_misses.append(
                {
                    "id": item["id"],
                    "question": question,
                    "expected_sources": expected_sources,
                    "retrieved_sources": hybrid_sources,
                }
            )

        if not is_hit(expected_sources, rerank_sources):
            rerank_misses.append(
                {
                    "id": item["id"],
                    "question": question,
                    "expected_sources": expected_sources,
                    "retrieved_sources": rerank_sources,
                }
            )

    print_misses("VECTOR MISSES", vector_misses)
    print_misses("HYBRID MISSES", hybrid_misses)
    print_misses("RERANKER MISSES", rerank_misses)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total = len(golden)

    vector_recall = (total - len(vector_misses)) / total
    hybrid_recall = (total - len(hybrid_misses)) / total
    rerank_recall = (total - len(rerank_misses)) / total

    print("Vector misses:", len(vector_misses))
    print("Hybrid misses:", len(hybrid_misses))
    print("Reranker misses:", len(rerank_misses))

    print()
    print(f"Vector Recall@5: {vector_recall:.2%}")
    print(f"Hybrid Recall@5: {hybrid_recall:.2%}")
    print(f"Hybrid + Reranker Recall@5: {rerank_recall:.2%}")


if __name__ == "__main__":
    main()