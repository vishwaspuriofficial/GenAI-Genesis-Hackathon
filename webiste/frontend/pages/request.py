import streamlit as st
import requests
import json
import time
import pandas as pd
from utils.common import API_BASE_URL, ROLES

# Define file types to be uploaded
ALLOWED_FILE_TYPES = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png']

def show_request_page():
    """Show the meeting request form with tabs for different sections"""
    st.markdown("""
        <div class="form-container">
            <div class="form-header">
                <h1 class="form-title">Create Meeting Request</h1>
                <p class="form-description">Fill in the details below to schedule your meeting</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session states for form data if not present
    if 'meeting_data' not in st.session_state:
        st.session_state.meeting_data = {
            'title': '',
            'description': '',
            'date': '',
            'time': '',
            'duration': 30,
            'team_agent': ROLES[0],
            'meeting_link': ''
        }
    
    if 'meeting_files' not in st.session_state:
        st.session_state.meeting_files = []
    
    # Create tabs using columns
    tab1, tab2, tab3 = st.columns(3)
    
    with tab1:
        if st.button("Meeting Details", use_container_width=True, 
                   type="primary" if st.session_state.active_tab == "Meeting Details" else "secondary"):
            st.session_state.active_tab = "Meeting Details"
            st.rerun()
    
    with tab2:
        if st.button("Attachments", use_container_width=True,
                   type="primary" if st.session_state.active_tab == "Attachments" else "secondary"):
            st.session_state.active_tab = "Attachments"
            st.rerun()
    
    with tab3:
        if st.button("Review", use_container_width=True,
                   type="primary" if st.session_state.active_tab == "Review" else "secondary"):
            st.session_state.active_tab = "Review"
            st.rerun()

    # Show different content based on active tab
    if st.session_state.active_tab == "Meeting Details":
        show_meeting_details_form()
    elif st.session_state.active_tab == "Attachments":
        show_attachments_form()
    else:  # Review tab
        show_review_form()

def show_meeting_details_form():
    """Show the meeting details form"""
    # Create a styled form
    with st.form(key="meeting_details_form"):
        st.subheader("Meeting Details")
        
        # Title
        title = st.text_input(
            "Meeting Title",
            value=st.session_state.meeting_data.get('title', ''),
            placeholder="E.g., Project Kickoff Meeting",
            help="A descriptive title for the meeting"
        )
        
        # Date and time
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input(
                "Date",
                value=None if not st.session_state.meeting_data.get('date') else st.session_state.meeting_data.get('date')
            )
        
        with col2:
            time = st.time_input(
                "Time",
                value=None if not st.session_state.meeting_data.get('time') else st.session_state.meeting_data.get('time')
            )
        
        with col3:
            duration = st.number_input(
                "Duration (minutes)",
                min_value=15,
                max_value=180,
                value=st.session_state.meeting_data.get('duration', 30),
                step=15
            )
        
        # Meeting link
        meeting_link = st.text_input(
            "Meeting Link (Zoom, Teams, etc.)",
            value=st.session_state.meeting_data.get('meeting_link', ''),
            placeholder="https://zoom.us/j/123456789",
            help="Provide a link for participants to join the meeting"
        )
        
        # Get user's current role
        current_user_role = st.session_state.user_info.get('role', '')
        
        # Filter out the user's own role from available teams
        available_teams = [role for role in ROLES if role.lower() != current_user_role.lower()]
        
        # Display a message about not being able to select own team
        st.info("You cannot select your own team. The dropdown below shows only other teams.")
        
        # Team agent selection with filtered options
        team_agent = st.selectbox(
            "Select Team",
            available_teams,
            index=0,
            help="Choose the team you want to meet with (you cannot select your own team)"
        )
        
        # Description
        description = st.text_area(
            "Meeting Description",
            value=st.session_state.meeting_data.get('description', ''),
            placeholder="Describe the purpose and goals of this meeting...",
            height=150,
            help="Provide details about what you want to discuss"
        )
        
        # Submit button
        submitted = st.form_submit_button(
            label="Save & Continue to Attachments",
            use_container_width=True
        )
        
        # Handle form submission
        if submitted:
            # Validate form
            if not all([title, description, date, time]):
                st.error("Please fill in all required fields")
            else:
                # Update session state with form data
                st.session_state.meeting_data.update({
                    'title': title,
                    'description': description,
                    'date': date,
                    'time': time.strftime("%H:%M"),
                    'duration': duration,
                    'team_agent': team_agent,
                    'meeting_link': meeting_link
                })
                
                # Navigate to next tab
                st.session_state.active_tab = "Attachments"
                st.rerun()

def show_attachments_form():
    """Show form for uploading attachments"""
    # Initialize meeting_files in session state if not present
    if 'meeting_files' not in st.session_state:
        st.session_state.meeting_files = []
    
    st.subheader("Upload Meeting Materials")
    st.write("You can attach relevant documents, presentations, or images to share with the team.")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Files", 
        type=ALLOWED_FILE_TYPES,
        help=f"Allowed file types: {', '.join(ALLOWED_FILE_TYPES)}"
    )
    
    # Add file button
    if uploaded_file is not None:
        # Check if file already exists by name
        file_names = [f['name'] for f in st.session_state.meeting_files]
        if uploaded_file.name in file_names:
            st.warning(f"File '{uploaded_file.name}' is already uploaded. Please select a different file.")
        else:
            if st.button("Add File"):
                # Add file to session state
                st.session_state.meeting_files.append({
                    'name': uploaded_file.name,
                    'type': uploaded_file.type,
                    'data': uploaded_file.getvalue(),
                    'size': len(uploaded_file.getvalue())
                })
                st.success(f"File '{uploaded_file.name}' added successfully!")
                st.rerun()
    
    # Display uploaded files
    if st.session_state.meeting_files:
        st.subheader("Uploaded Files")
        
        # Create a table of uploaded files
        file_data = []
        for i, file in enumerate(st.session_state.meeting_files):
            file_data.append({
                "Name": file['name'],
                "Type": file['type'],
                "Size": f"{file['size'] / 1024:.1f} KB",
                "Remove": f"remove_{i}"
            })
        
        # Display as table
        df = pd.DataFrame(file_data)
        st.table(df[["Name", "Type", "Size"]])
        
        # Remove buttons
        cols = st.columns(min(len(st.session_state.meeting_files), 4))
        for i, col in enumerate(cols):
            if i < len(st.session_state.meeting_files):
                with col:
                    if st.button(f"Remove {st.session_state.meeting_files[i]['name']}", key=f"remove_{i}"):
                        del st.session_state.meeting_files[i]
                        st.rerun()
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Meeting Details"):
            st.session_state.active_tab = "Meeting Details"
            st.rerun()
    with col2:
        if st.button("Continue to Review →"):
            st.session_state.active_tab = "Review"
            st.rerun()

def show_review_form():
    """Show the review form and submit the meeting request"""
    st.subheader("Review Meeting Request")
    
    # Display meeting details
    st.markdown("### Meeting Details")
    st.markdown(f"**Title:** {st.session_state.meeting_data.get('title', 'Not specified')}")
    st.markdown(f"**Date:** {st.session_state.meeting_data.get('date', 'Not specified')}")
    st.markdown(f"**Time:** {st.session_state.meeting_data.get('time', 'Not specified')}")
    st.markdown(f"**Duration:** {st.session_state.meeting_data.get('duration', 'Not specified')} minutes")
    st.markdown(f"**Team:** {st.session_state.meeting_data.get('team_agent', 'Not specified')}")
    
    # Display meeting link if available
    meeting_link = st.session_state.meeting_data.get('meeting_link', '')
    if meeting_link:
        st.markdown(f"**Meeting Link:** [{meeting_link}]({meeting_link})")
    else:
        st.markdown("**Meeting Link:** Not specified")
        
    st.markdown(f"**Description:**")
    st.markdown(f"```\n{st.session_state.meeting_data.get('description', 'Not specified')}\n```")
    
    # Display files
    if st.session_state.meeting_files:
        st.markdown("### Attachments")
        for file in st.session_state.meeting_files:
            st.markdown(f"- {file['name']} ({file['size'] / 1024:.1f} KB)")
    
    # Navigation and submission buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Edit Request"):
            st.session_state.active_tab = "Meeting Details"
            st.rerun()
    
    with col2:
        if st.button("Submit Request", type="primary"):
            submit_meeting_request()

def submit_meeting_request():
    """Submit the meeting request to the API"""
    if not st.session_state.token:
        st.error("You must be logged in to submit a meeting request")
        return
    
    with st.spinner("Submitting meeting request..."):
        try:
            # First create the meeting
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            meeting_data = {
                "title": st.session_state.meeting_data.get('title'),
                "description": st.session_state.meeting_data.get('description'),
                "date": str(st.session_state.meeting_data.get('date')),
                "time": st.session_state.meeting_data.get('time'),
                "duration": st.session_state.meeting_data.get('duration'),
                "team_agent": st.session_state.meeting_data.get('team_agent'),
                "meeting_link": st.session_state.meeting_data.get('meeting_link')
            }
            
            # Create meeting request
            response = requests.post(
                f"{API_BASE_URL}/meetings",
                json=meeting_data,
                headers=headers
            )
            
            if response.status_code == 201:
                meeting_id = response.json().get('meeting_id')
                
                # Upload attachments if any
                upload_success = True
                if st.session_state.meeting_files:
                    for file in st.session_state.meeting_files:
                        upload_response = upload_file(meeting_id, file, headers)
                        if not upload_response:
                            upload_success = False
                
                # Show success message
                st.success("Meeting request submitted successfully!")
                
                if not upload_success:
                    st.warning("Some attachments could not be uploaded. The meeting was created but you may need to add attachments later.")
                
                # Clear session state
                st.session_state.meeting_data = {}
                st.session_state.meeting_files = []
                st.session_state.active_tab = "Meeting Details"
                
                # Redirect to landing page after 2 seconds
                time.sleep(2)
                st.session_state.page = 'landing'
                st.rerun()
            else:
                st.error(f"Failed to submit meeting request: {response.json().get('message', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"Error submitting meeting request: {str(e)}")

def upload_file(meeting_id, file, headers):
    """Upload a file attachment to a meeting"""
    try:
        files = {
            'file': (file['name'], file['data'], file['type'])
        }
        
        response = requests.post(
            f"{API_BASE_URL}/meetings/upload/{meeting_id}",
            files=files,
            headers=headers
        )
        
        return response.status_code == 200
    
    except Exception as e:
        st.error(f"Error uploading file {file['name']}: {str(e)}")
        return False

# Import pandas for the table display
import pandas as pd 