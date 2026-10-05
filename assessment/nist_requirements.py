import json
from pathlib import Path


CATALOG_PATH = Path(
    "data/frameworks/nist_csf_2.0_catalog.json"
)


def load_nist_catalog():
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"NIST catalog not found: {CATALOG_PATH}"
        )

    with open(
        CATALOG_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def get_nist_controls(
    function_filter="ALL",
):
    catalog = load_nist_catalog()

    controls = catalog.get(
        "subcategories",
        [],
    )

    if function_filter == "ALL":
        return controls

    return [
        control
        for control in controls
        if control.get("function")
        == function_filter
    ]


def get_nist_control(
    control_id,
):
    controls = get_nist_controls()

    for control in controls:
        if control["id"] == control_id:
            return control

    raise ValueError(
        f"NIST control not found: {control_id}"
    )


def build_assessment_requirement(
    control,
):
    """
    Build the final requirement sent to the RAG assessor.

    NIST subcategory text is authoritative.
    Implementation examples are supporting context only.
    """

    requirement = control["text"]

    examples = control.get(
        "implementation_examples",
        [],
    )

    example_texts = [
        example["text"]
        for example in examples
        if example.get("text")
    ]

    parts = [
        f"NIST CSF 2.0 Subcategory {control['id']}",
        "",
        "Requirement:",
        requirement,
    ]

    if example_texts:
        parts.extend(
            [
                "",
                (
                    "Implementation examples "
                    "for assessment context only:"
                ),
            ]
        )

        for text in example_texts:
            parts.append(
                f"- {text}"
            )

    parts.extend(
        [
            "",
            (
                "Assess whether the organization's "
                "retrieved evidence supports the "
                "NIST subcategory itself. "
                "Implementation examples are illustrative "
                "and must not be treated as individually "
                "mandatory requirements."
            ),
        ]
    )

    return "\n".join(parts)