import streamlit as st
from services.auth_service import AuthService

def show_login():
    st.header("Sign In")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign In"):
        auth_service = AuthService()
        user, message = auth_service.login_user(email, password)
        
        if user:
            st.success(message)
            st.session_state['user'] = user
            st.rerun()
        else:
            st.error(message)

    st.markdown("---")
    if st.button("Don't have an account? Register"):
        st.session_state['page'] = 'register'
        st.rerun()
