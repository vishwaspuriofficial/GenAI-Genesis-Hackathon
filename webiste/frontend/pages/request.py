import streamlit as st
import requests
import json
from utils.common import API_BASE_URL

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
        show_meeting_details_form()
    elif st.session_state.active_tab == "Preferences":
        show_preferences_form()
    else:  # Review tab
        show_review_form()

def show_meeting_details_form():
    """Show the meeting details form"""
    # Create a styled form
    with st.form(key="meeting_form"):
        st.subheader("Team & Meeting Details")
        
        # Team agent selection
        team_agent = st.selectbox(
            "Select Team Agent",
            ["Frontend", "Backend", "HR", "Marketing", "Sales", "Support"],
            help="Choose the team you want to meet with"
        )
        
        # Meeting link input
        meeting_link = st.text_input(
            "Meeting Link",
            placeholder="https://meet.google.com/...",
            help="Paste your Google Meet or Zoom link here"
        )
        
        st.subheader("Meeting Purpose")
        
        # Meeting goal
        meeting_goal = st.text_area(
            "Meeting Goal",
            placeholder="Describe the primary objective of this meeting...",
            height=120,
            help="What do you hope to achieve in this meeting?"
        )
        
        # Discussion topics
        discussion_topics = st.text_area(
            "Discussion Topics",
            placeholder="What specific questions or topics would you like to discuss?",
            height=120,
            help="List the key questions you need answered"
        )
        
        # Submit button
        submit_button = st.form_submit_button(
            label="📅 Schedule Meeting",
            use_container_width=True
        )
        
        # Handle form submission
        if submit_button:
            # Validate form
            if not all([meeting_goal, meeting_link, discussion_topics]):
                st.error("Please fill in all fields")
            else:
                # Create data dictionary
                meeting_data = {
                    "team_agent": team_agent,
                    "prompt_text": discussion_topics,
                    "meeting_goal": meeting_goal,
                    "meeting_link": meeting_link,
                    "requester_name": st.session_state.user_info['name']
                }
                
                # For development, just show success without API call
                st.success("Meeting request submitted successfully!")
                st.write("Meeting Request Details:")
                st.write(meeting_data)
                
                # In a real app, this would send the data to the API
                # Commented out for development
                """
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/meetings",
                        json=meeting_data,
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
                """

def show_preferences_form():
    """Show the meeting preferences form"""
    st.write("Preferences settings coming soon!")

def show_review_form():
    """Show the review form"""
    st.write("Review your meeting details here!") 