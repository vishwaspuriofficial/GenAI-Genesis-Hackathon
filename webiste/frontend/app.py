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
        --primary-color: #A742FF;
        --primary-light: #C78AFF;
        --primary-dark: #7B00FF;
        --secondary-color: #FF36F7;
        --background: #0A0014;
        --surface: #1A0033;
        --text: #E2E8F0;
        --text-light: #B8B8B8;
        --accent: #FF2E9F;
        --success: #00FFB3;
        --warning: #FFB86C;
        --error: #FF5555;
        --neon-glow: 0 0 10px rgba(167, 66, 255, 0.5),
                     0 0 20px rgba(167, 66, 255, 0.3),
                     0 0 30px rgba(167, 66, 255, 0.1);
    }

    .main {
        font-family: 'Space Grotesk', sans-serif;
        background: linear-gradient(135deg, var(--background) 0%, #1A0033 100%);
        color: var(--text);
        min-height: 100vh;
    }
    
    /* Glass card effect */
    .glass-card {
        background: rgba(26, 0, 51, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2.5rem;
        border: 1px solid rgba(167, 66, 255, 0.2);
        box-shadow: var(--neon-glow);
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
        max-width: 800px;
        margin: 2rem auto;
        padding: 2rem;
        background: rgba(21, 28, 50, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(0, 245, 255, 0.1);
    }
    
    .form-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .form-header h1 {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .form-header p {
        color: var(--text-light);
        font-size: 1.1rem;
    }
    
    /* Custom Streamlit elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(26, 0, 51, 0.8) !important;
        border: 1px solid rgba(167, 66, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        color: var(--text) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        box-shadow: var(--neon-glow) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 20px rgba(167, 66, 255, 0.6),
                   0 0 40px rgba(167, 66, 255, 0.4) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
        font-family: 'Space Grotesk', sans-serif !important;
        box-shadow: var(--neon-glow) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(167, 66, 255, 0.6),
                   0 0 40px rgba(167, 66, 255, 0.4) !important;
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
        background: rgba(26, 0, 51, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(167, 66, 255, 0.2);
        box-shadow: var(--neon-glow);
        margin-bottom: 2rem;
    }

    .landing-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: var(--primary-color);
        box-shadow: 0 0 20px rgba(167, 66, 255, 0.6),
                   0 0 40px rgba(167, 66, 255, 0.4),
                   0 0 60px rgba(167, 66, 255, 0.2);
    }

    .landing-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        transition: 0.5s;
    }

    .landing-card:hover::after {
        left: 100%;
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
        background: rgba(26, 0, 51, 0.8) !important;
        border: 1px solid rgba(167, 66, 255, 0.2) !important;
        border-radius: 12px !important;
        box-shadow: var(--neon-glow) !important;
    }

    .stSelectbox > div > div:hover {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 20px rgba(167, 66, 255, 0.6),
                   0 0 40px rgba(167, 66, 255, 0.4) !important;
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

    /* Dashboard cards */
    .dashboard-card {
        background: rgba(21, 28, 50, 0.7);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(0, 245, 255, 0.1);
        transition: all 0.3s ease;
    }

    .dashboard-card:hover {
        transform: translateY(-5px);
        border-color: var(--primary-color);
    }

    /* Stats container */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }

    .stat-card {
        background: rgba(26, 0, 51, 0.6);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(167, 66, 255, 0.2);
        box-shadow: var(--neon-glow);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        text-shadow: 0 0 10px rgba(167, 66, 255, 0.5);
    }

    /* Profile section */
    .profile-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: rgba(26, 0, 51, 0.5);
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid rgba(167, 66, 255, 0.2);
        box-shadow: var(--neon-glow);
    }

    .profile-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        box-shadow: var(--neon-glow);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    /* Navigation pills */
    .nav-pills {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        padding: 0.5rem;
        background: rgba(26, 0, 51, 0.3);
        border-radius: 12px;
        border: 1px solid rgba(167, 66, 255, 0.2);
    }

    .nav-pill {
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        color: var(--text-light);
    }

    .nav-pill:hover {
        color: var(--primary-color);
        text-shadow: 0 0 10px rgba(167, 66, 255, 0.5);
    }

    .nav-pill.active {
        background: var(--primary-color);
        color: white;
        box-shadow: var(--neon-glow);
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
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
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.button("Create an account"):
        st.session_state.auth_page = 'signup'
        st.rerun()

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
                    st.rerun()
                else:
                    st.error(response.json().get('error', 'Could not create account'))
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.button("Back to login"):
        st.session_state.auth_page = 'login'
        st.rerun()

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
                st.session_state.user_info = {'name': 'Guest', 'role': 'Visitor'}
                st.session_state.page = 'landing'
                st.rerun()

        # Show back button if not on landing page
        if st.session_state.page != 'landing':
            if st.button("← Back to Landing Page"):
                st.session_state.page = 'landing'
                st.rerun()

        # Main content
        if st.session_state.page == 'landing':
            # Profile section
            user_name = st.session_state.user_info.get('name', 'Guest')
            user_role = st.session_state.user_info.get('role', 'Visitor')
            
            st.markdown(f"""
                <div class="profile-container">
                    <div class="profile-avatar">{user_name[0]}</div>
                    <div>
                        <h3>{user_name}</h3>
                        <p>{user_role}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Stats section
            st.markdown("""
                <div class="stats-container">
                    <div class="stat-card">
                        <div class="stat-number">12</div>
                        <p>Total Meetings</p>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">5</div>
                        <p>Pending Requests</p>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">7</div>
                        <p>Completed</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

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
                if st.button("Request Meeting", key="request_btn", type="primary"):
                    st.session_state.page = 'request'
                    st.rerun()
            
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
                    st.rerun()

        elif st.session_state.page == 'request':
            st.markdown("""
                <div class="form-container">
                    <div class="form-header">
                        <h1>Create Meeting Request</h1>
                        <p>Fill in the details below to schedule your meeting</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Create tabs using columns
            tab1, tab2, tab3 = st.columns(3)
            
            with tab1:
                if st.button("Meeting Details", use_container_width=True, 
                           type="primary" if st.session_state.active_tab == "Meeting Details" else "secondary"):
                    st.session_state.active_tab = "Meeting Details"
                    st.rerun()
            
            with tab2:
                if st.button("Preferences", use_container_width=True,
                           type="primary" if st.session_state.active_tab == "Preferences" else "secondary"):
                    st.session_state.active_tab = "Preferences"
                    st.rerun()
            
            with tab3:
                if st.button("Review", use_container_width=True,
                           type="primary" if st.session_state.active_tab == "Review" else "secondary"):
                    st.session_state.active_tab = "Review"
                    st.rerun()

            # Show different content based on active tab
            if st.session_state.active_tab == "Meeting Details":
                with st.form("meeting_request_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
                        team_agent = st.selectbox(
                            "Select Team Agent",
                            ["Frontend", "Backend", "HR", "Marketing", "Sales", "Support"],
                            help="Choose the team you want to meet with"
                        )
                        meeting_link = st.text_input(
                            "Meeting Link",
                            placeholder="https://meet.google.com/...",
                            help="Paste your Google Meet or Zoom link here"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
                        meeting_goal = st.text_area(
                            "Meeting Goal",
                            placeholder="Describe the primary objective of this meeting...",
                            help="What do you hope to achieve in this meeting?"
                        )
                        prompt_text = st.text_area(
                            "Perpetual Question",
                            placeholder="What specific questions or topics would you like to discuss?",
                            help="List the key questions you need answered"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    submitted = st.form_submit_button("📅 Schedule Meeting", use_container_width=True)
                    
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
                                    st.rerun()
                                else:
                                    st.error(f"Failed to submit meeting request: {response.json().get('error', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

            elif st.session_state.active_tab == "Preferences":
                st.write("Preferences settings coming soon!")
            
            else:  # Review tab
                st.write("Review your meeting details here!")

        else:  # Response page
            st.title("Meeting Requests Dashboard")
            
            if st.button("🔄 Refresh"):
                st.rerun()
            
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
                                        st.rerun()
                                with col2:
                                    if st.button("Reject", key=f"reject_{meeting['_id']}"):
                                        requests.put(
                                            f"{API_BASE_URL}/meetings/{meeting['_id']}",
                                            json={"status": "rejected"},
                                            headers=headers
                                        )
                                        st.rerun()
                                with col3:
                                    if st.button("Mark Pending", key=f"pending_{meeting['_id']}"):
                                        requests.put(
                                            f"{API_BASE_URL}/meetings/{meeting['_id']}",
                                            json={"status": "pending"},
                                            headers=headers
                                        )
                                        st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 