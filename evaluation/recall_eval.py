import json

from retrieval.hybrid_search import hybrid_search


GOLDEN_FILE = "evaluation/golden_questions.json"


def evaluate_recall_at_5():
    with open(GOLDEN_FILE, "r", encoding="utf-8") as f:
        golden_questions = json.load(f)

    hits = 0

    print("\nEvaluating Recall@5...\n")

    for item in golden_questions:
        question = item["question"]
        expected_source = item["expected_source"]

        results = hybrid_search(
            question,
            top_k=5,
            candidate_k=10,
        )

        retrieved_sources = [
            result["metadata"].get("source")
            for result in results
        ]

        hit = expected_source in retrieved_sources

        if hit:
            hits += 1

        print(
            f"Q{item['id']:02d} "
            f"{'HIT ' if hit else 'MISS'} | "
            f"Expected: {expected_source}"
        )

        if not hit:
            print("     Retrieved:", retrieved_sources)

    total = len(golden_questions)
    recall = hits / total if total else 0

    print("\n" + "=" * 70)
    print(f"Hits: {hits}/{total}")
    print(f"Recall@5: {recall:.2%}")
    print("=" * 70)

    if recall >= 0.80:
        print("PASS: Recall@5 meets the capstone target.")
    else:
        print("FAIL: Recall@5 is below 80% and needs improvement.")


if __name__ == "__main__":
    evaluate_recall_at_5()