import json
import re
from pathlib import Path


SOURCE_PATH = Path(
    "data/frameworks/nist_csf_2.0_official.json"
)

OUTPUT_PATH = Path(
    "data/frameworks/nist_csf_2.0_catalog.json"
)


FUNCTION_PREFIXES = {
    "GV": "GOVERN",
    "ID": "IDENTIFY",
    "PR": "PROTECT",
    "DE": "DETECT",
    "RS": "RESPOND",
    "RC": "RECOVER",
}


SUBCATEGORY_PATTERN = re.compile(
    r"^(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}$"
)


EXAMPLE_PATTERN = re.compile(
    r"^(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}\.\d{3}$"
)


def load_source():
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Official NIST JSON not found: {SOURCE_PATH}"
        )

    with open(
        SOURCE_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def get_elements(data):
    """
    NIST export structure:

    response
      └── elements
            ├── documents
            ├── elements
            ├── relationship_types
            └── relationships
    """

    try:
        return data[
            "response"
        ][
            "elements"
        ][
            "elements"
        ]

    except KeyError as exc:
        raise ValueError(
            "Unexpected NIST JSON structure."
        ) from exc


def build_withdrawn_set(elements):
    """
    Any element with a matching WR-<id> entry is considered
    withdrawn / legacy and should not be assessed as an
    active CSF 2.0 subcategory.
    """

    withdrawn = set()

    for element in elements:
        if (
            element.get("element_type")
            != "withdraw_reason"
        ):
            continue

        identifier = element.get(
            "element_identifier",
            "",
        )

        if identifier.startswith("WR-"):
            withdrawn.add(
                identifier[3:]
            )

    return withdrawn


def build_functions(elements):
    functions = {}

    for element in elements:
        if (
            element.get("element_type")
            != "function"
        ):
            continue

        identifier = element.get(
            "element_identifier"
        )

        if identifier not in FUNCTION_PREFIXES:
            continue

        functions[identifier] = {
            "id": identifier,
            "name": element.get(
                "title",
                FUNCTION_PREFIXES[
                    identifier
                ],
            ),
            "text": element.get(
                "text",
                "",
            ),
        }

    return functions


def build_categories(elements):
    categories = {}

    for element in elements:
        if (
            element.get("element_type")
            != "category"
        ):
            continue

        identifier = element.get(
            "element_identifier",
            "",
        )

        if not any(
            identifier.startswith(
                prefix + "."
            )
            for prefix in FUNCTION_PREFIXES
        ):
            continue

        categories[identifier] = {
            "id": identifier,
            "title": element.get(
                "title",
                "",
            ),
            "text": element.get(
                "text",
                "",
            ),
        }

    return categories


def build_examples(elements):
    """
    Group implementation examples by parent subcategory.

    Example:
        PR.AA-03.200
    belongs to:
        PR.AA-03
    """

    examples = {}

    for element in elements:
        if (
            element.get("element_type")
            != "implementation_example"
        ):
            continue

        identifier = element.get(
            "element_identifier",
            "",
        )

        if not EXAMPLE_PATTERN.match(
            identifier
        ):
            continue

        parent_id = identifier.rsplit(
            ".",
            1,
        )[0]

        examples.setdefault(
            parent_id,
            [],
        )

        examples[parent_id].append(
            {
                "id": identifier,
                "title": element.get(
                    "title",
                    "",
                ),
                "text": element.get(
                    "text",
                    "",
                ),
            }
        )

    return examples


def build_active_subcategories(
    elements,
    withdrawn,
    categories,
    examples,
):
    subcategories = []

    seen = set()

    for element in elements:
        if (
            element.get("element_type")
            != "subcategory"
        ):
            continue

        identifier = element.get(
            "element_identifier",
            "",
        )

        if not SUBCATEGORY_PATTERN.match(
            identifier
        ):
            continue

        # Skip withdrawn / legacy subcategories.
        if identifier in withdrawn:
            continue

        # Skip duplicate projection entries that
        # contain no actual subcategory text.
        text = element.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        if identifier in seen:
            continue

        seen.add(identifier)

        function_id = identifier.split(
            ".",
            1,
        )[0]

        category_id = identifier.split(
            "-",
            1,
        )[0]

        category = categories.get(
            category_id,
            {},
        )

        subcategories.append(
            {
                "id": identifier,
                "function": function_id,
                "function_name": FUNCTION_PREFIXES.get(
                    function_id,
                    function_id,
                ),
                "category": category_id,
                "category_name": category.get(
                    "title",
                    category_id,
                ),
                "category_text": category.get(
                    "text",
                    "",
                ),
                "text": text,
                "implementation_examples": examples.get(
                    identifier,
                    [],
                ),
            }
        )

    return subcategories


def validate_catalog(
    functions,
    categories,
    subcategories,
):
    if len(functions) != 6:
        raise ValueError(
            f"Expected 6 functions, found {len(functions)}"
        )

    ids = [
        item["id"]
        for item in subcategories
    ]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate active subcategory IDs found."
        )

    for item in subcategories:
        if not item["text"]:
            raise ValueError(
                f"Empty text for {item['id']}"
            )

        if (
            item["category"]
            not in categories
        ):
            raise ValueError(
                f"Missing category for {item['id']}"
            )


def save_catalog(
    functions,
    categories,
    subcategories,
):
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    catalog = {
        "framework": "NIST Cybersecurity Framework",
        "version": "2.0",
        "source": "Official NIST JSON export",
        "functions": functions,
        "categories": categories,
        "total_subcategories": len(
            subcategories
        ),
        "subcategories": subcategories,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            catalog,
            f,
            indent=2,
            ensure_ascii=False,
        )


def print_summary(
    functions,
    categories,
    subcategories,
    withdrawn,
):
    print()
    print(
        "=" * 70
    )
    print(
        "NIST CSF 2.0 ACTIVE CATALOG"
    )
    print(
        "=" * 70
    )

    print(
        f"Functions: {len(functions)}"
    )

    print(
        f"Categories found: {len(categories)}"
    )

    print(
        f"Withdrawn / legacy IDs detected: {len(withdrawn)}"
    )

    print(
        f"Active subcategories: {len(subcategories)}"
    )

    print()

    for prefix, name in FUNCTION_PREFIXES.items():
        count = sum(
            1
            for item in subcategories
            if item["function"] == prefix
        )

        print(
            f"{name:10} ({prefix}): {count}"
        )

    print()
    print(
        "First 10 active subcategories:"
    )
    print(
        "-" * 70
    )

    for item in subcategories[:10]:
        print(
            f"{item['id']} | "
            f"{item['category_name']}"
        )

        print(
            item["text"]
        )

        print(
            f"Implementation examples: "
            f"{len(item['implementation_examples'])}"
        )

        print()


def main():
    data = load_source()

    elements = get_elements(
        data
    )

    withdrawn = build_withdrawn_set(
        elements
    )

    functions = build_functions(
        elements
    )

    categories = build_categories(
        elements
    )

    examples = build_examples(
        elements
    )

    subcategories = build_active_subcategories(
        elements=elements,
        withdrawn=withdrawn,
        categories=categories,
        examples=examples,
    )

    validate_catalog(
        functions=functions,
        categories=categories,
        subcategories=subcategories,
    )

    save_catalog(
        functions=functions,
        categories=categories,
        subcategories=subcategories,
    )

    print_summary(
        functions=functions,
        categories=categories,
        subcategories=subcategories,
        withdrawn=withdrawn,
    )

    print(
        "Saved catalog to:"
    )
    print(
        OUTPUT_PATH
    )


if __name__ == "__main__":
    main()