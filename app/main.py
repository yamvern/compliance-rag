import json
from pathlib import Path
from auth import require_login, logout_button
import streamlit as st


REPORT_PATH = Path("reports/batch_assessment.json")


st.set_page_config(
    page_title="ComplianceRAG",
    page_icon="🛡️",
    layout="wide",
)
require_login()
logout_button()


def load_report():
    if not REPORT_PATH.exists():
        return None

    with open(
        REPORT_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def status_icon(status: str):
    icons = {
        "SUPPORTED": "✅",
        "PARTIAL": "🟡",
        "NO_EVIDENCE": "❌",
        "NEEDS_REVIEW": "🔍",
    }

    return icons.get(status, "•")


st.title("🛡️ ComplianceRAG")

st.caption(
    "Cybersecurity Evidence & Gap Assessment Platform"
)

report = load_report()

if report is None:
    st.error(
        "No assessment report found. "
        "Run the batch assessment first."
    )
    st.stop()


summary = report["summary"]
controls = report["controls"]


# -------------------------------------------------
# Overview
# -------------------------------------------------

st.header("Assessment Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Evidence Coverage",
    f"{summary['evidence_coverage']}%",
)

col2.metric(
    "Supported",
    summary["supported"],
)

col3.metric(
    "Partial",
    summary["partial"],
)

col4.metric(
    "No Evidence",
    summary["no_evidence"],
)

col5.metric(
    "Needs Review",
    summary["needs_review"],
)


st.progress(
    min(
        summary["evidence_coverage"] / 100,
        1.0,
    )
)


st.divider()


# -------------------------------------------------
# Controls
# -------------------------------------------------

st.header("Control Assessment")

status_filter = st.multiselect(
    "Filter by status",
    [
        "SUPPORTED",
        "PARTIAL",
        "NO_EVIDENCE",
        "NEEDS_REVIEW",
    ],
    default=[
        "SUPPORTED",
        "PARTIAL",
        "NO_EVIDENCE",
        "NEEDS_REVIEW",
    ],
)


filtered_controls = [
    control
    for control in controls
    if control["status"] in status_filter
]


for control in filtered_controls:

    label = (
        f"{status_icon(control['status'])} "
        f"{control['id']} — "
        f"{control['title']} "
        f"[{control['status']}]"
    )

    with st.expander(label):

        st.markdown("### Requirement")
        st.write(control["requirement"])

        st.markdown("### Assessment")
        st.write(control["reason"])

        if control["gap"]:
            st.markdown("### Gap")
            st.warning(control["gap"])

        st.markdown("### Recommendation")
        st.write(control["recommendation"])

        st.markdown("### Evidence Sources")

        evidence_sources = control.get(
            "evidence_sources",
            [],
        )

        if not evidence_sources:
            st.info("No supporting evidence cited.")

        else:
            for source in evidence_sources:

                st.write(
                    f"- **{source['source']}** "
                    f"(chunk {source['chunk']})"
                )


st.divider()

st.caption(
    "ComplianceRAG provides evidence-based readiness "
    "assessment and does not constitute formal certification."
)