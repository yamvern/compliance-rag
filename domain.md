# ComplianceRAG

## Domain

Cybersecurity Governance, Risk, and Compliance (GRC)

## Problem

Organizations maintain cybersecurity policies, procedures, and governance documents. Mapping these documents manually to cybersecurity framework requirements is time-consuming and difficult to maintain.

ComplianceRAG uses Retrieval-Augmented Generation (RAG) to retrieve relevant evidence from organizational documents and map that evidence to cybersecurity framework requirements.

## Initial Framework

NIST Cybersecurity Framework (CSF) 2.0

## Target Users

- GRC Analysts
- Cybersecurity Consultants
- Information Security Officers
- Internal Auditors
- Small and Medium Organizations

## Core Use Case

For each cybersecurity framework requirement, the application searches the organization's uploaded documents for relevant supporting evidence.

The application then produces an evidence-based assessment.

## Assessment States

- SUPPORTED
- PARTIAL
- NO_EVIDENCE
- NEEDS_REVIEW

## Main Outputs

- Evidence coverage dashboard
- Control-to-evidence mapping
- Evidence citations
- Documentation gap analysis
- Suggested remediation
- Compliance question-answering assistant

## Important Limitation

ComplianceRAG does not certify an organization as compliant.

It provides an evidence-based readiness and documentation-gap assessment designed to assist a human GRC or security reviewer.

## Capstone Scope

The capstone version will:

1. Use 20-50 high-quality cybersecurity-related documents.
2. Implement a document ingestion pipeline.
3. Document the chunking strategy.
4. Document the embedding model selection.
5. Document the vector database selection.
6. Implement hybrid retrieval.
7. Implement reranking.
8. Build a 30-question golden dataset.
9. Measure Recall@5.
10. Reach at least 80% Recall@5.
11. Provide a Streamlit user interface.
12. Add basic authentication.
13. Be tested by three users.
14. Run RAGAS evaluation.
15. Include a cost analysis.
16. Include an Architecture Decision Record.
17. Provide a public repository and live demo.