from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path(
    "data/frameworks/nist_csf_2.0.pdf"
)


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"NIST PDF not found: {PDF_PATH}"
        )

    reader = PdfReader(
        str(PDF_PATH)
    )

    print(
        f"Pages: {len(reader.pages)}"
    )

    print(
        "\nSearching for NIST CSF "
        "subcategory identifiers...\n"
    )

    prefixes = (
        "GV.",
        "ID.",
        "PR.",
        "DE.",
        "RS.",
        "RC.",
    )

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text() or ""

        matching_lines = []

        for line in text.splitlines():
            cleaned = " ".join(
                line.split()
            )

            if any(
                prefix in cleaned
                for prefix in prefixes
            ):
                matching_lines.append(
                    cleaned
                )

        if matching_lines:
            print(
                "=" * 80
            )

            print(
                f"PAGE {page_number}"
            )

            print(
                "=" * 80
            )

            for line in matching_lines:
                print(line)


if __name__ == "__main__":
    main()