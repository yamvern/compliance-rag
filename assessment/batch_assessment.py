import json
from pathlib import Path

from assessment.evidence_assessor import assess_requirement
from assessment.scoring import calculate_evidence_coverage


REQUIREMENTS = [
    {
        "id": "AC-01",
        "title": "Remote Administrative MFA",
        "requirement": (
            "Remote administrative access must use "
            "multi-factor authentication."
        ),
    },
    {
        "id": "AC-02",
        "title": "Periodic Access Reviews",
        "requirement": (
            "User access privileges must be periodically reviewed, "
            "and the organization must define a mandatory review frequency."
        ),
    },
    {
        "id": "IR-01",
        "title": "Incident Reporting",
        "requirement": (
            "Personnel must report suspected cybersecurity incidents "
            "to the appropriate security function."
        ),
    },
    {
        "id": "IR-02",
        "title": "Lessons Learned",
        "requirement": (
            "The organization must perform documented post-incident "
            "lessons-learned reviews after cybersecurity incidents."
        ),
    },
    {
        "id": "RM-01",
        "title": "Cyber Risk Assessment",
        "requirement": (
            "Cybersecurity risks must be identified and assessed "
            "based on likelihood and business impact."
        ),
    },
    {
        "id": "AM-01",
        "title": "Asset Inventory",
        "requirement": (
            "The organization must maintain an inventory of "
            "information systems, devices, software, and important assets."
        ),
    },
    {
        "id": "BK-01",
        "title": "Backup Restoration Testing",
        "requirement": (
            "Backup restoration must be tested periodically."
        ),
    },
    {
        "id": "BC-01",
        "title": "Business Continuity Testing",
        "requirement": (
            "Business continuity plans must be tested on a "
            "defined recurring schedule."
        ),
    },
    {
        "id": "TP-01",
        "title": "Supplier Security",
        "requirement": (
            "Cybersecurity risks must be considered before engaging "
            "important third-party suppliers."
        ),
    },
    {
        "id": "LG-01",
        "title": "Security Logging",
        "requirement": (
            "Security-relevant systems must log authentication events "
            "and administrative actions."
        ),
    },
    {
        "id": "VM-01",
        "title": "Vulnerability Prioritization",
        "requirement": (
            "Vulnerabilities must be prioritized according to "
            "severity and business impact."
        ),
    },
    {
        "id": "RMV-01",
        "title": "Removable Media Controls",
        "requirement": (
            "All removable media devices must be inventoried, "
            "encrypted, and formally approved before use."
        ),
    },
]


def run_batch_assessment():
    results = []

    print("\nRunning batch assessment...\n")

    for index, control in enumerate(REQUIREMENTS, start=1):
        print(
            f"[{index}/{len(REQUIREMENTS)}] "
            f"{control['id']} - {control['title']}"
        )

        result = assess_requirement(
            control["requirement"]
        )

        assessment = result["assessment"]

        results.append(
            {
                "id": control["id"],
                "title": control["title"],
                "requirement": control["requirement"],
                "status": assessment["status"],
                "reason": assessment["reason"],
                "gap": assessment["gap"],
                "recommendation": assessment["recommendation"],
                "evidence_sources": assessment["evidence_sources"],
            }
        )

    summary = calculate_evidence_coverage(results)

    output = {
        "summary": summary,
        "controls": results,
    }

    Path("reports").mkdir(exist_ok=True)

    with open(
        "reports/batch_assessment.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("\n" + "=" * 70)
    print("ASSESSMENT SUMMARY")
    print("=" * 70)

    print(
        "Evidence Coverage:",
        f"{summary['evidence_coverage']}%"
    )
    print("Supported:", summary["supported"])
    print("Partial:", summary["partial"])
    print("No Evidence:", summary["no_evidence"])
    print("Needs Review:", summary["needs_review"])

    print(
        "\nSaved report to:",
        "reports/batch_assessment.json"
    )


if __name__ == "__main__":
    run_batch_assessment()