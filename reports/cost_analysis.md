# ComplianceRAG Cost Analysis

## Overview

This document estimates the monthly LLM inference cost of operating ComplianceRAG at three user scales:

- 1,000 users
- 10,000 users
- 100,000 users

The estimates focus on the primary variable API cost: generation using Cohere Command A.

## Current Architecture

ComplianceRAG uses:

- Cohere Command A (`command-a-03-2025`) for LLM generation and evidence assessment.
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` for local embeddings.
- ChromaDB for vector storage.
- BM25 for lexical retrieval.
- Cross-Encoder reranking.

Because embeddings, BM25 retrieval, and reranking are executed locally, they do not incur per-token Cohere API charges in the current architecture.

Hosting, persistent storage, bandwidth, monitoring, and other infrastructure costs are excluded from the calculations below because they depend on the final deployment environment.

## Pricing Assumption

The cost model uses the Cohere Command A pricing available at the time of this analysis:

- Input: $2.50 per 1 million tokens
- Output: $10.00 per 1 million tokens

Actual production costs may change if Cohere updates its pricing.

## Usage Assumptions

For estimation purposes, the following average workload is assumed:

- 10 RAG queries per user per month
- 2,500 input tokens per query
- 300 output tokens per query

These values represent an estimated production workload rather than measurements from every possible user interaction.

## Estimated Cost Per Query

Input cost:

2,500 × ($2.50 / 1,000,000) = $0.00625

Output cost:

300 × ($10.00 / 1,000,000) = $0.00300

Estimated total:

$0.00625 + $0.00300 = $0.00925 per query

## Monthly Cost Scenarios

| Users | Queries per User | Monthly Queries | Estimated LLM Cost |
|---:|---:|---:|---:|
| 1,000 | 10 | 10,000 | $92.50 |
| 10,000 | 10 | 100,000 | $925.00 |
| 100,000 | 10 | 1,000,000 | $9,250.00 |

## Cost Optimization Opportunities

Several strategies could reduce production cost:

1. Cache repeated queries and assessment results.
2. Avoid rerunning unchanged framework assessments.
3. Limit retrieved context to the most relevant evidence.
4. Keep prompts concise to reduce input tokens.
5. Use deterministic scoring outside the LLM where possible.
6. Run embeddings and reranking locally, as implemented in the current architecture.
7. Batch or precompute framework assessments when appropriate.

## Limitations

This analysis is an estimate rather than a billing forecast.

Actual cost depends on:

- Number of queries per user
- Prompt and context length
- Generated response length
- Model pricing changes
- Repeated framework assessments
- Hosting and storage requirements
- Production traffic patterns

The estimates exclude infrastructure costs and focus on LLM inference.

## Conclusion

At the assumed workload, ComplianceRAG's estimated monthly Cohere generation cost ranges from approximately $92.50 for 1,000 users to $9,250 for 100,000 users.

The architecture reduces external API dependence by performing embeddings, lexical retrieval, vector search, reranking, and deterministic evidence-coverage scoring locally.