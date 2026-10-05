import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


import streamlit as st

from app.auth import (
    require_login,
    logout_button,
)

from app.feedback import (
    render_feedback_page,
)

from app.upload import (
    render_upload_page,
)


REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "batch_assessment.json"
)


REPORT_PATH = Path(
    "reports/batch_assessment.json"
)

FUNCTION_NAMES = {
    "GV": "GOVERN",
    "ID": "IDENTIFY",
    "PR": "PROTECT",
    "DE": "DETECT",
    "RS": "RESPOND",
    "RC": "RECOVER",
}


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ComplianceRAG",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# AUTHENTICATION
# =========================================================

require_login()
logout_button()


# =========================================================
# HELPERS
# =========================================================

def load_report():
    if not REPORT_PATH.exists():
        return None

    try:
        with open(
            REPORT_PATH,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return None


def status_icon(status):
    icons = {
        "SUPPORTED": "✅",
        "PARTIAL": "🟡",
        "NO_EVIDENCE": "❌",
        "NEEDS_REVIEW": "🔍",
    }

    return icons.get(
        status,
        "•",
    )


def status_label(status):
    labels = {
        "SUPPORTED": "Supported",
        "PARTIAL": "Partial",
        "NO_EVIDENCE": "No Evidence",
        "NEEDS_REVIEW": "Needs Review",
    }

    return labels.get(
        status,
        status,
    )


def report_modified_time():
    if not REPORT_PATH.exists():
        return None

    timestamp = (
        REPORT_PATH.stat().st_mtime
    )

    return datetime.fromtimestamp(
        timestamp
    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def run_assessment(
    function_filter,
):
    command = [
        sys.executable,
        "-m",
        "assessment.batch_assessment",
        "--function",
        function_filter,
    ]

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
    )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown(
    "# 🛡️ ComplianceRAG"
)

st.sidebar.caption(
    "NIST CSF 2.0 Evidence & Gap Assessment"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Documents",
        "User Testing",
        "About",
    ],
)

st.sidebar.divider()

