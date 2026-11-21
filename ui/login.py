import streamlit as st

from services.auth_service import AuthService
from ui.components import flash, go_to, show_flash


def show_login():
    show_flash()
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.header("Sign In")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", type="primary", width="stretch")

        if submitted:
            user, message = AuthService().login_user(email, password)
            if user:
                st.session_state["user"] = user
                flash(f"Welcome back, {user['username']}!")
                go_to(st.session_state.pop("next_page", None) or "home")
            else:
                st.error(message)

        st.markdown("---")
        if st.button("Don't have an account? Register"):
            go_to("register")
