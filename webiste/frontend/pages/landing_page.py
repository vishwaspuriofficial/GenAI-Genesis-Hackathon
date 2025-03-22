import streamlit as st

def show_landing_page():
    st.markdown("""
        <div style="text-align: center; margin: 2rem 0 4rem 0;">
            <h1 style="font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(90deg, #FF416C, #FF4B2B); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Welcome to the Meeting Request System
            </h1>
            <p style="font-size: 1.2rem; color: #E0E0E0; margin-bottom: 2rem;">
                Choose your role to get started with the meeting management system
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="landing-card">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔧</div>
                <h2 style="color: #FF416C; margin-bottom: 1rem;">Request a Meeting</h2>
                <p style="color: #E0E0E0; margin-bottom: 2rem;">
                    Need to schedule a meeting with a team agent? Submit your request with all the necessary details 
                    and we'll process it for you.
                </p>
                <button class="stButton primary-btn" style="width: 100%;" id="request-btn">
                    Request Meeting
                </button>
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
                    Team agent? Access all meeting requests, review details, and respond to them from your 
                    personalized dashboard.
                </p>
                <button class="stButton primary-btn" style="width: 100%;" id="response-btn">
                    View Requests
                </button>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Requests", key="response_btn"):
            st.session_state.page = 'response'
            st.experimental_rerun() 