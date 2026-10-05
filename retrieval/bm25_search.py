import re
from rank_bm25 import BM25Okapi

from ingestion.document_loader import load_directory
from ingestion.chunker import chunk_documents


def tokenize(text: str) -> list[str]:
    """
    Simple tokenizer for BM25.
    Converts text to lowercase and extracts words/numbers.
    """
    return re.findall(r"\b\w+\b", text.lower())


def build_bm25_index(documents: list[dict]):
    tokenized_corpus = [
        tokenize(document["text"])
        for document in documents
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    return bm25


def search_bm25(
    query: str,
    documents: list[dict],
    top_k: int = 5,
) -> list[dict]:

    bm25 = build_bm25_index(documents)

    tokenized_query = tokenize(query)

    scores = bm25.get_scores(tokenized_query)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True,
    )[:top_k]

    results = []

    for rank, index in enumerate(ranked_indices, start=1):
        results.append(
            {
                "rank": rank,
                "score": float(scores[index]),
                "text": documents[index]["text"],
                "metadata": documents[index]["metadata"],
            }
        )

    return results


if __name__ == "__main__":
    print("Loading company documents...")

    company_documents = load_directory("data/company_docs")
    company_chunks = chunk_documents(company_documents)

    query = "multi-factor authentication remote administrative access"

    print("\nQUERY:")
    print(query)

    print("\nBM25 RESULTS:\n")

    results = search_bm25(
        query,
        company_chunks,
        top_k=5,
    )

    for result in results:
        print("=" * 80)
        print("Rank:", result["rank"])
        print("Source:", result["metadata"].get("source"))
        print("Chunk:", result["metadata"].get("chunk_index"))
        print("BM25 Score:", round(result["score"], 4))
        print()
        print(result["text"][:500])
        print()