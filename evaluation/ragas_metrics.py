import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory

from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
)


INPUT_PATH = Path(
    "reports/ragas_results.json"
)

OUTPUT_PATH = Path(
    "reports/ragas_metrics.json"
)

MODEL_NAME = "cohere/command-a-03-2025"

EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

LITELLM_MASTER_KEY = os.getenv(
    "LITELLM_MASTER_KEY"
)

if not LITELLM_MASTER_KEY:
    raise ValueError(
        "LITELLM_MASTER_KEY was not found in .env"
    )


# =========================================================
# DATASET
# =========================================================

def load_dataset():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"RAG dataset not found: {INPUT_PATH}"
        )

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


# =========================================================
# RAGAS METRICS
# =========================================================

def create_metrics():
    """
    Create RAGAS metrics using LiteLLM as an
    OpenAI-compatible local proxy.

    LiteLLM forwards requests to Cohere.
    """

    async_client = AsyncOpenAI(
        api_key=LITELLM_MASTER_KEY,
        base_url="http://localhost:4000/v1",
    )

    llm = llm_factory(
        MODEL_NAME,
        provider="openai",
        client=async_client,
        temperature=0,
    )

    embeddings = embedding_factory(
        "huggingface",
        model=EMBEDDING_MODEL,
    )

    return {
        "faithfulness": Faithfulness(
            llm=llm
        ),
        "answer_relevancy": AnswerRelevancy(
            llm=llm,
            embeddings=embeddings,
        ),
        "context_precision": ContextPrecision(
            llm=llm
        ),
        "context_recall": ContextRecall(
            llm=llm
        ),
    }


# =========================================================
# SINGLE SAMPLE EVALUATION
# =========================================================

async def evaluate_row(
    row,
    metrics,
    index,
    total,
):
    question = row["question"]
    answer = row["answer"]
    contexts = row["contexts"]
    reference = row["reference"]

    print()
    print(
        f"[{index}/{total}] {question}"
    )

    results = {}

    # -----------------------------------------------------
    # Faithfulness
    # -----------------------------------------------------

    faithfulness_result = (
        await metrics[
            "faithfulness"
        ].ascore(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts,
        )
    )

    results["faithfulness"] = float(
        faithfulness_result.value
    )

    print(
        "    Faithfulness:",
        round(
            results["faithfulness"],
            4,
        ),
    )

    # -----------------------------------------------------
    # Answer Relevancy
    # -----------------------------------------------------

    relevancy_result = (
        await metrics[
            "answer_relevancy"
        ].ascore(
            user_input=question,
            response=answer,
        )
    )

    results["answer_relevancy"] = float(
        relevancy_result.value
    )

    print(
        "    Answer Relevancy:",
        round(
            results["answer_relevancy"],
            4,
        ),
    )

    # -----------------------------------------------------
    # Context Precision
    # -----------------------------------------------------

    precision_result = (
        await metrics[
            "context_precision"
        ].ascore(
            user_input=question,
            reference=reference,
            retrieved_contexts=contexts,
        )
    )

    results["context_precision"] = float(
        precision_result.value
    )

    print(
        "    Context Precision:",
        round(
            results["context_precision"],
            4,
        ),
    )

    # -----------------------------------------------------
    # Context Recall
    # -----------------------------------------------------

    recall_result = (
        await metrics[
            "context_recall"
        ].ascore(
            user_input=question,
            reference=reference,
            retrieved_contexts=contexts,
        )
    )

    results["context_recall"] = float(
        recall_result.value
    )

    print(
        "    Context Recall:",
        round(
            results["context_recall"],
            4,
        ),
    )

    results["question"] = question
    results["answer"] = answer
    results["reference"] = reference

    return results


# =========================================================
# AVERAGES
# =========================================================

def calculate_average(
    rows,
    metric_name,
):
    values = [
        row[metric_name]
        for row in rows
    ]

    if not values:
        return 0.0

    return sum(values) / len(values)


# =========================================================
# MAIN EVALUATION
# =========================================================

async def main_async():
    dataset = load_dataset()

    metrics = create_metrics()

    results = []

    total = len(dataset)

    print()
    print("=" * 70)
    print("RAGAS EVALUATION")
    print("=" * 70)

    print(
        f"Evaluation samples: {total}"
    )

    print(
        f"Judge model: {MODEL_NAME}"
    )

    print(
        f"Embedding model: {EMBEDDING_MODEL}"
    )

    print(
        "LLM endpoint: "
        "http://localhost:4000/v1"
    )

    # Sequential on purpose to reduce
    # rate-limit pressure.
    for index, row in enumerate(
        dataset,
        start=1,
    ):

        try:

            result = await evaluate_row(
                row=row,
                metrics=metrics,
                index=index,
                total=total,
            )

            results.append(
                result
            )

        except Exception as exc:

            print(
                f"    ERROR: {exc}"
            )

            results.append(
                {
                    "question": row[
                        "question"
                    ],
                    "answer": row[
                        "answer"
                    ],
                    "reference": row[
                        "reference"
                    ],
                    "error": str(exc),
                }
            )

    successful = [
        row
        for row in results
        if "error" not in row
    ]

    if not successful:
        raise RuntimeError(
            "RAGAS evaluation failed "
            "for all samples."
        )

    summary = {
        "samples_total": total,

        "samples_successful": len(
            successful
        ),

        "samples_failed": (
            total
            - len(successful)
        ),

        "faithfulness": round(
            calculate_average(
                successful,
                "faithfulness",
            ),
            4,
        ),

        "answer_relevancy": round(
            calculate_average(
                successful,
                "answer_relevancy",
            ),
            4,
        ),

        "context_precision": round(
            calculate_average(
                successful,
                "context_precision",
            ),
            4,
        ),

        "context_recall": round(
            calculate_average(
                successful,
                "context_recall",
            ),
            4,
        ),
    }

    summary["overall_ragas_score"] = round(
        (
            summary["faithfulness"]
            + summary["answer_relevancy"]
            + summary["context_precision"]
            + summary["context_recall"]
        )
        / 4,
        4,
    )

    output = {
        "evaluation": "RAGAS",

        "evaluation_samples": total,

        "judge_model": MODEL_NAME,

        "embedding_model": (
            EMBEDDING_MODEL
        ),

        "summary": summary,

        "results": results,
    }

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
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 70)
    print("RAGAS SUMMARY")
    print("=" * 70)

    print(
        "Successful samples:",
        f"{summary['samples_successful']}"
        f"/{summary['samples_total']}",
    )

    print(
        "Faithfulness:",
        summary["faithfulness"],
    )

    print(
        "Answer Relevancy:",
        summary[
            "answer_relevancy"
        ],
    )

    print(
        "Context Precision:",
        summary[
            "context_precision"
        ],
    )

    print(
        "Context Recall:",
        summary[
            "context_recall"
        ],
    )

    print(
        "Overall RAGAS Score:",
        summary[
            "overall_ragas_score"
        ],
    )

    print()

    print(
        "Saved to:",
        OUTPUT_PATH,
    )


def main():
    asyncio.run(
        main_async()
    )


if __name__ == "__main__":
    main()