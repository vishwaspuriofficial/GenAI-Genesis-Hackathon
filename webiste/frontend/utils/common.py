"""
Common utilities for the frontend application
"""
import streamlit as st
import time
import os

# API Constants
API_BASE_URL = "http://localhost:8000/api"

# Roles/Teams available in the system
ROLES = ["Frontend", "Backend", "Design", "Product", "Marketing", "Sales"]

# Max size for file uploads in MB
MAX_FILE_SIZE_MB = 10

def load_css(css_file):
    """Load a CSS file and return its contents as a string"""
    try:
        with open(css_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: CSS file not found: {css_file}")
        return ""
    except Exception as e:
        print(f"Error loading CSS file {css_file}: {str(e)}")
        return ""

def load_all_css():
    """Load all CSS files from the css directory and apply them"""
    try:
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
            css_content = load_css(css_path)
            all_css += css_content
        
        if all_css:
            # Add comment to CSS to denote we're avoiding using HTML in components
            all_css = "/* Base styling only - Do not use HTML in Streamlit components directly */\n" + all_css
            st.markdown(f'<style>{all_css}</style>', unsafe_allow_html=True)
            
            # Display warning in development environment
            if os.environ.get('STREAMLIT_ENV') == 'development':
                st.warning("⚠️ Using raw HTML in Streamlit components can cause rendering issues. Please use native Streamlit components instead.")
    except Exception as e:
        st.error(f"Error loading CSS: {str(e)}")

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

# Alias for init_session_state for backwards compatibility
initialize_session_state = init_session_state

def is_logged_in():
    """Check if user is logged in"""
    return st.session_state.get('authenticated', False)

def set_page(page_name):
    """Set the current page in session state and trigger rerun"""
    st.session_state.page = page_name
    st.rerun()

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