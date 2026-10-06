# ComplianceRAG

## AI-Powered Cybersecurity Evidence & Gap Assessment Platform

ComplianceRAG is a Retrieval-Augmented Generation (RAG) application for cybersecurity Governance, Risk, and Compliance (GRC).

The system maps organizational cybersecurity policies and procedures to requirements from the **NIST Cybersecurity Framework (CSF) 2.0**, retrieves supporting evidence, identifies documentation gaps, and generates evidence-based readiness assessments.

> **Important:** ComplianceRAG does not certify an organization as compliant. It is an evidence-based readiness and documentation-gap assessment tool designed to assist human GRC, cybersecurity, and audit professionals.

---

## Live Demo

**Live Application:** To be added after deployment.

**GitHub Repository:** To be added after publishing the repository.

---

## Problem

Organizations maintain cybersecurity policies, procedures, standards, and governance documents across many files.

Manually mapping these documents to cybersecurity framework requirements can be:

- Time-consuming
- Difficult to maintain
- Inconsistent
- Hard to audit
- Difficult to trace back to source evidence

ComplianceRAG uses Retrieval-Augmented Generation to help automate evidence discovery and framework mapping while keeping the supporting source documents visible to the reviewer.

---

## Target Users

ComplianceRAG is designed for:

- GRC Analysts
- Cybersecurity Consultants
- Information Security Officers
- Internal Auditors
- Small and Medium Organizations

---

## Framework

The initial framework supported by the project is:

**NIST Cybersecurity Framework (CSF) 2.0**

The official NIST CSF 2.0 catalog is used as the authoritative framework source.

The parsed active catalog contains:

- 6 Functions
- 106 active Subcategories

The six CSF Functions are:

- GOVERN (GV)
- IDENTIFY (ID)
- PROTECT (PR)
- DETECT (DE)
- RESPOND (RS)
- RECOVER (RC)

Implementation examples are used only as contextual guidance and are not treated as independently mandatory requirements.

---

## Core Capabilities

ComplianceRAG provides:

- Organizational document ingestion
- PDF and TXT document loading
- Overlapping document chunking
- Local multilingual embeddings
- ChromaDB vector storage
- Semantic vector retrieval
- BM25 lexical retrieval
- Hybrid Search
- Reciprocal Rank Fusion (RRF)
- Cross-Encoder reranking
- NIST CSF 2.0 requirement mapping
- LLM-based evidence assessment
- Evidence citations
- Documentation gap identification
- Remediation recommendations
- Deterministic Evidence Coverage scoring
- Function-level and Category-level dashboards
- Document upload and re-indexing
- Simple application authentication
- User-testing feedback collection
- Retrieval and RAGAS evaluation

---

## Architecture

ComplianceRAG separates offline indexing from online retrieval and assessment.

### Offline Indexing

```text
Organizational Documents
        |
        v
Document Loading
        |
        v
Text Chunking
        |
        v
Local Embeddings
        |
        v
ChromaDB
```

### Online Assessment

```text
NIST CSF Requirement
        |
        +-------------------+
        |                   |
        v                   v
 Vector Search          BM25 Search
        |                   |
        +---------+---------+
                  |
                  v
        Reciprocal Rank Fusion
                  |
                  v
         Cross-Encoder Reranker
                  |
                  v
          Top Evidence Chunks
                  |
                  v
          Cohere Command A
                  |
                  v
       Evidence Assessment
                  |
                  v
     Deterministic Scoring
                  |
                  v
       Streamlit Dashboard
```

---

## Retrieval Pipeline

### 1. Document Loading

The ingestion pipeline supports:

- `.txt`
- `.pdf`

Source metadata is preserved so retrieved evidence can be traced back to its original document.

### 2. Chunking

Organizational documents are divided into overlapping word-based chunks.

Current configuration:

```text
Chunk size:    180 words
Chunk overlap: 40 words
```

Overlap helps preserve context that may span chunk boundaries.

### 3. Embeddings

The embedding model is:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Embeddings are generated locally.

This reduces dependency on external embedding APIs and provides multilingual semantic representation.

