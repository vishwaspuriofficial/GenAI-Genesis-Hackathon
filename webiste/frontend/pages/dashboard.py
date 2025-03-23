"""
Dashboard page for viewing team-specific meeting requests
"""
import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
from utils.common import API_BASE_URL

def show_dashboard_page():
    """
    Display the dashboard for viewing team-specific meeting requests
    """
    st.title("Meeting Dashboard")
    st.caption("View and manage your meeting requests")
    
    if "token" not in st.session_state or not st.session_state.token:
        st.error("You must be logged in to view this page.")
        return
    
    # Get user info
    user_role = st.session_state.user_info.get('role', '')
    user_name = st.session_state.user_info.get('name', 'User')
    user_id = st.session_state.user_info.get('id', '')
    
    # Show user context
    st.info(f"Logged in as: {user_name} ({user_role})")
    
    # Dashboard filters sidebar
    with st.sidebar:
        st.header("Filters")
        
        view_mode = st.radio(
            "View Mode",
            options=["My Requests", "Other Team Requests", "All Requests"],
            help="Filter meetings based on your role: 'My Requests' shows requests you created, 'Other Team Requests' shows requests assigned to your team"
        )
        
        status_filter = st.multiselect(
            "Status",
            options=["pending", "accepted", "declined", "completed"],
            default=["pending", "accepted"],
            help="Filter by meeting status"
        )
        
        sort_by = st.selectbox(
            "Sort by",
            options=["Date (newest first)", "Date (oldest first)", "Status"],
            index=0,
            help="Sort meeting requests"
        )
        
        # Filter out test users option
        hide_test_users = st.checkbox("Hide Test Users", value=True, 
                                    help="Filter out requests from users with 'test' in their name or email")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Main content area
    meetings = fetch_meetings(user_role)
    
    if not meetings:
        st.warning("No meeting requests found.")
        return
    
    # Filter meetings based on view mode, status, and test users
    filtered_meetings = filter_meetings(meetings, user_role, user_id, view_mode, status_filter, hide_test_users)
    
    if not filtered_meetings:
        st.info("No meeting requests match your filter criteria.")
        return
    
    # Sort meetings
    sorted_meetings = sort_meetings(filtered_meetings, sort_by)
    
    # Display meetings summary
    display_meetings_summary(sorted_meetings)
    
    # Display a header based on view mode
    if view_mode == "My Requests":
        st.subheader("📝 My Meeting Requests")
        st.caption("Requests you've created for other teams")
    elif view_mode == "Other Team Requests":
        st.subheader("📬 Requests Assigned to Your Team")
        st.caption("Requests from other teams that need your team's attention")
    else:
        st.subheader("🗂 All Meeting Requests")
    
    # Display meetings using pure Streamlit components
    for meeting in sorted_meetings:
        display_meeting_card_pure_streamlit(meeting, user_role)

