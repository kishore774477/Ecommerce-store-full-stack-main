import streamlit as st
from services.auth_service import AuthService
from utils.validators import validate_email, validate_password_strength

def show_register():
    st.header("Register")
    
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
            return
            
        if not validate_email(email):
            st.error("Invalid email format")
            return
            
        if not validate_password_strength(password):
            st.error("Password must be at least 8 characters")
            return
            
        auth_service = AuthService()
        success, message = auth_service.register_user(username, email, password)
        
        if success:
            st.success(message)
            st.info("Please sign in")
        else:
            st.error(message)

    st.markdown("---")
    if st.button("Already have an account? Sign In"):
        st.session_state['page'] = 'login'
        st.rerun()
