from pathlib import Path
from pypdf import PdfReader


def load_txt(file_path: Path) -> dict:
    """Load a TXT file and return its text with metadata."""
    text = file_path.read_text(encoding="utf-8")

    return {
        "text": text,
        "metadata": {
            "source": file_path.name,
            "file_type": "txt",
            "path": str(file_path),
        },
    }


def load_pdf(file_path: Path) -> list[dict]:
    """Load a PDF file page by page."""
    reader = PdfReader(str(file_path))
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        documents.append(
            {
                "text": text,
                "metadata": {
                    "source": file_path.name,
                    "file_type": "pdf",
                    "page": page_number,
                    "path": str(file_path),
                },
            }
        )

    return documents


def load_directory(directory_path: str) -> list[dict]:
    """Load supported documents from a directory."""
    directory = Path(directory_path)
    documents = []

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() == ".txt":
            document = load_txt(file_path)

            # Ignore empty TXT files
            if document["text"].strip():
                documents.append(document)

        elif file_path.suffix.lower() == ".pdf":
            documents.extend(load_pdf(file_path))

    return documents


if __name__ == "__main__":
    print("Loading company documents...")

    company_documents = load_directory("data/company_docs")

    print(f"Loaded company documents: {len(company_documents)}")

    for document in company_documents:
        print(
            document["metadata"]["source"],
            "-",
            len(document["text"]),
            "characters",
        )

    print("\nLoading framework documents...")

    framework_documents = load_directory("data/frameworks")

    print(f"Loaded framework pages: {len(framework_documents)}")

    for document in framework_documents[:5]:
        print(
            document["metadata"]["source"],
            "- Page:",
            document["metadata"].get("page"),
            "-",
            len(document["text"]),
            "characters",
        )