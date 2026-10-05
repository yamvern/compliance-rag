from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from ingestion.document_loader import load_directory
from ingestion.chunker import chunk_documents

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DB_PATH = "chroma_db"

COMPANY_COLLECTION = "company_documents"
FRAMEWORK_COLLECTION = "framework_documents"


def get_embedding_model():
    print(f"Loading embedding model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)


def get_chroma_client():
    return chromadb.PersistentClient(path=DB_PATH)


def reset_collection(client, collection_name):
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    return client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def prepare_metadata(metadata: dict) -> dict:
    """
    Chroma metadata values must be simple scalar values.
    """
    clean_metadata = {}

    for key, value in metadata.items():
        if value is None:
            continue

        if isinstance(value, (str, int, float, bool)):
            clean_metadata[key] = value
        else:
            clean_metadata[key] = str(value)

    return clean_metadata


def index_documents(
    documents: list[dict],
    collection,
    model,
    prefix: str,
):
    texts = [document["text"] for document in documents]

    print(f"Creating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    ids = []
    metadatas = []

    for index, document in enumerate(documents):
        ids.append(f"{prefix}_{index}")

        metadata = prepare_metadata(document["metadata"])
        metadata["document_id"] = ids[-1]

        metadatas.append(metadata)

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Stored {len(ids)} chunks in collection: {collection.name}")


def main():
    model = get_embedding_model()
    client = get_chroma_client()

    print("\nPreparing company documents...")

    company_documents = load_directory("data/company_docs")
    company_chunks = chunk_documents(company_documents)

    company_collection = reset_collection(
        client,
        COMPANY_COLLECTION,
    )

    index_documents(
        company_chunks,
        company_collection,
        model,
        prefix="company",
    )

    print("\nPreparing framework documents...")

    framework_documents = load_directory("data/frameworks")
    framework_chunks = chunk_documents(framework_documents)

    framework_collection = reset_collection(
        client,
        FRAMEWORK_COLLECTION,
    )

    index_documents(
        framework_chunks,
        framework_collection,
        model,
        prefix="framework",
    )

    print("\nIndexing complete.")

    print(
        "Company chunks:",
        company_collection.count(),
    )

    print(
        "Framework chunks:",
        framework_collection.count(),
    )


if __name__ == "__main__":
    main()