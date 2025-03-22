import streamlit as st
import requests
import json
import pandas as pd

# API endpoint
API_BASE_URL = "http://localhost:5000/api"

# Configure page settings
st.set_page_config(
    page_title="Meeting Request System",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS with glassmorphism and neomorphism design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-color: #00F5FF;
        --primary-light: #80FFFF;
        --primary-dark: #00C4FF;
        --background: #0A0F1E;
        --surface: #151C32;
        --text: #E2E8F0;
        --text-light: #94A3B8;
        --accent: #FF2E63;
        --success: #00FFA3;
        --warning: #FFB86C;
        --error: #FF5555;
    }

    .main {
        font-family: 'Space Grotesk', sans-serif;
        background: linear-gradient(135deg, #0A0F1E 0%, #1A1F35 100%);
        color: var(--text);
        min-height: 100vh;
    }
    
    /* Glass card effect */
    .glass-card {
        background: rgba(21, 28, 50, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 245, 255, 0.1);
    }
    
    /* Neomorphic elements */
    .neo-input {
        background: rgba(21, 28, 50, 0.8);
        border: 1px solid rgba(0, 245, 255, 0.1);
        border-radius: 12px;
        padding: 14px 18px;
        color: var(--text);
        transition: all 0.3s ease;
    }
    
    .neo-input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.2);
    }
    
    .neo-button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: var(--background);
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
    }
    
    .neo-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 25px rgba(0, 245, 255, 0.4);
    }
    
    .neo-button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        transform: rotate(45deg);
        transition: 0.5s;
    }
    
    .neo-button:hover::after {
        left: 100%;
    }
    
    /* Form styling */
    .form-container {
        max-width: 450px;
        margin: 2rem auto;
    }
    
    .form-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .form-header h1 {
        color: var(--primary-color);
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .form-header p {
        color: var(--text-light);
        font-size: 1.1rem;
    }
    
    /* Custom Streamlit elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(21, 28, 50, 0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        color: var(--text) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.2) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)) !important;
        color: var(--background) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 25px rgba(0, 245, 255, 0.4) !important;
    }

    /* Card styling */
    .card {
        background: rgba(21, 28, 50, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 245, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 245, 255, 0.1);
        transition: all 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 245, 255, 0.2);
    }

    .status-badge {
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .status-pending {
        background: rgba(255, 184, 108, 0.2);
        color: var(--warning);
        border: 1px solid var(--warning);
    }

    .status-accepted {
        background: rgba(0, 255, 163, 0.2);
        color: var(--success);
        border: 1px solid var(--success);
    }

    .status-rejected {
        background: rgba(255, 85, 85, 0.2);
        color: var(--error);
        border: 1px solid var(--error);
    }

    /* Landing page cards */
    .landing-card {
        background: rgba(21, 28, 50, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid rgba(0, 245, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 245, 255, 0.1);
        position: relative;
        overflow: hidden;
    }

    .landing-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            45deg,
            transparent,
            rgba(0, 245, 255, 0.1),
            transparent
        );
        transform: translateX(-100%);
        transition: 0.5s;
    }

    .landing-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 12px 40px rgba(0, 245, 255, 0.2);
    }

    .landing-card:hover::before {
        transform: translateX(100%);
    }

    /* Additional styles */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: 1px;
    }

    a {
        color: var(--primary-color);
        text-decoration: none;
        transition: all 0.3s ease;
    }

    a:hover {
        color: var(--primary-light);
        text-shadow: 0 0 10px rgba(0, 245, 255, 0.4);
    }

    /* Streamlit selectbox styling */
    .stSelectbox > div > div {
        background: rgba(21, 28, 50, 0.8) !important;
        border: 1px solid rgba(0, 245, 255, 0.1) !important;
        border-radius: 12px !important;
    }

    .stSelectbox > div > div:hover {
        border-color: var(--primary-color) !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--background);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary-dark);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'auth_page' not in st.session_state:
    st.session_state.auth_page = 'login'
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def show_login():
    st.markdown("""
        <div class="form-container glass-card">
            <div class="form-header">
                <h1>Welcome Back</h1>
                <p>Sign in to continue to the Meeting Request System</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")
        
        if submitted:
            try:
                response = requests.post(f"{API_BASE_URL}/auth/login", 
                    json={"email": email, "password": password})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.authenticated = True
                    st.session_state.user_info = data['user']
                    st.session_state.token = data['token']
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.button("Create an account"):
        st.session_state.auth_page = 'signup'
        st.experimental_rerun()

def show_signup():
    st.markdown("""
        <div class="form-container glass-card">
            <div class="form-header">
                <h1>Create Account</h1>
                <p>Join the Meeting Request System</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Frontend", "Backend", "HR", "Marketing", "Sales", "Support"])
        submitted = st.form_submit_button("Sign Up")
        
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
                    st.experimental_rerun()
                else:
                    st.error(response.json().get('error', 'Could not create account'))
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.button("Back to login"):
        st.session_state.auth_page = 'login'
        st.experimental_rerun()

def main():
    st.session_state.authenticated = True
    if not st.session_state.authenticated:
        if st.session_state.auth_page == 'login':
            show_login()
        else:
            show_signup()
    else:
        # Add logout button in the header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("Meeting Request System")
        with col2:
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_info = None
                st.session_state.page = 'landing'
                st.experimental_rerun()

        # Show back button if not on landing page
        if st.session_state.page != 'landing':
            if st.button("← Back to Landing Page"):
                st.session_state.page = 'landing'
                st.experimental_rerun()

        # Main content
        if st.session_state.page == 'landing':
            st.markdown("""
                <h1 style="text-align: center; margin-bottom: 2rem;">Welcome to the Meeting Request System</h1>
                <p style="text-align: center; margin-bottom: 3rem;">Choose your action below</p>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div class="landing-card">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🔧</div>
                        <h2 style="color: #FF416C; margin-bottom: 1rem;">Request a Meeting</h2>
                        <p style="color: #E0E0E0; margin-bottom: 2rem;">
                            Need to schedule a meeting with a team agent? Submit your request with all the necessary details.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Request Meeting", key="request_btn"):
                    st.session_state.page = 'request'
                    st.experimental_rerun()
            
            with col2:
                st.markdown("""
                    <div class="landing-card">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">⚙️</div>
                        <h2 style="color: #FF416C; margin-bottom: 1rem;">Respond to Requests</h2>
                        <p style="color: #E0E0E0; margin-bottom: 2rem;">
                            Team agent? Access all meeting requests, review details, and respond to them from your dashboard.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("View Requests", key="response_btn"):
                    st.session_state.page = 'response'
                    st.experimental_rerun()

        elif st.session_state.page == 'request':
            st.title("Create Meeting Request")
            
            with st.form("meeting_request_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    team_agent = st.selectbox(
                        "Select Team Agent",
                        ["Frontend", "Backend", "HR", "Marketing", "Sales", "Support"]
                    )
                    meeting_link = st.text_input("Meeting Link")
                
                with col2:
                    meeting_goal = st.text_area("Meeting Goal")
                    prompt_text = st.text_area("Perpetual Question")
                
                submitted = st.form_submit_button("Submit Request")
                
                if submitted:
                    if not all([meeting_goal, meeting_link, prompt_text]):
                        st.error("Please fill in all fields")
                    else:
                        data = {
                            "team_agent": team_agent,
                            "prompt_text": prompt_text,
                            "meeting_goal": meeting_goal,
                            "meeting_link": meeting_link,
                            "requester_name": st.session_state.user_info['name']
                        }
                        
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/meetings",
                                json=data,
                                headers=headers
                            )
                            if response.status_code == 200:
                                st.success("Meeting request submitted successfully!")
                                st.session_state.page = 'landing'
                                st.experimental_rerun()
                            else:
                                st.error(f"Failed to submit meeting request: {response.json().get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

        else:  # Response page
            st.title("Meeting Requests Dashboard")
            
            if st.button("🔄 Refresh"):
                st.experimental_rerun()
            
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.get(f"{API_BASE_URL}/meetings", headers=headers)
                meetings = response.json()
                
                if not meetings:
                    st.markdown("""
                        <div class="card" style="text-align: center; padding: 3rem;">
                            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
                            <h2>No Meeting Requests</h2>
                            <p>There are currently no meeting requests in the system.</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    for meeting in meetings:
                        with st.container():
                            st.markdown(f"""
                                <div class="card">
                                    <h3>{meeting['requester_name']}'s Request</h3>
                                    <p><strong>Team Agent:</strong> {meeting['team_agent']}</p>
                                    <p><strong>Meeting Goal:</strong> {meeting['meeting_goal']}</p>
                                    <p><strong>Meeting Link:</strong> <a href="{meeting['meeting_link']}">{meeting['meeting_link']}</a></p>
                                    <p><strong>Prompt:</strong> {meeting['prompt_text']}</p>
                                    <p><strong>Status:</strong> <span class="status-badge status-{meeting['status'].lower()}">{meeting['status'].upper()}</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if st.session_state.user_info['role'] == 'responder':
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    if st.button("Accept", key=f"accept_{meeting['_id']}"):
                                        requests.put(
                                            f"{API_BASE_URL}/meetings/{meeting['_id']}",
                                            json={"status": "accepted"},
                                            headers=headers
                                        )
                                        st.experimental_rerun()
                                with col2:
                                    if st.button("Reject", key=f"reject_{meeting['_id']}"):
                                        requests.put(
                                            f"{API_BASE_URL}/meetings/{meeting['_id']}",
                                            json={"status": "rejected"},
                                            headers=headers
                                        )
                                        st.experimental_rerun()
                                with col3:
                                    if st.button("Mark Pending", key=f"pending_{meeting['_id']}"):
                                        requests.put(
                                            f"{API_BASE_URL}/meetings/{meeting['_id']}",
                                            json={"status": "pending"},
                                            headers=headers
                                        )
                                        st.experimental_rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 