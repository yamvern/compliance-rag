from ingestion.document_loader import load_directory

CHUNK_SIZE = 180
CHUNK_OVERLAP = 40


def split_text_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    chunk_size = maximum number of words per chunk
    overlap = number of words shared between consecutive chunks
    """

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append(chunk_text)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Convert loaded documents into smaller chunks
    while preserving source metadata.
    """

    chunked_documents = []

    for document in documents:
        text = document["text"]
        metadata = document["metadata"]

        chunks = split_text_into_chunks(text)

        for chunk_index, chunk_text in enumerate(chunks):
            chunk_metadata = metadata.copy()

            chunk_metadata["chunk_index"] = chunk_index
            chunk_metadata["chunk_word_count"] = len(chunk_text.split())

            chunked_documents.append(
                {
                    "text": chunk_text,
                    "metadata": chunk_metadata,
                }
            )

    return chunked_documents


if __name__ == "__main__":
    print("Loading company documents...")

    company_documents = load_directory("data/company_docs")

    company_chunks = chunk_documents(company_documents)

    print(f"Original company documents: {len(company_documents)}")
    print(f"Company chunks created: {len(company_chunks)}")

    print("\nSample company chunks:")

    for chunk in company_chunks[:5]:
        print("-" * 70)
        print("Source:", chunk["metadata"]["source"])
        print("Chunk:", chunk["metadata"]["chunk_index"])
        print("Words:", chunk["metadata"]["chunk_word_count"])
        print(chunk["text"][:300])

    print("\nLoading framework documents...")

    framework_documents = load_directory("data/frameworks")

    framework_chunks = chunk_documents(framework_documents)

    print(f"Original framework pages: {len(framework_documents)}")
    print(f"Framework chunks created: {len(framework_chunks)}")

    print("\nSample framework chunks:")

    for chunk in framework_chunks[:5]:
        print("-" * 70)
        print("Source:", chunk["metadata"]["source"])
        print("Page:", chunk["metadata"].get("page"))
        print("Chunk:", chunk["metadata"]["chunk_index"])
        print("Words:", chunk["metadata"]["chunk_word_count"])
        print(chunk["text"][:300])