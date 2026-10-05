import json

from retrieval.vector_search import (
    search_collection,
    COMPANY_COLLECTION,
)

from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank


GOLDEN_FILE = "evaluation/golden_questions.json"


def load_golden():
    with open(GOLDEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_vector_only(golden):
    hits = 0

    for item in golden:
        results = search_collection(
            COMPANY_COLLECTION,
            item["question"],
            top_k=5,
        )

        sources = [
            result["metadata"].get("source")
            for result in results
        ]

        if item["expected_source"] in sources:
            hits += 1

    return hits / len(golden)


def evaluate_hybrid(golden):
    hits = 0

    for item in golden:
        results = hybrid_search(
            item["question"],
            top_k=5,
            candidate_k=10,
        )

        sources = [
            result["metadata"].get("source")
            for result in results
        ]

        if item["expected_source"] in sources:
            hits += 1

    return hits / len(golden)


def evaluate_hybrid_rerank(golden):
    hits = 0

    for index, item in enumerate(golden, start=1):
        print(f"Reranking question {index}/{len(golden)}")

        candidates = hybrid_search(
            item["question"],
            top_k=10,
            candidate_k=10,
        )

        results = rerank(
            item["question"],
            candidates,
            top_k=5,
        )

        sources = [
            result["metadata"].get("source")
            for result in results
        ]

        if item["expected_source"] in sources:
            hits += 1

    return hits / len(golden)


def main():
    golden = load_golden()

    print("\nEvaluating Vector Search...")
    vector_recall = evaluate_vector_only(golden)

    print("\nEvaluating Hybrid Search...")
    hybrid_recall = evaluate_hybrid(golden)

    print("\nEvaluating Hybrid + Reranker...")
    rerank_recall = evaluate_hybrid_rerank(golden)

    print("\n" + "=" * 60)
    print("RETRIEVAL COMPARISON")
    print("=" * 60)

    print(f"Vector Only:         {vector_recall:.2%}")
    print(f"Hybrid Search:       {hybrid_recall:.2%}")
    print(f"Hybrid + Reranker:   {rerank_recall:.2%}")

    print("=" * 60)


if __name__ == "__main__":
    main()