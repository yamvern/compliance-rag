STATUS_SCORES = {
    "SUPPORTED": 1.0,
    "PARTIAL": 0.5,
    "NO_EVIDENCE": 0.0,
}


def calculate_evidence_coverage(assessments: list[dict]) -> dict:
    """
    Calculate evidence coverage using deterministic rules.

    NEEDS_REVIEW is excluded from the denominator until
    a human reviewer resolves it.
    """

    supported = 0
    partial = 0
    no_evidence = 0
    needs_review = 0

    earned_points = 0.0
    assessable_controls = 0

    for item in assessments:
        status = item["status"].upper()

        if status == "SUPPORTED":
            supported += 1
            earned_points += STATUS_SCORES["SUPPORTED"]
            assessable_controls += 1

        elif status == "PARTIAL":
            partial += 1
            earned_points += STATUS_SCORES["PARTIAL"]
            assessable_controls += 1

        elif status == "NO_EVIDENCE":
            no_evidence += 1
            earned_points += STATUS_SCORES["NO_EVIDENCE"]
            assessable_controls += 1

        elif status == "NEEDS_REVIEW":
            needs_review += 1

        else:
            raise ValueError(f"Unknown assessment status: {status}")

    if assessable_controls == 0:
        coverage = 0.0
    else:
        coverage = (
            earned_points / assessable_controls
        ) * 100

    return {
        "evidence_coverage": round(coverage, 2),
        "supported": supported,
        "partial": partial,
        "no_evidence": no_evidence,
        "needs_review": needs_review,
        "assessable_controls": assessable_controls,
        "total_controls": len(assessments),
    }


if __name__ == "__main__":
    sample = [
        {"status": "SUPPORTED"},
        {"status": "SUPPORTED"},
        {"status": "PARTIAL"},
        {"status": "NO_EVIDENCE"},
        {"status": "NEEDS_REVIEW"},
    ]

    result = calculate_evidence_coverage(sample)

    print(result)