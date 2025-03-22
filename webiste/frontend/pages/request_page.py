import streamlit as st
import requests
import base64

API_BASE_URL = "http://localhost:5000/api"

def show_request_page():
    # Back button
    if st.button("← Back to Home"):
        st.session_state.page = 'landing'
        st.experimental_rerun()
    
    st.markdown('<h1 style="margin-bottom: 2rem;">Create Meeting Request</h1>', unsafe_allow_html=True)
    
    # Main form in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    with st.form("meeting_request_form"):
        st.markdown('<h3>Meeting Details</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            requester_name = st.text_input("Your Name")
            team_agent = st.selectbox(
                "Select Team Agent",
                ["Agent 1", "Agent 2", "Agent 3", "Agent 4"]
            )
            meeting_link = st.text_input("Meeting Link")
        
        with col2:
            meeting_goal = st.text_area("Meeting Goal", height=132)
        
        st.markdown('<h3 style="margin-top: 1.5rem;">Prompt Information</h3>', unsafe_allow_html=True)
        prompt_file = st.file_uploader("Upload Prompt File", type=['txt'])
        
        col1, col2 = st.columns([3, 1])
        with col2:
            submitted = st.form_submit_button("Submit Request")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if submitted:
        if not requester_name or not meeting_goal or not meeting_link:
            st.error("Please fill in all required fields")
            return
            
        if prompt_file is None:
            st.error("Please upload a prompt file")
            return
            
        # Convert file content to base64 string
        prompt_content = base64.b64encode(prompt_file.read()).decode()
        
        data = {
            "team_agent": team_agent,
            "prompt_file": prompt_content,
            "meeting_goal": meeting_goal,
            "meeting_link": meeting_link,
            "requester_name": requester_name
        }
        
        try:
            with st.spinner("Submitting your request..."):
                response = requests.post(f"{API_BASE_URL}/meetings", json=data)
            
            if response.status_code == 200:
                st.success("Meeting request submitted successfully!")
                
                # Show success card
                st.markdown("""
                    <div class="card" style="background-color: #e6fff2; border-color: #a3e9c1;">
                        <h3 style="color: #28a745;">Request Submitted!</h3>
                        <p>Your meeting request has been submitted successfully. The team agent will review your request and respond soon.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Failed to submit meeting request")
        except Exception as e:
            st.error(f"Error: {str(e)}") 