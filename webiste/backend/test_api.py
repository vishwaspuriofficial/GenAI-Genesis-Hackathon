"""
Test script for API endpoints
"""
import requests
import json
import os
import time
import random
import string

# API Base URL
API_BASE_URL = "http://localhost:8000/api"

# Test user credentials
TEST_USER = {
    "name": "Test User",
    "email": f"test_{random.randint(1000, 9999)}@example.com",
    "password": "password123",
    "role": "Frontend"
}

# Global variables for test data
token = None
user_id = None
meeting_id = None
file_url = None

# Test files directory
TEST_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files')

# Create test files directory if it doesn't exist
if not os.path.exists(TEST_FILES_DIR):
    os.makedirs(TEST_FILES_DIR)

# Create a test file
TEST_FILE_PATH = os.path.join(TEST_FILES_DIR, 'test_document.txt')
with open(TEST_FILE_PATH, 'w') as f:
    f.write("This is a test document for the API testing.")

def print_separator(title):
    """Print a separator with a title"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def test_signup():
    """Test the signup endpoint"""
    global user_id
    
    print_separator("TESTING SIGNUP")
    
    print(f"Signing up with email: {TEST_USER['email']}")
    response = requests.post(
        f"{API_BASE_URL}/auth/signup",
        json=TEST_USER
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201, "Signup failed"
    user_id = response.json().get('user_id')
    assert user_id is not None, "User ID not returned"
    
    print(f"Successfully signed up with user ID: {user_id}")
    return True

def test_login():
    """Test the login endpoint"""
    global token
    
    print_separator("TESTING LOGIN")
    
    print(f"Logging in with email: {TEST_USER['email']}")
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={
            "email": TEST_USER['email'],
            "password": TEST_USER['password']
        }
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, "Login failed"
    token = response.json().get('token')
    assert token is not None, "Token not returned"
    
    print(f"Successfully logged in with token: {token[:20]}...")
    return True

def test_create_meeting():
    """Test creating a meeting"""
    global meeting_id
    
    print_separator("TESTING CREATE MEETING")
    
    # Create a test meeting
    meeting_data = {
        "title": "Test Meeting",
        "description": "This is a test meeting created by the API test script",
        "date": "2025-12-31",
        "time": "14:00",
        "duration": 60,
        "team_agent": "Backend"
    }
    
    print(f"Creating meeting with title: {meeting_data['title']}")
    response = requests.post(
        f"{API_BASE_URL}/meetings",
        json=meeting_data,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201, "Creating meeting failed"
    meeting_id = response.json().get('meeting_id')
    assert meeting_id is not None, "Meeting ID not returned"
    
    print(f"Successfully created meeting with ID: {meeting_id}")
    return True

def test_get_meetings():
    """Test getting meetings"""
    print_separator("TESTING GET MEETINGS")
    
    print("Getting all meetings")
    response = requests.get(
        f"{API_BASE_URL}/meetings",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response (first few meetings): {json.dumps(response.json()['meetings'][:2], indent=2) if response.status_code == 200 and len(response.json().get('meetings', [])) > 0 else response.json()}")
    
    assert response.status_code == 200, "Getting meetings failed"
    meetings = response.json().get('meetings')
    assert meetings is not None, "Meetings not returned"
    
    print(f"Successfully retrieved {len(meetings)} meetings")
    return True

def test_get_meeting_by_id():
    """Test getting a specific meeting by ID"""
    print_separator("TESTING GET MEETING BY ID")
    
    print(f"Getting meeting with ID: {meeting_id}")
    response = requests.get(
        f"{API_BASE_URL}/meetings/{meeting_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.json()}")
    
    assert response.status_code == 200, "Getting meeting by ID failed"
    meeting = response.json().get('meeting')
    assert meeting is not None, "Meeting not returned"
    assert meeting['id'] == meeting_id, "Meeting ID doesn't match"
    
    print(f"Successfully retrieved meeting with ID: {meeting_id}")
    return True

def test_update_meeting():
    """Test updating a meeting"""
    print_separator("TESTING UPDATE MEETING")
    
    # Update the meeting status
    update_data = {
        "status": "confirmed"
    }
    
    print(f"Updating meeting with ID {meeting_id} to status: {update_data['status']}")
    response = requests.put(
        f"{API_BASE_URL}/meetings/{meeting_id}",
        json=update_data,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, "Updating meeting failed"
    
    # Verify the update
    response = requests.get(
        f"{API_BASE_URL}/meetings/{meeting_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    assert response.status_code == 200, "Getting updated meeting failed"
    updated_meeting = response.json().get('meeting')
    assert updated_meeting['status'] == update_data['status'], "Meeting status not updated"
    
    print(f"Successfully updated meeting with ID: {meeting_id}")
    return True

def test_upload_file():
    """Test uploading a file to a meeting"""
    global file_url
    
    print_separator("TESTING FILE UPLOAD")
    
    # Upload a test file
    print(f"Uploading file to meeting with ID: {meeting_id}")
    with open(TEST_FILE_PATH, 'rb') as f:
        response = requests.post(
            f"{API_BASE_URL}/meetings/upload/{meeting_id}",
            files={
                "file": (os.path.basename(TEST_FILE_PATH), f, "text/plain")
            },
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, "Uploading file failed"
    file_url = response.json().get('file_url')
    assert file_url is not None, "File URL not returned"
    
    # Verify the file was added to the meeting
    response = requests.get(
        f"{API_BASE_URL}/meetings/{meeting_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    assert response.status_code == 200, "Getting meeting with attachments failed"
    meeting = response.json().get('meeting')
    attachments = meeting.get('attachments', [])
    assert len(attachments) > 0, "Attachment not added to meeting"
    assert any(a.get('file_url') == file_url for a in attachments), "Uploaded file not found in attachments"
    
    print(f"Successfully uploaded file with URL: {file_url}")
    return True

def test_delete_attachment():
    """Test deleting an attachment from a meeting"""
    print_separator("TESTING DELETE ATTACHMENT")
    
    if not file_url:
        print("Skipping test because no file was uploaded")
        return True
    
    print(f"Deleting file with URL: {file_url} from meeting with ID: {meeting_id}")
    response = requests.delete(
        f"{API_BASE_URL}/meetings/attachment/{meeting_id}",
        params={
            "file_url": file_url
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, "Deleting attachment failed"
    
    # Verify the attachment was removed
    response = requests.get(
        f"{API_BASE_URL}/meetings/{meeting_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    assert response.status_code == 200, "Getting meeting after attachment deletion failed"
    meeting = response.json().get('meeting')
    attachments = meeting.get('attachments', [])
    assert not any(a.get('file_url') == file_url for a in attachments), "Attachment not deleted from meeting"
    
    print(f"Successfully deleted attachment from meeting with ID: {meeting_id}")
    return True

def cleanup():
    """Clean up test files"""
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
    
    if os.path.exists(TEST_FILES_DIR) and not os.listdir(TEST_FILES_DIR):
        os.rmdir(TEST_FILES_DIR)

def run_all_tests():
    """Run all tests in sequence"""
    try:
        test_signup()
        test_login()
        test_create_meeting()
        test_get_meetings()
        test_get_meeting_by_id()
        test_update_meeting()
        test_upload_file()
        test_delete_attachment()
        
        print_separator("ALL TESTS PASSED")
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False
    finally:
        cleanup()

if __name__ == "__main__":
    # Ensure the backend server is running before executing tests
    print("Make sure the backend server is running at http://localhost:8000")
    print("Press Enter to start the tests or Ctrl+C to cancel...")
    try:
        input()
        run_all_tests()
    except KeyboardInterrupt:
        print("\nTests cancelled by user")