### 4. Vector Database

The project uses:

```text
ChromaDB
```

Separate collections are maintained for organizational documents and framework documents.

### 5. Hybrid Search

Retrieval combines:

- Semantic vector search
- BM25 lexical search

The two rankings are combined using weighted Reciprocal Rank Fusion (RRF).

The current weighting prioritizes semantic retrieval while preserving lexical matching:

```text
Vector weight: 0.70
BM25 weight:   0.30
```

Hybrid retrieval is useful in cybersecurity because queries may contain both semantic concepts and exact technical terminology.

### 6. Reranking

Hybrid candidates are reranked using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The final evidence set is passed to the assessment model.

---

## Evidence Assessment

ComplianceRAG uses:

```text
Cohere Command A
```

Current model configuration:

```text
command-a-03-2025
```

For each NIST CSF requirement, the application retrieves organizational evidence and asks the model to perform an evidence-based assessment.

The model is instructed to use only the supplied evidence and avoid assuming undocumented controls.

---

## Assessment States

Every assessed requirement receives one of four states:

### SUPPORTED

The retrieved evidence adequately supports the requirement.

### PARTIAL

Relevant evidence exists, but important elements of the requirement are missing or insufficiently documented.

### NO_EVIDENCE

No adequate supporting evidence was found in the retrieved organizational documents.

### NEEDS_REVIEW

The evidence cannot be assessed reliably and requires human review.

---

## Evidence Coverage

ComplianceRAG deliberately avoids presenting its output as a compliance certification.

Instead, it calculates an **Evidence Coverage** metric.

The deterministic scoring rules are:

| Assessment State | Score |
|---|---:|
| SUPPORTED | 1.0 |
| PARTIAL | 0.5 |
| NO_EVIDENCE | 0.0 |
| NEEDS_REVIEW | Excluded |

The final score is calculated outside the LLM.

This separates evidence interpretation from numerical scoring and improves reproducibility.

---

## Example Assessment

A result may look like:

```json
{
  "status": "PARTIAL",
  "reason": "Relevant evidence exists but does not fully address the requirement.",
  "gap": "Additional documented controls are required.",
  "recommendation": "Document and implement the missing control requirements.",
  "evidence_sources": [
    {
      "source": "02_access_control_policy.txt",
      "chunk": 1
    }
  ]
}
```

The result is intended to support a human reviewer rather than replace professional judgment.

---

## Dashboard

The Streamlit interface provides:

- Authentication
- Framework information
- Assessment scope selection
- Evidence Coverage
- Assessment-state summaries
- Function-level coverage
- Category-level coverage
- Control filtering
- Status filtering
- Requirement search
- Evidence citations
- Documentation gaps
- Recommendations
- Document upload
- User-testing feedback

Assessments can be run by NIST Function instead of always evaluating all 106 Subcategories, helping reduce unnecessary API usage.

---

## Dataset

The demonstration environment includes 20 synthetic organizational cybersecurity policy and procedure documents.

Examples include:

- Information Security Policy
- Access Control Policy
- Password Policy
- Incident Response Policy
- Risk Management Policy
- Asset Management Policy
- Backup Policy
- Business Continuity Policy
- Vendor Security Policy
- Security Awareness Policy
- Logging and Monitoring Policy
- Vulnerability Management Policy
- Change Management Policy
- Remote Access Policy
- Data Classification Policy
- Encryption Policy
- Mobile Device Policy
- Physical Security Policy
- Secure Development Policy
- Account Management Procedure

These documents form a **controlled synthetic demonstration corpus**.

The corpus intentionally contains both supporting evidence and documentation gaps so that the system can demonstrate SUPPORTED, PARTIAL, and NO_EVIDENCE behavior.

It should not be interpreted as documentation from a real organization.

---

## Retrieval Evaluation

Retrieval performance is evaluated separately from generation quality.

### Baseline Golden Questions

A set of 30 Golden Questions was used to evaluate retrieval.

The baseline evaluation achieved:

```text
Recall@5: 100%
```

This exceeds the capstone requirement of:

```text
Recall@5 > 80%
```

### Hard Retrieval Evaluation

