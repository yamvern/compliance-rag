import argparse
import json
from pathlib import Path

from assessment.evidence_assessor import assess_requirement
from assessment.scoring import calculate_evidence_coverage
from assessment.nist_requirements import (
    load_nist_catalog,
    get_nist_controls,
    build_assessment_requirement,
)


REPORT_PATH = Path(
    "reports/batch_assessment.json"
)

VALID_FUNCTIONS = {
    "GV",
    "ID",
    "PR",
    "DE",
    "RS",
    "RC",
    "ALL",
}


def build_result_record(
    control,
    assessment,
):
    return {
        "id": control["id"],

        "title": control.get(
            "category_name",
            control["id"],
        ),

        "function": control.get(
            "function",
            "",
        ),

        "function_name": control.get(
            "function_name",
            "",
        ),

        "category": control.get(
            "category",
            "",
        ),

        "category_name": control.get(
            "category_name",
            "",
        ),

        "requirement": control["text"],

        "status": assessment["status"],

        "reason": assessment["reason"],

        "gap": assessment.get(
            "gap"
        ),

        "recommendation": assessment.get(
            "recommendation"
        ),

        "evidence_sources": assessment.get(
            "evidence_sources",
            [],
        ),
    }


def calculate_function_summaries(
    results,
):
    summaries = {}

    function_ids = sorted(
        {
            item["function"]
            for item in results
            if item.get("function")
        }
    )

    for function_id in function_ids:

        function_controls = [
            item
            for item in results
            if item["function"] == function_id
        ]

        if not function_controls:
            continue

        function_summary = (
            calculate_evidence_coverage(
                function_controls
            )
        )

        function_name = (
            function_controls[0].get(
                "function_name",
                function_id,
            )
        )

        summaries[function_id] = {
            "name": function_name,
            **function_summary,
        }

    return summaries


def calculate_category_summaries(
    results,
):
    summaries = {}

    category_ids = sorted(
        {
            item["category"]
            for item in results
            if item.get("category")
        }
    )

    for category_id in category_ids:

        category_controls = [
            item
            for item in results
            if item["category"] == category_id
        ]

        if not category_controls:
            continue

        category_summary = (
            calculate_evidence_coverage(
                category_controls
            )
        )

        category_name = (
            category_controls[0].get(
                "category_name",
                category_id,
            )
        )

        function_id = (
            category_controls[0].get(
                "function",
                "",
            )
        )

        function_name = (
            category_controls[0].get(
                "function_name",
                "",
            )
        )

        summaries[category_id] = {
            "name": category_name,
            "function": function_id,
            "function_name": function_name,
            **category_summary,
        }

    return summaries


def run_batch_assessment(
    function_filter="ALL",
    limit=None,
):
    catalog = load_nist_catalog()

    controls = get_nist_controls(
        function_filter=function_filter,
    )

    if limit is not None:

        if limit <= 0:
            raise ValueError(
                "--limit must be greater than 0."
            )

        controls = controls[:limit]

    if not controls:
        raise ValueError(
            "No NIST CSF 2.0 subcategories matched "
            f"the selected function: {function_filter}"
        )

    results = []

    print()
    print("=" * 70)
    print("NIST CSF 2.0 BATCH ASSESSMENT")
    print("=" * 70)

    print(
        f"Assessment scope: {function_filter}"
    )

    print(
        f"Controls to assess: {len(controls)}"
    )

    print()

    for index, control in enumerate(
        controls,
        start=1,
    ):

        print(
            f"[{index}/{len(controls)}] "
            f"{control['id']} - "
            f"{control.get('category_name', '')}"
        )

        assessment_requirement = (
            build_assessment_requirement(
                control
            )
        )

        result = assess_requirement(
            assessment_requirement
        )

        assessment = result.get(
            "assessment",
            {}
        )

        required_fields = {
            "status",
            "reason",
        }

        missing_fields = (
            required_fields
            - set(assessment.keys())
        )

        if missing_fields:
            raise ValueError(
                f"Assessment for {control['id']} "
                f"is missing fields: "
                f"{sorted(missing_fields)}"
            )

        record = build_result_record(
            control=control,
            assessment=assessment,
        )

        results.append(
            record
        )

        print(
            f"    Status: {record['status']}"
        )

    overall_summary = (
        calculate_evidence_coverage(
            results
        )
    )

    function_summaries = (
        calculate_function_summaries(
            results
        )
    )

    category_summaries = (
        calculate_category_summaries(
            results
        )
    )

    output = {
        "framework": catalog.get(
            "framework",
            "NIST Cybersecurity Framework",
        ),

        "framework_version": catalog.get(
            "version",
            "2.0",
        ),

        "assessment_scope": (
            function_filter
        ),

        "total_controls_assessed": (
            len(results)
        ),

        "catalog_total_subcategories": (
            catalog.get(
                "total_subcategories",
                len(
                    catalog.get(
                        "subcategories",
                        [],
                    )
                ),
            )
        ),

        "summary": overall_summary,

        "function_summaries": (
            function_summaries
        ),

        "category_summaries": (
            category_summaries
        ),

        "controls": results,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        REPORT_PATH,
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
    print("ASSESSMENT SUMMARY")
    print("=" * 70)

    print(
        "Framework:",
        f"{output['framework']} "
        f"{output['framework_version']}",
    )

    print(
        "Scope:",
        function_filter,
    )

    print(
        "Controls assessed:",
        len(results),
    )

    print(
        "Evidence Coverage:",
        f"{overall_summary['evidence_coverage']}%",
    )

    print(
        "Supported:",
        overall_summary["supported"],
    )

    print(
        "Partial:",
        overall_summary["partial"],
    )

    print(
        "No Evidence:",
        overall_summary["no_evidence"],
    )

    print(
        "Needs Review:",
        overall_summary["needs_review"],
    )

    if function_summaries:

        print()
        print(
            "FUNCTION COVERAGE"
        )

        print(
            "-" * 70
        )

        for function_id, summary in (
            function_summaries.items()
        ):

            print(
                f"{function_id} "
                f"{summary['name']}: "
                f"{summary['evidence_coverage']}%"
            )

    print()

    print(
        "Saved report to:",
        REPORT_PATH,
    )

    return output


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Run ComplianceRAG against "
            "NIST Cybersecurity Framework 2.0."
        )
    )

    parser.add_argument(
        "--function",
        default="ALL",
        type=str.upper,
        choices=sorted(
            VALID_FUNCTIONS
        ),
        help=(
            "Assessment scope: "
            "GV, ID, PR, DE, RS, RC, or ALL."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Optional maximum number of "
            "subcategories to assess."
        ),
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    run_batch_assessment(
        function_filter=args.function,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()