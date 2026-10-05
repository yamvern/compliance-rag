import json
import os
from pathlib import Path

import cohere
from dotenv import load_dotenv

from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank


QUESTIONS_PATH = Path(
    "evaluation/ragas_questions.json"
)

OUTPUT_PATH = Path(
    "reports/ragas_results.json"
)

load_dotenv()

COHERE_API_KEY = os.getenv(
    "COHERE_API_KEY"
)

if not COHERE_API_KEY:
    raise ValueError(
        "COHERE_API_KEY was not found in .env"
    )


co = cohere.ClientV2(
    api_key=COHERE_API_KEY
)

MODEL_NAME = "command-a-03-2025"


def load_questions():
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def retrieve_contexts(
    question,
    top_k=5,
):
    candidates = hybrid_search(
        question,
        top_k=10,
        candidate_k=10,
    )

    results = rerank(
        question,
        candidates,
        top_k=top_k,
    )

    contexts = [
        item["text"]
        for item in results
    ]

    sources = [
        {
            "source": item[
                "metadata"
            ].get(
                "source",
                "unknown",
            ),
            "chunk": item[
                "metadata"
            ].get(
                "chunk_index",
                "unknown",
            ),
        }
        for item in results
    ]

    return contexts, sources


def generate_answer(
    question,
    contexts,
):
    context_text = "\n\n".join(
        f"[CONTEXT {i}]\n{text}"
        for i, text in enumerate(
            contexts,
            start=1,
        )
    )

    system_prompt = """
You are a cybersecurity assistant.

Answer the user's question using ONLY the supplied organizational context.

Do not use outside knowledge.
Do not invent controls, procedures, or evidence.
If the answer is not supported by the context, say that the available evidence is insufficient.

Give a concise answer in 2 to 4 sentences.
""".strip()

    user_prompt = f"""
QUESTION:

{question}

ORGANIZATIONAL CONTEXT:

{context_text}

Answer using only the context above.
""".strip()

    response = co.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
    )

    return (
        response.message
        .content[0]
        .text
        .strip()
    )


def build_dataset():
    questions = load_questions()

    rows = []

    for index, item in enumerate(
        questions,
        start=1,
    ):
        question = item["question"]
        reference = item["reference"]

        print(
            f"[{index}/{len(questions)}] "
            f"{question}"
        )

        contexts, sources = (
            retrieve_contexts(
                question
            )
        )

        answer = generate_answer(
            question,
            contexts,
        )

        rows.append(
            {
                "question": question,
                "answer": answer,
                "contexts": contexts,
                "reference": reference,
                "sources": sources,
            }
        )

    return rows


def save_results(rows):
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            rows,
            f,
            indent=2,
            ensure_ascii=False,
        )


def main():
    rows = build_dataset()

    save_results(
        rows
    )

    print()
    print("=" * 70)
    print("RAG DATASET GENERATED")
    print("=" * 70)

    print(
        f"Questions: {len(rows)}"
    )

    print(
        "Saved to:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()