A second 30-question challenge set was created using:

- Paraphrased questions
- Scenario-based questions
- Reasoning questions
- Cross-policy questions

Results:

| Retrieval Method | Recall@5 |
|---|---:|
| Vector Only | 96.67% |
| Hybrid Search | 90.00% |
| Hybrid + Reranker | 93.33% |

An important finding was that vector-only retrieval performed best on the harder paraphrased test set.

Therefore, the project does not claim that Hybrid Search universally outperforms vector retrieval.

Hybrid Search remains part of the production architecture because it combines semantic retrieval with exact lexical matching, while reranking provides a final relevance stage.

---

## RAGAS Evaluation

Generation and context quality were evaluated using **RAGAS** on 20 questions.

All 20 evaluation samples completed successfully.

| Metric | Score |
|---|---:|
| Faithfulness | 0.8933 |
| Answer Relevancy | 0.7519 |
| Context Precision | 0.9533 |
| Context Recall | 1.0000 |
| Mean of Selected Metrics | **0.8996** |

### Interpretation

The evaluation shows:

- Strong grounding of generated answers in retrieved evidence
- Very high context precision
- Complete context recall on the evaluation dataset
- Answer relevancy as the primary area for future improvement

The value `0.8996` is reported as the **mean of the selected RAGAS metrics**, rather than being presented as a universal RAGAS metric.

Detailed results are stored in:

```text
reports/ragas_metrics.json
```

---

## Cost Analysis

A production cost estimate was created for:

- 1,000 users
- 10,000 users
- 100,000 users

The estimate assumes:

```text
10 queries per user per month
2,500 input tokens per query
300 output tokens per query
```

Under the pricing assumptions documented at the time of analysis:

| Users | Monthly Queries | Estimated Monthly LLM Cost |
|---:|---:|---:|
| 1,000 | 10,000 | $92.50 |
| 10,000 | 100,000 | $925.00 |
| 100,000 | 1,000,000 | $9,250.00 |

These estimates cover LLM inference only.

They exclude hosting, persistent storage, bandwidth, monitoring, and other infrastructure costs.

See:

```text
reports/cost_analysis.md
```

for assumptions and limitations.

---

## Project Structure

