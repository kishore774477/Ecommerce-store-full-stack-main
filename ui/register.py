import streamlit as st

from services.auth_service import AuthService
from ui.components import flash, go_to


def show_register():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.header("Register")
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password", help="At least 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create account", type="primary", width="stretch")

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = AuthService().register_user(username, email, password)
                if success:
                    flash("Account created — please sign in.")
                    go_to("login")
                else:
                    st.error(message)

        st.markdown("---")
        if st.button("Already have an account? Sign In"):
            go_to("login")
