import json

from assessment.evidence_assessor import assess_requirement


TEST_REQUIREMENTS = [
    {
        "name": "SUPPORTED TEST",
        "requirement": (
            "Remote administrative access must use "
            "multi-factor authentication."
        ),
        "expected": "SUPPORTED",
    },
    {
        "name": "PARTIAL TEST",
        "requirement": (
            "User access privileges must be periodically reviewed, "
            "and the organization must define a mandatory review frequency."
        ),
        "expected": "PARTIAL",
    },
    {
        "name": "NO EVIDENCE TEST",
        "requirement": (
            "All removable media devices must be inventoried, "
            "encrypted, and formally approved before use."
        ),
        "expected": "NO_EVIDENCE",
    },
]


def main():
    for test in TEST_REQUIREMENTS:
        print("\n" + "=" * 80)
        print(test["name"])
        print("=" * 80)

        print("\nRequirement:")
        print(test["requirement"])

        result = assess_requirement(
            test["requirement"]
        )

        assessment = result["assessment"]

        print("\nExpected:")
        print(test["expected"])

        print("\nActual:")
        print(assessment["status"])

        print("\nAssessment:")
        print(
            json.dumps(
                assessment,
                indent=2,
                ensure_ascii=False,
            )
        )

        print("\nEvidence retrieved:")

        for evidence in result["retrieved_evidence"]:
            print(
                "-",
                evidence["metadata"].get("source"),
                "chunk",
                evidence["metadata"].get("chunk_index"),
            )


if __name__ == "__main__":
    main()