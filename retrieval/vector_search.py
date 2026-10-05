import chromadb
from sentence_transformers import SentenceTransformer
from functools import lru_cache

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DB_PATH = "chroma_db"

COMPANY_COLLECTION = "company_documents"
FRAMEWORK_COLLECTION = "framework_documents"


@lru_cache(maxsize=1)
def load_model():
    print(f"Loading embedding model once: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)

@lru_cache(maxsize=1)
def get_client():
    return chromadb.PersistentClient(path=DB_PATH)

def search_collection(
    collection_name: str,
    query: str,
    top_k: int = 5,
):
    model = load_model()
    client = get_client()

    collection = client.get_collection(collection_name)

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    )[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    output = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):
        similarity = 1 - distance

        output.append(
            {
                "rank": rank,
                "text": document,
                "metadata": metadata,
                "distance": distance,
                "similarity": similarity,
            }
        )

    return output


if __name__ == "__main__":
    query = "How does Acme Corp control user access?"

    print("QUERY:")
    print(query)

    print("\nSearching company documents...\n")

    results = search_collection(
        COMPANY_COLLECTION,
        query,
        top_k=5,
    )

    for result in results:
        print("=" * 80)
        print("Rank:", result["rank"])
        print("Source:", result["metadata"].get("source"))
        print("Chunk:", result["metadata"].get("chunk_index"))
        print("Similarity:", round(result["similarity"], 4))
        print()
        print(result["text"][:500])
        print()