def fetch_meetings(user_role):
    """Fetch meetings from the API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/meetings",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            return response.json().get('meetings', [])
        else:
            st.error(f"Error fetching meetings: {response.json().get('message', 'Unknown error')}")
            return []
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def filter_meetings(meetings, user_role, user_id, view_mode, status_filter, hide_test_users=True):
    """Filter meetings based on view mode, status, and hide test users option"""
    filtered = []
    
    for meeting in meetings:
        # Skip test users if enabled
        if hide_test_users:
            requester_name = meeting.get('requester_name', '').lower()
            requester_email = meeting.get('requester_email', '').lower()
            if 'test' in requester_name or 'test' in requester_email:
                continue
        
        # Get meeting properties for filtering
        is_my_request = meeting.get('requester_id') == user_id
        is_for_my_team = meeting.get('team_agent') == user_role
        
        # Filter by view mode
        if view_mode == "My Requests" and not is_my_request:
            continue
        elif view_mode == "Other Team Requests" and not is_for_my_team:
            continue
        # If view_mode is "All Requests", include everything
            
        # Filter by status
        if status_filter and meeting.get('status') not in status_filter:
            continue
            
        filtered.append(meeting)
    
    return filtered

def sort_meetings(meetings, sort_by):
    """Sort meetings based on the selected criteria"""
    if sort_by == "Date (newest first)":
        return sorted(meetings, key=lambda m: m.get('date', ''), reverse=True)
    elif sort_by == "Date (oldest first)":
        return sorted(meetings, key=lambda m: m.get('date', ''))
    elif sort_by == "Status":
        # Custom status order: pending, accepted, declined, completed
        status_order = {"pending": 0, "accepted": 1, "declined": 2, "completed": 3}
        return sorted(meetings, key=lambda m: status_order.get(m.get('status', 'pending'), 99))
    
    return meetings

def display_meetings_summary(meetings):
    """Display a summary of meetings"""
    # Count meetings by status
    status_counts = {"pending": 0, "accepted": 0, "declined": 0, "completed": 0}
    for meeting in meetings:
        status = meeting.get('status', 'pending')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Create columns for status counts
    cols = st.columns(4)
    
    for i, (status, count) in enumerate(status_counts.items()):
        with cols[i]:
            st.metric(label=status.title(), value=count)
    
    st.divider()

def display_meeting_card_pure_streamlit(meeting, user_role):
    """Display a single meeting card using only Streamlit native components"""
    meeting_id = meeting.get('id')
    status = meeting.get('status', 'pending')
    is_team_agent = user_role == meeting.get('team_agent')
    is_requester = st.session_state.user_info.get('id') == meeting.get('requester_id')
    
    # Create a bordered container for each meeting
    with st.container():
        # Determine card class based on whether it's the user's own request or for their team
        card_class = "meeting-card"
        if is_requester:
            card_class += " meeting-card-own"
            indicator_class = "your-request-indicator"
            indicator_text = "🔹 Your Request"
        elif is_team_agent:
            card_class += " meeting-card-team"
            indicator_class = "team-request-indicator"
            indicator_text = "🔸 For Your Team"
        
        # Apply card styling using markdown with HTML
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # Add a visual indicator
        if is_requester or is_team_agent:
            st.markdown(f'<div class="{indicator_class}">{indicator_text}</div>', unsafe_allow_html=True)
        
        # Header row with title and status
        col1, col2 = st.columns([5, 1])
        with col1:
            st.subheader(meeting.get('title', 'No Title'))
        with col2:
            # Color-coded status indicator using HTML/CSS
            status_class = f"status-badge status-{status.lower()}"
            st.markdown(f'<div class="{status_class}">{status.upper()}</div>', unsafe_allow_html=True)
        
        # Meeting details in an expander
        with st.expander("View Meeting Details"):
            # Date and time
            st.markdown(f"📅 **Date and Time:** {meeting.get('date', 'No Date')} at {meeting.get('time', 'No Time')}")
            
            # Description section
            st.markdown("**Description:**")
            st.code(meeting.get('description', 'No description provided'), language=None)
            
            # Meeting details using columns
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Team Agent:** {meeting.get('team_agent', 'No Team')}")
            with col2:
                st.markdown(f"**Duration:** {meeting.get('duration', '30')} minutes")
            
            # Display meeting link if available
            meeting_link = meeting.get('meeting_link', '')
            if meeting_link:
                st.markdown(f"**Meeting Link:** [{meeting_link}]({meeting_link})")
            
            st.markdown(f"**Requested by:** {meeting.get('requester_name', 'Unknown')}")
            
            # Attachments section
            st.markdown("**Requester Attachments:**")
            attachments = meeting.get('attachments', [])
            if attachments:
                for attachment in attachments:
                    filename = attachment.get('filename', 'Unknown file')
                    file_url = attachment.get('file_url', '')
                    if file_url:
                        st.markdown(f"[{filename}]({file_url})")
            else:
                st.code("No attachments", language=None)
            
            # Display team response files if available
            st.markdown("**Team Response Files:**")
            response_files = meeting.get('response_files', [])
            if response_files:
                for file in response_files:
                    filename = file.get('filename', 'Unknown file')
                    file_url = file.get('file_url', '')
                    if file_url:
                        st.markdown(f"[{filename}]({file_url})")
            else:
                st.code("No team files uploaded", language=None)
            
            # Response section if available
            if meeting.get('response'):
                st.markdown("**Team Response:**")
                st.code(meeting.get('response'), language=None)
            
            # Action buttons for team agent
            if is_team_agent and status == "pending":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Accept", key=f"accept_{meeting_id}", type="primary"):
                        update_meeting_status(meeting_id, "accepted")
                        st.success("Meeting accepted!")
                        st.rerun()
                
                with col2:
                    if st.button("Decline", key=f"decline_{meeting_id}", type="secondary"):
                        update_meeting_status(meeting_id, "declined")
                        st.success("Meeting declined!")
                        st.rerun()
        
        # Close the card div
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add spacing between cards
        st.write("")

def update_meeting_status(meeting_id, status):
    """Update the status of a meeting"""
    try:
        response = requests.put(
            f"{API_BASE_URL}/meetings/{meeting_id}",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            json={"status": status}
        )
        
        if response.status_code != 200:
            st.error(f"Error updating meeting: {response.json().get('message', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def update_meeting_response(meeting_id, response):
    """Update the response of a meeting"""
    try:
        response_data = requests.put(
            f"{API_BASE_URL}/meetings/{meeting_id}",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            json={"response": response}
        )
        
        if response_data.status_code != 200:
            st.error(f"Error updating response: {response_data.json().get('message', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}") 