import streamlit as st
import requests
from utils.common import API_BASE_URL

def show_response_page():
    """Show the meeting requests dashboard"""
    st.markdown("""
        <h1 class="dashboard-card-title">Meeting Requests Dashboard</h1>
        <p class="form-description">Review and respond to meeting requests</p>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh"):
        st.rerun()
    
    try:
        load_and_display_meetings()
    except Exception as e:
        st.error(f"Error: {str(e)}")

def load_and_display_meetings():
    """Load and display meeting requests"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_BASE_URL}/meetings", headers=headers)
    meetings = response.json()
    
    if not meetings:
        display_empty_state()
    else:
        display_meetings(meetings, headers)

def display_empty_state():
    """Display a message when there are no meetings"""
    st.markdown("""
        <div class="dashboard-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <h2>No Meeting Requests</h2>
            <p>There are currently no meeting requests in the system.</p>
        </div>
    """, unsafe_allow_html=True)

def display_meetings(meetings, headers):
    """Display a list of meeting requests"""
    for meeting in meetings:
        with st.container():
            st.markdown(f"""
                <div class="dashboard-card">
                    <div class="dashboard-card-header">
                        <div class="dashboard-card-title">
                            <i>📊</i> {meeting['requester_name']}'s Request
                        </div>
                        <div class="dashboard-card-badge">
                            {meeting['status'].upper()}
                        </div>
                    </div>
                    
                    <div class="meeting-item">
                        <div class="meeting-item-header">
                            <div class="meeting-title">Team: {meeting['team_agent']}</div>
                            <div class="meeting-date">
                                <i>🔗</i> <a href="{meeting['meeting_link']}" target="_blank">{meeting['meeting_link']}</a>
                            </div>
                        </div>
                        
                        <div style="margin: 1rem 0;">
                            <p><strong>Meeting Goal:</strong></p>
                            <p style="background: rgba(60, 9, 108, 0.3); padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem;">
                                {meeting['meeting_goal']}
                            </p>
                        </div>
                        
                        <div style="margin: 1rem 0;">
                            <p><strong>Discussion Topics:</strong></p>
                            <p style="background: rgba(60, 9, 108, 0.3); padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem;">
                                {meeting['prompt_text']}
                            </p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.user_info.get('role') == 'responder':
                display_response_buttons(meeting, headers)

def display_response_buttons(meeting, headers):
    """Display response buttons for a meeting request"""
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Accept", key=f"accept_{meeting['_id']}"):
            update_meeting_status(meeting['_id'], "accepted", headers)
    with col2:
        if st.button("Reject", key=f"reject_{meeting['_id']}"):
            update_meeting_status(meeting['_id'], "rejected", headers)
    with col3:
        if st.button("Mark Pending", key=f"pending_{meeting['_id']}"):
            update_meeting_status(meeting['_id'], "pending", headers)

def update_meeting_status(meeting_id, status, headers):
    """Update the status of a meeting request"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/meetings/{meeting_id}",
            json={"status": status},
            headers=headers
        )
        if response.status_code == 200:
            st.success(f"Meeting status updated to {status}")
            st.rerun()
        else:
            st.error(f"Failed to update meeting status: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}") 