st.sidebar.caption(
    "RAG Engineering Capstone"
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    header_left, header_right = st.columns(
        [4, 2]
    )

    with header_left:

        st.title(
            "🛡️ NIST CSF 2.0 Readiness Dashboard"
        )

        st.caption(
            "Evidence-based cybersecurity readiness "
            "and documentation gap assessment"
        )

    with header_right:

        selected_scope = st.selectbox(
            "Assessment Scope",
            [
                "PR",
                "GV",
                "ID",
                "DE",
                "RS",
                "RC",
                "ALL",
            ],
            format_func=lambda value: (
                "ALL — Full NIST CSF 2.0"
                if value == "ALL"
                else (
                    f"{value} — "
                    f"{FUNCTION_NAMES[value]}"
                )
            ),
        )

        run_clicked = st.button(
            "▶ Run Assessment",
            type="primary",
            use_container_width=True,
        )

    # -----------------------------------------------------
    # Run Assessment
    # -----------------------------------------------------

    if run_clicked:

        if selected_scope == "ALL":

            st.warning(
                "A full NIST CSF 2.0 assessment "
                "evaluates all 106 active subcategories "
                "and will use substantially more API calls."
            )

        with st.spinner(
            f"Assessing NIST CSF 2.0 "
            f"scope: {selected_scope}..."
        ):

            result = run_assessment(
                selected_scope
            )

        if result.returncode == 0:

            st.success(
                "Assessment completed successfully."
            )

            st.rerun()

        else:

            st.error(
                "Assessment failed."
            )

            with st.expander(
                "View error details"
            ):

                st.code(
                    result.stderr
                    or result.stdout
                )

    # -----------------------------------------------------
    # Load Report
    # -----------------------------------------------------

    report = load_report()

    if report is None:

        st.warning(
            "No assessment report is available."
        )

        st.info(
            "Upload organizational documents, "
            "index them, then run a NIST CSF "
            "assessment."
        )

        st.stop()

    summary = report.get(
        "summary",
        {},
    )

    controls = report.get(
        "controls",
        [],
    )

    function_summaries = report.get(
        "function_summaries",
        {},
    )

    category_summaries = report.get(
        "category_summaries",
        {},
    )

    framework = report.get(
        "framework",
        "NIST Cybersecurity Framework",
    )

    version = report.get(
        "framework_version",
        "2.0",
    )

    assessment_scope = report.get(
        "assessment_scope",
        "Unknown",
    )

    total_assessed = report.get(
        "total_controls_assessed",
        len(controls),
    )

    catalog_total = report.get(
        "catalog_total_subcategories",
        106,
    )

    modified_time = (
        report_modified_time()
    )

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    metadata1, metadata2, metadata3 = (
        st.columns(3)
    )

    metadata1.info(
        f"**Framework:** "
        f"{framework} {version}"
    )

    metadata2.info(
        f"**Assessment Scope:** "
        f"{assessment_scope}"
    )

    metadata3.info(
        f"**Subcategories Assessed:** "
        f"{total_assessed} / {catalog_total}"
    )

    if modified_time:

        st.caption(
            f"Last assessment: "
            f"{modified_time}"
        )

    st.divider()

    # -----------------------------------------------------
    # Overall Metrics
    # -----------------------------------------------------

    st.header(
        "Assessment Overview"
    )

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    coverage = summary.get(
        "evidence_coverage",
        0,
    )

    col1.metric(
        "Evidence Coverage",
        f"{coverage}%",
    )

    col2.metric(
        "Supported",
        summary.get(
            "supported",
            0,
        ),
    )

    col3.metric(
        "Partial",
        summary.get(
            "partial",
            0,
        ),
    )

    col4.metric(
        "No Evidence",
        summary.get(
            "no_evidence",
            0,
        ),
    )

    col5.metric(
        "Needs Review",
        summary.get(
            "needs_review",
            0,
        ),
    )

    st.progress(
        min(
            max(
                coverage / 100,
                0,
            ),
            1,
        )
    )

    st.caption(
        "Evidence Coverage represents the degree "
        "to which uploaded organizational evidence "
        "supports the assessed NIST CSF 2.0 "
        "subcategories. It is not a certification "
        "or formal audit opinion."
    )

    st.divider()

    # -----------------------------------------------------
    # Function Coverage
    # -----------------------------------------------------

    st.header(
        "Function Coverage"
    )

    if not function_summaries:

        st.info(
            "No function summary data available."
        )

    else:

        function_columns = st.columns(
            len(function_summaries)
        )

        for column, (
            function_id,
            function_data,
        ) in zip(
            function_columns,
            function_summaries.items(),
        ):

            with column:

                function_coverage = (
                    function_data.get(
                        "evidence_coverage",
                        0,
                    )
                )

                st.metric(
                    (
                        f"{function_id} "
                        f"{function_data.get('name', '')}"
                    ),
                    f"{function_coverage}%",
                )

                st.caption(
                    (
                        f"Supported: "
                        f"{function_data.get('supported', 0)}"
                        f" | Partial: "
                        f"{function_data.get('partial', 0)}"
                    )
                )

    st.divider()

    # -----------------------------------------------------
    # Category Coverage
    # -----------------------------------------------------

    st.header(
        "Category Coverage"
    )

    if category_summaries:

        category_chart = {
            (
                f"{category_id} — "
                f"{data.get('name', '')}"
            ): data.get(
                "evidence_coverage",
                0,
            )
            for category_id, data
            in category_summaries.items()
        }

        st.bar_chart(
            category_chart
        )

        with st.expander(
            "View Category Details"
        ):

            for category_id, data in (
                category_summaries.items()
            ):

                st.markdown(
                    f"**{category_id} — "
                    f"{data.get('name', '')}**"
                )

                st.write(
                    f"Evidence Coverage: "
                    f"{data.get('evidence_coverage', 0)}%"
                )

                st.caption(
                    f"Supported: "
                    f"{data.get('supported', 0)} | "
                    f"Partial: "
                    f"{data.get('partial', 0)} | "
                    f"No Evidence: "
                    f"{data.get('no_evidence', 0)} | "
                    f"Needs Review: "
                    f"{data.get('needs_review', 0)}"
                )

                st.divider()

    else:

        st.info(
            "No category summary data available."
        )

    st.divider()

    # -----------------------------------------------------
    # Subcategory Assessment
    # -----------------------------------------------------

    st.header(
        "NIST Subcategory Assessment"
    )

    filter1, filter2, filter3 = (
        st.columns(3)
    )

    available_functions = sorted(
        {
            item.get("function")
            for item in controls
            if item.get("function")
        }
    )

    available_categories = sorted(
        {
            item.get("category")
            for item in controls
            if item.get("category")
        }
    )

    with filter1:

        function_filter = st.multiselect(
            "Function",
            available_functions,
            default=available_functions,
            format_func=lambda value: (
                f"{value} — "
                f"{FUNCTION_NAMES.get(value, value)}"
            ),
        )

    with filter2:

        category_filter = st.multiselect(
            "Category",
            available_categories,
            default=available_categories,
        )

    with filter3:

        status_filter = st.multiselect(
            "Status",
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

    search_text = st.text_input(
        "Search NIST subcategories",
        placeholder=(
            "Example: authentication, backup, "
            "logging, incident..."
        ),
    )

    # -----------------------------------------------------
    # Apply Filters
    # -----------------------------------------------------

    filtered_controls = []

    for control in controls:

        if (
            control.get("function")
            not in function_filter
        ):
            continue

        if (
            control.get("category")
            not in category_filter
        ):
            continue

        if (
            control.get("status")
            not in status_filter
        ):
            continue

        searchable_text = (
            f"{control.get('id', '')} "
            f"{control.get('function_name', '')} "
            f"{control.get('category_name', '')} "
            f"{control.get('requirement', '')} "
            f"{control.get('reason', '')}"
        ).lower()

        if (
            search_text
            and search_text.lower()
            not in searchable_text
        ):
            continue

        filtered_controls.append(
            control
        )

    st.caption(
        f"Showing {len(filtered_controls)} "
        f"of {len(controls)} assessed "
        f"subcategories"
    )

    # -----------------------------------------------------
    # Subcategory Cards
    # -----------------------------------------------------

    for control in filtered_controls:

        status = control.get(
            "status",
            "NEEDS_REVIEW",
        )

        label = (
            f"{status_icon(status)} "
            f"{control.get('id', '')} — "
            f"{control.get('category_name', '')} "
            f"[{status_label(status)}]"
        )

        with st.expander(
            label
        ):

            info1, info2 = (
                st.columns(2)
            )

            info1.write(
                "**Function:** "
                f"{control.get('function', '')} — "
                f"{control.get('function_name', '')}"
            )

            info2.write(
                "**Category:** "
                f"{control.get('category', '')} — "
                f"{control.get('category_name', '')}"
            )

            st.markdown(
                "### NIST Requirement"
            )

            st.write(
                control.get(
                    "requirement",
                    "",
                )
            )

            st.markdown(
                "### Evidence Assessment"
            )

            reason = control.get(
                "reason",
                "",
            )

            if status == "SUPPORTED":

                st.success(
                    reason
                )

            elif status == "PARTIAL":

                st.warning(
                    reason
                )

            elif status == "NO_EVIDENCE":

                st.error(
                    reason
                )

            else:

                st.info(
                    reason
                )

            gap = control.get(
                "gap"
            )

            if gap:

                st.markdown(
                    "### Identified Gap"
                )

                st.warning(
                    gap
                )

            recommendation = (
                control.get(
                    "recommendation"
                )
            )

            if recommendation:

                st.markdown(
                    "### Recommendation"
                )

                st.write(
                    recommendation
                )

            st.markdown(
                "### Evidence Sources"
            )

            evidence_sources = (
                control.get(
                    "evidence_sources",
                    [],
                )
            )

            if not evidence_sources:

                st.info(
                    "No supporting organizational "
                    "evidence was cited."
                )

            else:

                for source in (
                    evidence_sources
                ):

                    st.write(
                        f"📄 **"
                        f"{source.get('source', 'Unknown')}"
                        f"** — chunk "
                        f"{source.get('chunk', 'N/A')}"
                    )

    # -----------------------------------------------------
    # Priority Gaps
    # -----------------------------------------------------

    st.divider()

    st.header(
        "Priority Documentation Gaps"
    )

    priority_gaps = [
        control
        for control in controls
        if control.get("status")
        in {
            "PARTIAL",
            "NO_EVIDENCE",
        }
    ]

    if not priority_gaps:

        st.success(
            "No documentation gaps were "
            "identified in this assessment scope."
        )

    else:

        no_evidence_gaps = [
            item
            for item in priority_gaps
            if item.get("status")
            == "NO_EVIDENCE"
        ]

        partial_gaps = [
            item
            for item in priority_gaps
            if item.get("status")
            == "PARTIAL"
        ]

        st.caption(
            f"High-priority No Evidence: "
            f"{len(no_evidence_gaps)} | "
            f"Partial Evidence: "
            f"{len(partial_gaps)}"
        )

        ordered_gaps = (
            no_evidence_gaps
            + partial_gaps
        )

        for control in ordered_gaps:

            status = control.get(
                "status",
                "",
            )

            st.markdown(
                f"{status_icon(status)} "
                f"**{control.get('id', '')} — "
                f"{control.get('category_name', '')}**"
            )

            gap = control.get(
                "gap"
            )

            if gap:

                st.caption(
                    gap
                )

    st.divider()

    st.caption(
        "ComplianceRAG performs evidence-based "
        "readiness and documentation gap assessment "
        "against NIST CSF 2.0. Results do not "
        "constitute formal certification, audit "
        "opinion, or legal compliance determination."
    )


# =========================================================
# UPLOAD DOCUMENTS
# =========================================================

elif page == "Upload Documents":

    st.title(
        "📄 Company Documents"
    )

    st.caption(
        "Upload organizational cybersecurity "
        "policies and procedures used as "
        "assessment evidence."
    )

    render_upload_page()

    st.divider()

    st.info(
        "After indexing new documents, return "
        "to Dashboard and run the desired "
        "NIST CSF 2.0 assessment scope."
    )


# =========================================================
# USER TESTING
# =========================================================

elif page == "User Testing":

    render_feedback_page()


# =========================================================
# ABOUT
# =========================================================

elif page == "About":

    st.title(
        "About ComplianceRAG"
    )

    st.markdown(
        """
## Project Purpose

**ComplianceRAG** is a cybersecurity Governance,
Risk, and Compliance evidence-assessment platform
built using Retrieval-Augmented Generation.

Organizations can upload cybersecurity policies
and procedures, and the system evaluates the
available documentary evidence against active
**NIST Cybersecurity Framework 2.0 subcategories**.

---

## Assessment Workflow

```text
Company Documents
        ↓
Document Extraction
        ↓
Chunking
        ↓
Multilingual Embeddings
        ↓
Chroma Vector Database
        ↓
Vector Retrieval + BM25
        ↓
Reciprocal Rank Fusion
        ↓
CrossEncoder Reranking
        ↓
Evidence Assessment
        ↓
SUPPORTED / PARTIAL /
NO_EVIDENCE / NEEDS_REVIEW
        ↓
Evidence Coverage + Gaps
        ↓
NIST CSF 2.0 Dashboard"""
    )