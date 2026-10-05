import json
import os

import cohere
from dotenv import load_dotenv

from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank


load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY was not found in .env")


co = cohere.ClientV2(api_key=COHERE_API_KEY)

MODEL_NAME = "command-a-03-2025"


def retrieve_evidence(requirement: str, top_k: int = 5):
    """
    Retrieve and rerank organizational evidence
    relevant to a cybersecurity requirement.
    """

    candidates = hybrid_search(
        requirement,
        top_k=10,
        candidate_k=10,
    )

    evidence = rerank(
        requirement,
        candidates,
        top_k=top_k,
    )

    return evidence


def build_evidence_context(evidence):
    """
    Convert retrieved chunks into a structured
    context for the language model.
    """

    sections = []

    for index, item in enumerate(evidence, start=1):
        source = item["metadata"].get("source", "unknown")
        chunk = item["metadata"].get("chunk_index", "unknown")
        text = item["text"]

        sections.append(
            f"""
[EVIDENCE {index}]
Source: {source}
Chunk: {chunk}
Text:
{text}
""".strip()
        )

    return "\n\n".join(sections)


def assess_requirement(requirement: str):
    """
    Assess whether retrieved organizational evidence
    supports a cybersecurity requirement.
    """

    evidence = retrieve_evidence(requirement)

    context = build_evidence_context(evidence)

    system_prompt = """
You are a cybersecurity GRC evidence assessment assistant.

Your job is to evaluate whether the provided organizational evidence
supports the cybersecurity requirement.

You must use ONLY the supplied evidence.

Do not assume that a control exists unless the evidence explicitly
supports it.

Do not certify the organization as compliant.

Choose exactly one status:

SUPPORTED
- The evidence clearly and substantially supports the requirement.

PARTIAL
- Some relevant evidence exists, but an important part of the
  requirement is missing, unclear, or incomplete.

NO_EVIDENCE
- The supplied evidence does not support the requirement.

NEEDS_REVIEW
- The evidence is relevant but too ambiguous, conflicting, or
  insufficient to make a reliable assessment.

Return ONLY valid JSON using this structure:

{
  "status": "SUPPORTED | PARTIAL | NO_EVIDENCE | NEEDS_REVIEW",
  "reason": "Short evidence-based explanation",
  "gap": "What is missing, or null if no material gap exists",
  "recommendation": "Recommended next action",
  "evidence_sources": [
    {
      "source": "filename",
      "chunk": 0
    }
  ]
}

Only cite sources that were actually provided in the evidence.
""".strip()

    user_prompt = f"""
CYBERSECURITY REQUIREMENT:

{requirement}

ORGANIZATIONAL EVIDENCE:

{context}

Assess the requirement using only the organizational evidence above.
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

    raw_output = response.message.content[0].text.strip()

    # Remove Markdown fences if the model returns them.
    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "")
        raw_output = raw_output.replace("```", "")
        raw_output = raw_output.strip()

    try:
        assessment = json.loads(raw_output)
    except json.JSONDecodeError:
        raise ValueError(
            "Cohere returned invalid JSON:\n\n"
            + raw_output
        )

    return {
        "requirement": requirement,
        "assessment": assessment,
        "retrieved_evidence": evidence,
    }


if __name__ == "__main__":

    requirement = (
        "Remote administrative access must use "
        "multi-factor authentication."
    )

    result = assess_requirement(requirement)

    print("\n" + "=" * 80)
    print("REQUIREMENT")
    print("=" * 80)
    print(result["requirement"])

    print("\n" + "=" * 80)
    print("ASSESSMENT")
    print("=" * 80)
    print(
        json.dumps(
            result["assessment"],
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\n" + "=" * 80)
    print("RETRIEVED EVIDENCE")
    print("=" * 80)

    for item in result["retrieved_evidence"]:
        print(
            item["metadata"].get("source"),
            "- chunk",
            item["metadata"].get("chunk_index"),
        )