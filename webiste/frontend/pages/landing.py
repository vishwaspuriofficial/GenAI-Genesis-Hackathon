import streamlit as st

def show_landing_page():
    """Show the main landing page with profile, stats, and navigation options"""
    # Profile section
    user_name = st.session_state.user_info.get('name', 'Guest')
    user_role = st.session_state.user_info.get('role', 'Visitor')
    
    st.markdown(f"""
        <div class="profile-container">
            <div class="profile-avatar">{user_name[0]}</div>
            <div>
                <h3 style="font-size: 1.4rem; font-weight: 600; margin-bottom: 0.3rem;">{user_name}</h3>
                <p style="color: var(--text-light); font-size: 1rem; display: flex; align-items: center;">
                    <span style="display: inline-block; height: 8px; width: 8px; background: var(--success); border-radius: 50%; margin-right: 0.5rem;"></span>
                    {user_role}
                </p>
            </div>
            <div style="margin-left: auto; padding: 0.5rem 1rem; background: rgba(157, 78, 221, 0.1); border-radius: 50px; font-size: 0.9rem;">
                <span style="color: var(--text-light);">Status:</span> 
                <span style="color: var(--success); font-weight: 500;">Active</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Stats section
    st.markdown("""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">12</div>
                <p style="color: var(--text-light); font-size: 1.1rem; font-weight: 500;">Total Meetings</p>
                <div style="height: 4px; width: 40px; background: var(--gradient-purple); margin-top: 1rem; border-radius: 2px;"></div>
            </div>
            <div class="stat-card">
                <div class="stat-number">5</div>
                <p style="color: var(--text-light); font-size: 1.1rem; font-weight: 500;">Pending Requests</p>
                <div style="height: 4px; width: 40px; background: linear-gradient(90deg, var(--warning), var(--primary-color)); margin-top: 1rem; border-radius: 2px;"></div>
            </div>
            <div class="stat-card">
                <div class="stat-number">7</div>
                <p style="color: var(--text-light); font-size: 1.1rem; font-weight: 500;">Completed</p>
                <div style="height: 4px; width: 40px; background: linear-gradient(90deg, var(--success), var(--secondary-color)); margin-top: 1rem; border-radius: 2px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Welcome header
    st.markdown("""
        <h1 style="text-align: center; margin-bottom: 2rem;">Welcome to the Meeting Request System</h1>
        <p style="text-align: center; margin-bottom: 3rem;">Choose your action below</p>
    """, unsafe_allow_html=True)
    
    # Action cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="landing-card">
                <div style="font-size: 3.5rem; margin-bottom: 1.5rem; background: linear-gradient(135deg, var(--success), var(--secondary-color)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">📅</div>
                <h2 style="font-size: 1.8rem; margin-bottom: 1.25rem; background: linear-gradient(135deg, var(--success), var(--secondary-color)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Request a Meeting</h2>
                <p style="color: var(--text-light); margin-bottom: 2rem; font-size: 1.1rem; line-height: 1.6;">
                    Need to schedule a meeting with a team agent? Submit your request with all the necessary details and we'll take care of the rest.
                </p>
                <div class="card-highlight" style="height: 4px; width: 50px; background: linear-gradient(90deg, var(--success), var(--secondary-color)); margin: 0 auto 2rem;"></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Request Meeting", key="request_btn", type="primary"):
            st.session_state.page = 'request'
            st.rerun()
    
    with col2:
        st.markdown("""
            <div class="landing-card">
                <div style="font-size: 3.5rem; margin-bottom: 1.5rem; background: var(--gradient-purple); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">⚙️</div>
                <h2 style="font-size: 1.8rem; margin-bottom: 1.25rem; background: var(--gradient-purple); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Respond to Requests</h2>
                <p style="color: var(--text-light); margin-bottom: 2rem; font-size: 1.1rem; line-height: 1.6;">
                    Team agent? Access all meeting requests, review details, and respond to them from your comprehensive dashboard.
                </p>
                <div class="card-highlight" style="height: 4px; width: 50px; background: var(--gradient-purple); margin: 0 auto 2rem;"></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Requests", key="response_btn"):
            st.session_state.page = 'response'
            st.rerun() 