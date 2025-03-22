import streamlit as st
import requests
import pandas as pd
import base64
import json

API_BASE_URL = "http://localhost:5000/api"

def show_response_page():
    # Back button
    if st.button("← Back to Home"):
        st.session_state.page = 'landing'
        st.experimental_rerun()
    
    st.markdown('<h1 style="margin-bottom: 2rem;">Meeting Requests Dashboard</h1>', unsafe_allow_html=True)
    
    # Refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh"):
            st.experimental_rerun()
    
    try:
        with st.spinner("Loading meeting requests..."):
            response = requests.get(f"{API_BASE_URL}/meetings")
            meetings = response.json()
        
        if not meetings:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
                    <h2>No Meeting Requests</h2>
                    <p>There are currently no meeting requests in the system.</p>
                </div>
            """, unsafe_allow_html=True)
            return
            
        # Convert to DataFrame for better display
        df = pd.DataFrame(meetings)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Add status badges
        def format_status(status):
            if status == "pending":
                return f'<span class="status-badge status-pending">Pending</span>'
            elif status == "accepted":
                return f'<span class="status-badge status-accepted">Accepted</span>'
            else:
                return f'<span class="status-badge status-rejected">Rejected</span>'
        
        # Create a styled dataframe
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>All Meeting Requests</h3>', unsafe_allow_html=True)
        
        # Format the dataframe for display
        display_df = df.copy()
        display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        display_df = display_df[['requester_name', 'team_agent', 'meeting_goal', 'status', 'created_at']]
        display_df.columns = ['Requester', 'Team Agent', 'Meeting Goal', 'Status', 'Created At']
        
        # Display the table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show detailed view for selected meeting
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>Meeting Details</h3>', unsafe_allow_html=True)
        
        selected_meeting = st.selectbox(
            "Select a meeting to view details",
            df['_id'].tolist(),
            format_func=lambda x: f"Request from {df[df['_id']==x]['requester_name'].iloc[0]} ({df[df['_id']==x]['created_at'].iloc[0].strftime('%Y-%m-%d')})"
        )
        
        if selected_meeting:
            meeting = df[df['_id'] == selected_meeting].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                    <p><strong>Requester:</strong> {meeting['requester_name']}</p>
                    <p><strong>Team Agent:</strong> {meeting['team_agent']}</p>
                    <p><strong>Meeting Goal:</strong> {meeting['meeting_goal']}</p>
                    <p><strong>Meeting Link:</strong> <a href="{meeting['meeting_link']}" target="_blank">{meeting['meeting_link']}</a></p>
                """, unsafe_allow_html=True)
            
            with col2:
                status_class = {
                    "pending": "status-pending",
                    "accepted": "status-accepted",
                    "rejected": "status-rejected"
                }.get(meeting['status'], "status-pending")
                
                st.markdown(f"""
                    <p><strong>Status:</strong> <span class="status-badge {status_class}">{meeting['status'].capitalize()}</span></p>
                    <p><strong>Created At:</strong> {meeting['created_at'].strftime('%Y-%m-%d %H:%M')}</p>
                """, unsafe_allow_html=True)
                
                # Download prompt file
                prompt_content = base64.b64decode(meeting['prompt_file'])
                st.download_button(
                    "📄 Download Prompt File",
                    prompt_content,
                    file_name=f"prompt_{meeting['requester_name']}.txt",
                    mime="text/plain"
                )
            
            # Update status section
            st.markdown('<hr style="margin: 1.5rem 0;">', unsafe_allow_html=True)
            st.markdown('<h4>Update Request Status</h4>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Accept Request", 
                            disabled=meeting['status']=='accepted',
                            type="primary" if meeting['status']!='accepted' else "secondary"):
                    update_status(selected_meeting, "accepted")
            
            with col2:
                if st.button("❌ Reject Request", 
                            disabled=meeting['status']=='rejected',
                            type="primary" if meeting['status']!='rejected' else "secondary"):
                    update_status(selected_meeting, "rejected")
            
            with col3:
                if st.button("⏳ Mark as Pending", 
                            disabled=meeting['status']=='pending',
                            type="primary" if meeting['status']!='pending' else "secondary"):
                    update_status(selected_meeting, "pending")
        
        st.markdown('</div>', unsafe_allow_html=True)
                            
    except Exception as e:
        st.error(f"Error: {str(e)}")

def update_status(meeting_id, status):
    try:
        with st.spinner(f"Updating status to {status}..."):
            response = requests.put(
                f"{API_BASE_URL}/meetings/{meeting_id}",
                json={"status": status}
            )
        
        if response.status_code == 200:
            st.success(f"Status updated to {status} successfully!")
            st.experimental_rerun()
        else:
            st.error("Failed to update status")
    except Exception as e:
        st.error(f"Error: {str(e)}") 