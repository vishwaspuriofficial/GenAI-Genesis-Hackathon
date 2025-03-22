import streamlit as st
import os

API_BASE_URL = "http://localhost:5000/api"

def load_css(css_file):
    try:
        with open(css_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def load_all_css():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_dir = os.path.join(current_dir, 'css')
    
    css_files = [
        "base.css",
        "streamlit.css",
        "landing.css",
        "forms.css",
        "dashboard.css",
        "auth.css"
    ]
    
    all_css = ""
    for css_file in css_files:
        css_path = os.path.join(css_dir, css_file)
        all_css += load_css(css_path)
    
    st.markdown(f'<style>{all_css}</style>', unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables if they don't exist"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = 'login'
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {'name': 'Guest', 'role': 'Visitor'}
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 'Meeting Details'

def display_logout_button():
    """Display logout button in the header"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Meeting Request System")
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_info = {'name': 'Guest', 'role': 'Visitor'}
            st.session_state.page = 'landing'
            st.rerun()

def display_back_button():
    """Display back button if not on landing page"""
    if st.session_state.page != 'landing':
        if st.button("← Back to Landing Page"):
            st.session_state.page = 'landing'
            st.rerun() 