import argparse
import json

from assessment.evidence_assessor import (
    assess_requirement,
)

from assessment.nist_requirements import (
    get_nist_control,
    build_assessment_requirement,
)


def assess_control(
    control_id,
):
    control = get_nist_control(
        control_id
    )

    requirement = (
        build_assessment_requirement(
            control
        )
    )

    result = assess_requirement(
        requirement
    )

    print()
    print("=" * 80)
    print("NIST CONTROL")
    print("=" * 80)

    print(
        f"ID: {control['id']}"
    )

    print(
        f"Function: "
        f"{control['function_name']}"
    )

    print(
        f"Category: "
        f"{control['category_name']}"
    )

    print()

    print(
        control["text"]
    )

    print()
    print("=" * 80)
    print("ASSESSMENT")
    print("=" * 80)

    print(
        json.dumps(
            result["assessment"],
            indent=2,
            ensure_ascii=False,
        )
    )

    print()
    print("=" * 80)
    print("RETRIEVED EVIDENCE")
    print("=" * 80)

    evidence = result.get(
        "evidence",
        [],
    )

    for item in evidence:

        metadata = item.get(
            "metadata",
            {}
        )

        print(
            f"{metadata.get('source', 'Unknown')} "
            f"- chunk "
            f"{metadata.get('chunk', 'N/A')}"
        )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Assess one NIST CSF 2.0 "
            "subcategory using ComplianceRAG."
        )
    )

    parser.add_argument(
        "--control",
        required=True,
        help=(
            "NIST control ID, "
            "for example PR.AA-03"
        ),
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    assess_control(
        args.control.upper()
    )


if __name__ == "__main__":
    main()