```text
compliance-rag/
|
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── feedback.py
│   ├── main.py
│   └── upload.py
│
├── assessment/
│   ├── assess_control.py
│   ├── batch_assessment.py
│   ├── evidence_assessor.py
│   ├── nist_requirements.py
│   └── scoring.py
│
├── ingestion/
│   ├── chunker.py
│   ├── document_loader.py
│   ├── embedder.py
│   └── nist_catalog.py
│
├── retrieval/
│   ├── bm25_search.py
│   ├── hybrid_search.py
│   ├── reranker.py
│   └── vector_search.py
│
├── evaluation/
│   ├── compare_retrieval.py
│   ├── golden_questions.json
│   ├── golden_questions_hard.json
│   ├── ragas_eval.py
│   ├── ragas_metrics.py
│   ├── ragas_questions.json
│   └── recall_eval.py
│
├── data/
│   ├── company_docs/
│   └── frameworks/
│
├── reports/
│   ├── batch_assessment.json
│   ├── cost_analysis.md
│   ├── ragas_metrics.json
│   ├── ragas_results.json
│   └── retrieval_evaluation.md
│
├── tests/
├── ADR.md
├── architecture.md
├── domain.md
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd compliance-rag
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a local `.env` file:

```text
COHERE_API_KEY=your_cohere_api_key
APP_USERNAME=your_username
APP_PASSWORD=your_password
```

Do not commit `.env` to Git.

The repository `.gitignore` excludes sensitive environment configuration.

---

## Build the Vector Index

Before starting the application, index the organizational and framework documents using the project's ingestion pipeline.

For the current implementation:

```bash
python -m ingestion.embedder
```

The local ChromaDB directory is not committed to Git and may need to be rebuilt in a new environment.

---

## Run the Application

Start Streamlit with:

```bash
streamlit run app/main.py
```

Then open the URL displayed by Streamlit.

Authenticate using the credentials configured through:

```text
APP_USERNAME
APP_PASSWORD
```

---

## Run a Single NIST Assessment

A single NIST CSF control can be assessed from the command line.

Example:

```bash
python -m assessment.assess_control --control PR.AA-03
```

---

## Run a Function Assessment

Example:

```bash
python -m assessment.batch_assessment --function PR
```

Supported function codes are:

```text
GV
ID
PR
DE
RS
RC
ALL
```

Running the entire framework may require many LLM calls, so Function-level assessment is recommended during development and testing.

---

## Run Retrieval Evaluation

Baseline evaluation:

```bash
python -m evaluation.recall_eval
```

Retrieval comparison:

```bash
python -m evaluation.compare_retrieval
```

---

## RAGAS Evaluation

The project includes a 20-question RAGAS evaluation dataset.

The generated RAG dataset is stored in:

```text
reports/ragas_results.json
```

The final metric results are stored in:

```text
reports/ragas_metrics.json
```

RAGAS evaluation may require external model calls and should not be repeatedly executed unnecessarily.

---

## Authentication

The application includes simple username/password authentication suitable for the capstone demonstration.

Credentials are loaded from environment variables rather than hard-coded into the repository.

This authentication mechanism is not intended to represent a production-grade identity and access management system.

A production implementation should integrate a dedicated identity provider and stronger session management.

---

## User Testing

The application includes a User Testing page for collecting structured feedback.

Feedback includes:

- Usability rating
- Clarity rating
- Evidence usefulness rating
- Most useful feature
- Problems encountered
- Improvement suggestions

The capstone requires testing with three real users.

Real user feedback should be collected before final submission and summarized in the project documentation.

---

## Security and Privacy Considerations

Compliance documents may contain sensitive organizational information.

A production deployment should therefore consider:

- Encryption at rest
- Encryption in transit
- Strong authentication
- Role-based authorization
- Tenant isolation
- Secure secret management
- Audit logging
- Document retention policies
- Secure deletion
- Restricted access to uploaded evidence

The current implementation is a capstone prototype and should not be used as-is for sensitive production compliance data.

---

## Limitations

Current limitations include:

1. The demonstration organizational corpus is synthetic.
2. Evidence quality depends on the quality and completeness of uploaded documents.
3. LLM assessments can still contain errors.
4. Evidence Coverage is not equivalent to regulatory or framework compliance.
5. The application does not issue certifications.
6. Cross-Encoder reranking adds retrieval latency.
7. Large framework assessments can require many LLM API calls.
8. ChromaDB deployment requires persistent-storage planning.
9. Uploaded files may require persistent cloud storage in a production deployment.
10. The current authentication mechanism is intentionally simple for the capstone.
11. The current evaluation dataset is limited in size.
12. Human GRC review remains necessary for final decisions.

---

## Design Decisions

The primary architecture decisions are documented in:

```text
ADR.md
```

Key decisions include:

- Local multilingual embeddings
- ChromaDB vector storage
- Hybrid retrieval
- Reciprocal Rank Fusion
- Cross-Encoder reranking
- Cohere-based evidence assessment
- Deterministic Evidence Coverage scoring
- Human review instead of automated compliance certification

---

## Future Improvements

Potential future improvements include:

- Production-grade identity management
- Multi-tenant organizational workspaces
- Persistent cloud document storage
- Incremental indexing
- Retrieval caching
- Assessment caching
- Additional cybersecurity frameworks
- Cross-framework control mapping
- Human approval workflows
- Improved answer relevancy
- Larger independent evaluation datasets
- Automated evidence freshness checks
- Audit trails
- Exportable assessment reports

---

## Responsible Use

ComplianceRAG is designed as a decision-support system.

Its output should be reviewed by qualified cybersecurity, GRC, compliance, or audit professionals.

A `SUPPORTED` result means that relevant evidence was found and assessed as supporting a framework requirement within the system's available evidence.

It does **not** mean that an organization has been formally certified as compliant.

---


---

## Author

Developed as a RAG Engineering Capstone Project.

## License

This project is intended for educational and demonstration purposes.