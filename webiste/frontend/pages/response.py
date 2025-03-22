import streamlit as st
import requests
from utils.common import API_BASE_URL

def show_response_page():
    """Show the meeting requests dashboard"""
    st.title("Meeting Requests Dashboard")
    st.caption("Review and respond to meeting requests")
    
    if st.button("🔄 Refresh"):
        st.rerun()
    
    try:
        load_and_display_meetings()
    except Exception as e:
        st.error(f"Error: {str(e)}")

def load_and_display_meetings():
    """Load and display meeting requests"""
    if "token" not in st.session_state or not st.session_state.token:
        st.error("You must be logged in to view this page.")
        return
        
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_BASE_URL}/meetings", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        meetings = data.get('meetings', [])
        
        if not meetings:
            display_empty_state()
        else:
            display_meetings(meetings, headers)
    else:
        st.error(f"Failed to load meetings: {response.status_code}")

def display_empty_state():
    """Display a message when there are no meetings"""
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 📭 No Meeting Requests")
            st.write("There are currently no meeting requests in the system.")

def display_meetings(meetings, headers):
    """Display a list of meeting requests"""
    current_user_role = st.session_state.user_info.get('role', '')
    
    for meeting in meetings:
        with st.container():
            # Create header with requester name and status
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{meeting.get('requester_name', 'Unknown')}'s Request")
            with col2:
                status = meeting.get('status', 'pending')
                if status == "pending":
                    st.markdown("#### :orange[PENDING]")
                elif status == "accepted":
                    st.markdown("#### :green[ACCEPTED]")
                elif status == "declined":
                    st.markdown("#### :red[DECLINED]")
                elif status == "completed":
                    st.markdown("#### :blue[COMPLETED]")
                else:
                    st.markdown(f"#### {status.upper()}")
            
            # Meeting details in an expander
            with st.expander(f"{meeting.get('title', 'No Title')} - {meeting.get('date', 'No Date')} at {meeting.get('time', 'No Time')}"):
                # Description section
                st.markdown("**Description:**")
                st.code(meeting.get('description', 'No description provided'), language=None)
                
                # Meeting details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Team Agent:** {meeting.get('team_agent', 'No team specified')}")
                with col2:
                    st.markdown(f"**Duration:** {meeting.get('duration', '0')} minutes")
                
                # Attachments section
                st.markdown("**Attachments:**")
                attachments = meeting.get('attachments', [])
                if attachments:
                    for attachment in attachments:
                        filename = attachment.get('filename', 'Unknown file')
                        file_url = attachment.get('file_url', '')
                        if file_url:
                            st.markdown(f"[{filename}]({file_url})")
                else:
                    st.code("No attachments", language=None)
                
                # Display response form for team agent
                if current_user_role == meeting.get('team_agent', ''):
                    display_response_form(meeting, headers)
            
            st.divider()

def display_response_form(meeting, headers):
    """Display response form for a meeting request"""
    meeting_id = meeting.get('id')
    current_status = meeting.get('status', 'pending')
    current_response = meeting.get('response', '')
    
    with st.form(key=f"response_form_{meeting_id}"):
        st.write("Update meeting status:")
        status = st.radio(
            "Status",
            ["pending", "accepted", "declined", "completed"],
            index=["pending", "accepted", "declined", "completed"].index(current_status) if current_status in ["pending", "accepted", "declined", "completed"] else 0,
            horizontal=True
        )
        
        st.markdown("### Your Response")
        response_text = st.text_area(
            "Response message:", 
            value=current_response,
            height=100,
            placeholder="Enter your response here..."
        )
        
        submitted = st.form_submit_button("Submit Response")
        
        if submitted:
            update_meeting(meeting_id, status, response_text, headers)

def update_meeting(meeting_id, status, response, headers):
    """Update the status and response of a meeting request"""
    try:
        data = {}
        if status:
            data["status"] = status
        if response:
            data["response"] = response
            
        response = requests.put(
            f"{API_BASE_URL}/meetings/{meeting_id}",
            json=data,
            headers=headers
        )
        if response.status_code == 200:
            st.success("Meeting updated successfully")
            st.rerun()
        else:
            st.error(f"Failed to update meeting: {response.json().get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}") 