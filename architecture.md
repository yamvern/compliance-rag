# ComplianceRAG Architecture

## 1. System Overview

ComplianceRAG is a Retrieval-Augmented Generation system designed to support
cybersecurity governance, risk, and compliance readiness assessment.

The system retrieves evidence from organizational cybersecurity documents
and maps that evidence to framework-related questions and requirements.

The current capstone implementation uses a synthetic company dataset of
20 cybersecurity policies and procedures, together with NIST CSF 2.0
as the framework source.

---

## 2. Ingestion Pipeline

The ingestion pipeline performs the following steps:

1. Load company TXT documents.
2. Load framework PDF documents.
3. Extract text and metadata.
4. Split documents into overlapping chunks.
5. Generate embeddings.
6. Store vectors and metadata in ChromaDB.

Metadata currently includes:

- source filename
- file type
- page number when available
- chunk index
- chunk word count

Preserving metadata is important because later stages need source traceability
and citations.

---

## 3. Chunking Strategy

### Selected Strategy

Fixed-size word-based chunking with overlap.

Current configuration:

- Chunk size: 180 words
- Chunk overlap: 40 words

### Why This Strategy Was Selected

This strategy was selected as the initial baseline because:

1. The company policies are relatively short and structurally simple.
2. It is deterministic and easy to evaluate.
3. Overlap reduces the risk of losing information located at chunk boundaries.
4. It provides a clear baseline that can later be compared with recursive or
   semantic chunking using Recall@5.

### Trade-offs

Advantages:

- Simple to implement.
- Fast.
- Reproducible.
- Low computational cost.

Limitations:

- May split logical sections.
- Does not understand document semantics.
- May separate headings from related content.

The strategy will be evaluated using the golden-question dataset rather than
being assumed to be optimal.

---

## 4. Embedding Model

### Selected Model

sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

### Why It Was Selected

The project is intended to support cybersecurity content that may contain
both English and Arabic.

The model was selected because:

1. It supports multiple languages.
2. It can run locally without per-request API cost.
3. It is lightweight enough for a capstone prototype.
4. It enables semantic search rather than exact keyword matching only.
5. It provides a useful baseline that can later be compared with hosted
   multilingual embedding APIs.

### Trade-offs

Advantages:

- No embedding API cost.
- Local processing.
- Multilingual support.
- Suitable for experimentation.

Limitations:

- May perform worse than larger commercial embedding models.
- Requires local compute.
- Must be evaluated on the project's own data using Recall@5.

---

## 5. Vector Database

### Selected Database

ChromaDB

### Why ChromaDB Was Selected

ChromaDB was selected because:

1. The capstone dataset is small.
2. It provides persistent local storage.
3. It integrates easily with Python.
4. It supports cosine similarity search.
5. It allows document text and metadata to be stored together with vectors.
6. It requires no separate database server.

### Why Other Options Were Not Selected

Pinecone was not required because the project does not need large-scale
managed infrastructure.

Qdrant and Weaviate provide stronger production features but introduce more
deployment complexity than necessary for the capstone.

pgvector is a strong option for production applications already using
PostgreSQL, but this prototype does not currently require relational joins.

---

## 6. Retrieval Architecture

The retrieval system uses hybrid search.

### Semantic Retrieval

Semantic retrieval uses vector similarity search through ChromaDB.

This is useful when the user's wording differs from the wording in company
policies.

### Keyword Retrieval

BM25 is used for lexical retrieval.

This is useful for cybersecurity terminology and exact identifiers such as:

- MFA
- SIEM
- control identifiers
- product or technology names
- specific security terms

### Hybrid Fusion

Vector and BM25 rankings are combined using Reciprocal Rank Fusion (RRF).

RRF is used instead of directly adding scores because vector similarity scores
and BM25 scores are not on the same numerical scale.

---

## 7. Reranking

A CrossEncoder reranker is applied after hybrid retrieval.

Current model:

cross-encoder/ms-marco-MiniLM-L-6-v2

The initial retrievers are optimized to find candidate evidence.

The reranker evaluates the query and candidate document together, allowing a
more precise final ordering before the best evidence is passed to the
generation or assessment stage.

---

## 8. Current Retrieval Flow

User Query
    ↓
Vector Search
    +
BM25 Search
    ↓
Reciprocal Rank Fusion
    ↓
Candidate Chunks
    ↓
CrossEncoder Reranking
    ↓
Top Evidence Chunks

---

## 9. Evaluation Plan

Retrieval quality will be evaluated using 30 golden questions.

For each question, the expected evidence source or chunk will be identified
manually.

Primary metric:

Recall@5

The target required by the capstone is:

Recall@5 > 80%

The system will first establish a baseline and then improve retrieval if the
target is not achieved.

Possible improvement areas include:

- chunk size
- chunk overlap
- embedding model
- BM25 tokenization
- hybrid fusion
- reranking
- document metadata

---

## 10. Dataset

The company dataset currently contains 20 synthetic cybersecurity policies
and procedures created for controlled evaluation.

Synthetic documents are used because the project requires known evidence and
known documentation gaps for repeatable testing.

NIST Cybersecurity Framework 2.0 is used as the initial framework source.

---

## 11. Architectural Principle

ComplianceRAG does not treat an LLM as the source of truth.

The core principle is:

Framework Requirement
    +
Retrieved Company Evidence
    ↓
Evidence-Based Assessment

The system must not claim formal certification.

Its purpose is to support readiness assessment, evidence discovery, and
documentation gap analysis for human review.