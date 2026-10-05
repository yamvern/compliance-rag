# Architecture Decision Record (ADR)

## ComplianceRAG — Architecture Decisions

**Status:** Accepted  
**Project:** ComplianceRAG  
**Domain:** Cybersecurity Governance, Risk, and Compliance (GRC)  
**Primary Framework:** NIST Cybersecurity Framework (CSF) 2.0

## Context

ComplianceRAG is a Retrieval-Augmented Generation system designed to map organizational cybersecurity evidence to NIST CSF 2.0 requirements.

The system must retrieve relevant evidence from organizational documents, assess whether the available evidence supports a framework requirement, identify documentation gaps, and provide traceable evidence citations.

The system does not certify an organization as compliant. It provides evidence-based readiness and documentation-gap assessment to support human GRC and security reviewers.

## Decision

ComplianceRAG uses a modular RAG architecture consisting of:

1. Document ingestion and chunking
2. Local multilingual embeddings
3. ChromaDB vector storage
4. Hybrid retrieval using vector search and BM25
5. Reciprocal Rank Fusion (RRF)
6. Cross-Encoder reranking
7. Cohere Command A for evidence assessment
8. Deterministic evidence-coverage scoring
9. Streamlit for the authenticated user interface

## Retrieval Architecture

Organizational documents are divided into overlapping chunks of approximately 180 words with a 40-word overlap.

Chunks are embedded using:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

The model was selected because it can run locally and supports multilingual semantic retrieval.

ChromaDB stores document embeddings and metadata.

Retrieval combines:

- Semantic vector search
- BM25 lexical search

Results are fused using weighted Reciprocal Rank Fusion (RRF), followed by a Cross-Encoder reranker:

`cross-encoder/ms-marco-MiniLM-L-6-v2`

This design supports both semantic matches and exact cybersecurity terminology.

## Framework Source

NIST Cybersecurity Framework 2.0 is the authoritative framework source.

The official NIST CSF 2.0 catalog is parsed into active Functions, Categories, and Subcategories.

The system currently contains:

- 6 Functions
- 106 active Subcategories

Implementation examples are treated as contextual guidance and are not interpreted as independently mandatory requirements.

## Evidence Assessment

For each NIST requirement, the system retrieves the most relevant organizational evidence and sends only that evidence to Cohere Command A.

The model must return one of four assessment states:

- SUPPORTED
- PARTIAL
- NO_EVIDENCE
- NEEDS_REVIEW

The assessment also contains:

- Reason
- Documentation gap
- Recommendation
- Evidence sources

The LLM is instructed not to assume evidence that was not retrieved and not to claim compliance certification.

## Scoring Decision

The LLM does not calculate the final readiness percentage.

A deterministic scoring engine assigns:

- SUPPORTED = 1.0
- PARTIAL = 0.5
- NO_EVIDENCE = 0.0
- NEEDS_REVIEW = excluded from the denominator

The resulting metric is called **Evidence Coverage**, not a compliance score.

This separates evidence interpretation from numerical scoring and makes the final calculation reproducible.

## Evaluation

Retrieval is evaluated independently from generation.

A 30-question Golden Question evaluation achieved Recall@5 above the required 80% threshold.

A harder paraphrase and scenario-based evaluation also remained above the required threshold.

Generation quality was evaluated using RAGAS on 20 questions.

Results:

- Faithfulness: 0.8933
- Answer Relevancy: 0.7519
- Context Precision: 0.9533
- Context Recall: 1.0000
- Mean of selected RAGAS metrics: 0.8996

These results indicate strong retrieval performance and evidence grounding, while answer relevancy remains an area for future improvement.

## Consequences

### Benefits

- Evidence is traceable to source documents.
- Hybrid retrieval handles semantic and lexical matches.
- Reranking improves final evidence selection.
- Local embeddings reduce external API dependency.
- Deterministic scoring improves reproducibility.
- The architecture supports framework-level gap analysis.
- Components can be evaluated independently.

### Trade-offs

- Cross-Encoder reranking adds latency.
- LLM-based assessment introduces API cost.
- Full-framework assessments require many model calls.
- ChromaDB persistence and uploaded documents require additional production storage planning.
- Evidence quality depends on the quality and completeness of organizational documents.

## Final Decision

The selected architecture prioritizes evidence traceability, retrieval quality, reproducible scoring, and human review over automated compliance certification.

ComplianceRAG should therefore be treated as a cybersecurity evidence and readiness-assessment platform rather than an automated compliance authority.