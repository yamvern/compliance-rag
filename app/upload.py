from pathlib import Path

import streamlit as st
import chromadb

from ingestion.document_loader import load_directory
from ingestion.chunker import chunk_documents
from ingestion.embedder import (
    get_embedding_model,
    prepare_metadata,
    DB_PATH,
    COMPANY_COLLECTION,
)


UPLOAD_DIR = Path("data/company_docs/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_files(uploaded_files):
    saved_files = []

    for uploaded_file in uploaded_files:
        destination = UPLOAD_DIR / uploaded_file.name

        with open(destination, "wb") as f:
            f.write(uploaded_file.getbuffer())

        saved_files.append(destination.name)

    return saved_files


def rebuild_company_index():
    """
    Rebuild only the company_documents collection.
    The NIST framework collection is left untouched.
    """

    model = get_embedding_model()

    company_documents = load_directory(
        "data/company_docs"
    )

    company_chunks = chunk_documents(
        company_documents
    )

    if not company_chunks:
        raise ValueError(
            "No readable company documents were found."
        )

    client = chromadb.PersistentClient(
        path=DB_PATH
    )

    try:
        client.delete_collection(
            COMPANY_COLLECTION
        )
    except Exception:
        pass

    collection = client.create_collection(
        name=COMPANY_COLLECTION,
        metadata={
            "hnsw:space": "cosine"
        },
    )

    texts = [
        document["text"]
        for document in company_chunks
    ]

    embeddings = model.encode(
        texts,
        show_progress_bar=False,
        normalize_embeddings=True,
    )

    ids = []
    metadatas = []

    for index, document in enumerate(
        company_chunks
    ):
        document_id = f"company_{index}"

        metadata = prepare_metadata(
            document["metadata"]
        )

        metadata["document_id"] = (
            document_id
        )

        ids.append(document_id)
        metadatas.append(metadata)

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )

    unique_sources = {
        document["metadata"].get("source")
        for document in company_chunks
    }

    return {
        "documents": len(unique_sources),
        "chunks": len(company_chunks),
        "collection_count": (
            collection.count()
        ),
    }


def render_upload_page():
    st.header(
        "Upload Company Documents"
    )

    st.caption(
        "Upload TXT or PDF cybersecurity "
        "policies and procedures."
    )

    uploaded_files = st.file_uploader(
        "Choose company documents",
        type=[
            "txt",
            "pdf",
        ],
        accept_multiple_files=True,
    )

    if uploaded_files:
        st.subheader(
            "Selected Files"
        )

        for uploaded_file in uploaded_files:
            st.write(
                f"• {uploaded_file.name}"
            )

    col1, col2 = st.columns(2)

    with col1:
        save_clicked = st.button(
            "Save Uploaded Files",
            use_container_width=True,
        )

    with col2:
        index_clicked = st.button(
            "Process & Index Documents",
            use_container_width=True,
            type="primary",
        )

    if save_clicked:
        if not uploaded_files:
            st.warning(
                "Please choose at least "
                "one file first."
            )

        else:
            saved_files = (
                save_uploaded_files(
                    uploaded_files
                )
            )

            st.success(
                f"Saved "
                f"{len(saved_files)} "
                f"file(s)."
            )

            for filename in saved_files:
                st.write(
                    f"✅ {filename}"
                )

    if index_clicked:
        if uploaded_files:
            save_uploaded_files(
                uploaded_files
            )

        with st.spinner(
            "Processing documents "
            "and rebuilding company index..."
        ):
            try:
                result = (
                    rebuild_company_index()
                )

            except Exception as exc:
                st.error(
                    f"Indexing failed: {exc}"
                )

            else:
                st.success(
                    "Company document index "
                    "updated successfully."
                )

                metric1, metric2 = (
                    st.columns(2)
                )

                metric1.metric(
                    "Documents",
                    result[
                        "documents"
                    ],
                )

                metric2.metric(
                    "Chunks Indexed",
                    result[
                        "chunks"
                    ],
                )

                st.info(
                    "The NIST framework "
                    "index was not rebuilt."
                )

    st.divider()

    existing_files = sorted(
        [
            path.name
            for path
            in UPLOAD_DIR.iterdir()
            if path.is_file()
        ]
    )

    st.subheader(
        "Uploaded Documents"
    )

    if not existing_files:
        st.info(
            "No uploaded documents yet."
        )

    else:
        for filename in existing_files:
            st.write(
                f"📄 {filename}"
            )