import streamlit as st

# Set page config first, before any other Streamlit commands
st.set_page_config(
    page_title="Meeting Request System",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from utils.common import (
    init_session_state, 
    load_all_css, 
    display_logout_button,
    display_back_button
)

from pages.auth import show_login, show_signup
from pages.landing import show_landing_page
from pages.request import show_request_page
from pages.dashboard import show_dashboard_page
from pages.response import show_response_page

load_all_css()
init_session_state()

def main():
    """Main application function"""
    #st.session_state.authenticated = True
    
    if not st.session_state.authenticated:
        if st.session_state.auth_page == 'login':
            show_login()
        else:
            show_signup()
    else:
        display_logout_button()
        display_back_button()

        if st.session_state.page == 'landing':
            show_landing_page()
        elif st.session_state.page == 'request':
            show_request_page()
        elif st.session_state.page == 'dashboard':
            show_dashboard_page()
        else:  
            show_response_page()

if __name__ == "__main__":
    main() 