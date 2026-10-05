import csv
from datetime import datetime
from pathlib import Path

import streamlit as st


FEEDBACK_FILE = Path("reports/user_feedback.csv")


def save_feedback(
    tester_name,
    usability_rating,
    clarity_rating,
    evidence_rating,
    useful_feature,
    issue,
    suggestion,
):
    FEEDBACK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_exists = FEEDBACK_FILE.exists()

    with open(
        FEEDBACK_FILE,
        "a",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "tester_name",
                    "usability_rating",
                    "clarity_rating",
                    "evidence_rating",
                    "useful_feature",
                    "issue",
                    "suggestion",
                ]
            )

        writer.writerow(
            [
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                tester_name,
                usability_rating,
                clarity_rating,
                evidence_rating,
                useful_feature,
                issue,
                suggestion,
            ]
        )


def render_feedback_page():

    st.title("🧪 User Testing")

    st.caption(
        "Help evaluate the usability and usefulness "
        "of ComplianceRAG."
    )

    st.info(
        "Please explore the Dashboard, review at least "
        "three control assessments, inspect the evidence "
        "sources, and then complete this form."
    )

    with st.form(
        "user_testing_form"
    ):

        tester_name = st.text_input(
            "Tester name or identifier",
            placeholder="Example: Tester 1",
        )

        usability_rating = st.slider(
            "How easy was the system to use?",
            min_value=1,
            max_value=5,
            value=4,
        )

        clarity_rating = st.slider(
            "How clear were the assessment results?",
            min_value=1,
            max_value=5,
            value=4,
        )

        evidence_rating = st.slider(
            "How useful were the evidence sources?",
            min_value=1,
            max_value=5,
            value=4,
        )

        useful_feature = st.selectbox(
            "Which feature was most useful?",
            [
                "Evidence Coverage Dashboard",
                "Control Assessment",
                "Gap Analysis",
                "Recommendations",
                "Evidence Sources",
                "Document Upload",
            ],
        )

        issue = st.text_area(
            "What was confusing or difficult?",
        )

        suggestion = st.text_area(
            "What would you improve?",
        )

        submitted = st.form_submit_button(
            "Submit Feedback",
            use_container_width=True,
            type="primary",
        )

    if submitted:

        if not tester_name.strip():

            st.warning(
                "Please enter a tester name "
                "or identifier."
            )

        else:

            save_feedback(
                tester_name=tester_name.strip(),
                usability_rating=usability_rating,
                clarity_rating=clarity_rating,
                evidence_rating=evidence_rating,
                useful_feature=useful_feature,
                issue=issue,
                suggestion=suggestion,
            )

            st.success(
                "Thank you. Your feedback "
                "has been recorded."
            )