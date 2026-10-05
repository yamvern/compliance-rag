import os

import streamlit as st
from dotenv import load_dotenv


load_dotenv()


def require_login():
    """
    Simple authentication gate for the capstone application.
    """

    if st.session_state.get("authenticated"):
        return

    st.title("🛡️ ComplianceRAG")

    st.caption(
        "Cybersecurity Evidence & Gap Assessment Platform"
    )

    st.subheader("Sign in")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password",
        )

        submitted = st.form_submit_button(
            "Sign in",
            use_container_width=True,
        )

    if submitted:
        expected_username = os.getenv("APP_USERNAME")
        expected_password = os.getenv("APP_PASSWORD")

        if (
            username == expected_username
            and password == expected_password
        ):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.rerun()

        else:
            st.error("Invalid username or password.")

    st.stop()


def logout_button():
    """
    Render a logout button in the sidebar.
    """

    username = st.session_state.get(
        "username",
        "User",
    )

    st.sidebar.write(
        f"Signed in as **{username}**"
    )

    if st.sidebar.button(
        "Log out",
        use_container_width=True,
    ):
        st.session_state.clear()
        st.rerun()