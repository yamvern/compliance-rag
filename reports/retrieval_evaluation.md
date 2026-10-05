## Hard Challenge Set

A second set of 30 harder questions was created using:

- paraphrased questions
- scenario-based questions
- reasoning questions
- cross-policy questions

### Results

| Method | Recall@5 |
|---|---:|
| Vector Search | 96.67% |
| Hybrid Search | 90.00% |
| Hybrid + Reranker | 93.33% |

All configurations exceeded the required 80% Recall@5 target.

### Findings

Vector retrieval performed best on the hard challenge set.

The challenge questions frequently used wording different from the source
documents, which favored semantic retrieval.

Adding BM25 introduced some lexical noise and reduced Recall@5.

CrossEncoder reranking recovered part of that loss, improving hybrid
retrieval from 90.00% to 93.33%.

An experiment increasing the reranking candidate pool from 10 to 20 reduced
Hybrid + Reranker Recall@5 from 93.33% to 90.00%. The larger candidate pool
was therefore rejected.

The final local retrieval configuration uses a candidate pool of 10 before
reranking.