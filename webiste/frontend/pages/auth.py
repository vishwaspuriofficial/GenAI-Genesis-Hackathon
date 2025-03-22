import streamlit as st
import requests
from utils.common import API_BASE_URL

def show_login():
    """Show login form and handle authentication"""
    st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <div class="auth-logo">
                    <span>📅</span> Meeting Request System
                </div>
                <h2 class="auth-title">Welcome Back</h2>
                <p class="auth-subtitle">Sign in to continue to the Meeting Request System</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            try:
                response = requests.post(f"{API_BASE_URL}/auth/login", 
                    json={"email": email, "password": password})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.authenticated = True
                    st.session_state.user_info = data['user']
                    st.session_state.token = data['token']
                    st.session_state.page = 'landing'
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("""
        <div class="auth-footer">
            Don't have an account? 
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Create an account", use_container_width=True):
        st.session_state.auth_page = 'signup'
        st.rerun()

def show_signup():
    """Show signup form and handle account creation"""
    st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <div class="auth-logo">
                    <span>📅</span> Meeting Request System
                </div>
                <h2 class="auth-title">Create Account</h2>
                <p class="auth-subtitle">Join the Meeting Request System</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Frontend", "Backend", "HR", "Marketing", "Sales", "Support"])
        submitted = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submitted:
            try:
                response = requests.post(f"{API_BASE_URL}/auth/signup", 
                    json={
                        "name": name,
                        "email": email,
                        "password": password,
                        "role": role
                    })
                if response.status_code == 201:
                    st.success("Account created successfully! Please sign in.")
                    st.session_state.auth_page = 'login'
                    st.rerun()
                else:
                    st.error(response.json().get('error', 'Could not create account'))
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("""
        <div class="auth-footer">
            Already have an account? 
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Back to login", use_container_width=True):
        st.session_state.auth_page = 'login'
        st.rerun() 