from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.exceptions import HTTPException
from firebase_config import FirebaseService
from models import User, Meeting, Attachment
from werkzeug.utils import secure_filename
from functools import wraps
from config import Config
from flask_cors import CORS
import jwt
import os
import uuid
import datetime
import io
import zipfile
import json
import sys

# Add directory to path for manage_appointments.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import manage_appointments

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.secret_key = Config.SECRET_KEY

# Initialize Firebase
firebase = FirebaseService()

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


CORS(app)

# API Documentation routes
@app.route('/api-docs')
def api_docs():
    """Serve the Swagger UI documentation page"""
    return send_from_directory('.', 'swagger-ui.html')

@app.route('/openapi.yaml')
def openapi_spec():
    """Serve the OpenAPI specification file"""
    return send_from_directory('.', 'openapi.yaml')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Helper function to get the current user from the request token
def get_current_user():
    """Get the current user from the request token"""
    token = None
    # Check if token is in headers
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if ' ' in auth_header:
            token = auth_header.split(" ")[1]
        else:
            token = auth_header
    
    if not token:
        print("[DEBUG] No token found in request")
        return None
    
    try:
        # Decode the token
        data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        current_user = firebase.get_user_by_email(data['email'])
        return current_user
    except Exception as e:
        print(f"[DEBUG] Error decoding token: {str(e)}")
        return None

# Decorator for routes that require authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if token is in headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            current_user = firebase.get_user_by_email(data['email'])
            
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
                
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

# Authentication routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        print("Received signup request")
        data = request.get_json()
        print("Request data:", data)
        
        # Check if all required fields are present
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing field: {field}'}), 400
        
        # Create a new user
        user = User(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            role=data['role']
        )
        
        print("Created user object:", user.to_dict())
        
        # Add user to database
        user_id = firebase.create_user(user.to_dict())
        print("User created with ID:", user_id)
        
        return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        print("Error in signup:", e)
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Check if all required fields are present
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password required'}), 400
        
        # Get user from database
        user = firebase.get_user_by_email(data['email'])
        
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Check password
        user_obj = User(
            email=user['email'],
            password="",  # Not needed for verification
            name=user['name'],
            role=user['role']
        )
        
        if not user_obj.verify_password(user['password_hash'], data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Generate token
        token = jwt.encode({
            'email': user['email'],
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.secret_key)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
    except Exception as e:
        print("Error in login:", e)
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

# Meeting routes
@app.route('/api/meetings', methods=['POST'])
@token_required
def create_meeting(current_user):
    try:
        data = request.get_json()
        
        # Check if all required fields are present
        required_fields = ['title', 'description', 'date', 'time', 'duration', 'team_agent', 'meeting_link']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing field: {field}'}), 400
        
        # Create a new meeting
        meeting = Meeting(
            title=data['title'],
            description=data['description'],
            date=data['date'],
            time=data['time'],
            duration=data['duration'],
            requester_id=current_user['id'],
            requester_name=current_user['name'],
            requester_role=current_user['role'],
            team_agent=data['team_agent'],
            meeting_link=data['meeting_link']
        )
        
        # Add meeting to database
        meeting_id = firebase.create_meeting(meeting.to_dict())
        
        # Also add to local appointments.json file
        try:
            # Load existing appointments
            appointments = manage_appointments.load_appointments()
            
            # Add this appointment
            date_str = data['date']
            time_str = data['time']
            manage_appointments.add_appointment(appointments, date_str, time_str, meeting_id)
            
            print(f"Successfully added appointment to local file: {date_str} {time_str} -> {meeting_id}")
        except Exception as local_err:
            print(f"Warning: Could not add appointment to local file: {str(local_err)}")
        
        return jsonify({
            'message': 'Meeting created successfully',
            'meeting_id': meeting_id,
        }), 201
    except Exception as e:
        print("Error creating meeting:", e)
        return jsonify({'message': 'Error creating meeting', 'error': str(e)}), 500

@app.route('/api/meetings', methods=['GET'])
@token_required
def get_meetings(current_user):
    try:
        # Get status filter from query params
        status = request.args.get('status')
        
        # Get meetings for the user's team
        meetings = firebase.get_meetings_by_team_or_requester(current_user['role'], status)
        
        return jsonify({'meetings': meetings}), 200
    except Exception as e:
        print("Error getting meetings:", e)
        return jsonify({'message': 'Error getting meetings', 'error': str(e)}), 500

@app.route('/api/meetings/<meeting_id>', methods=['GET'])
@token_required
def get_meeting(current_user, meeting_id):
    try:
        # Get meeting from database
        meeting = firebase.get_meeting_by_id(meeting_id)
        
        if not meeting:
            return jsonify({'message': 'Meeting not found'}), 404
        
        # Check if user has permission to view this meeting
        if meeting['requester_id'] != current_user['id'] and meeting['team_agent'] != current_user['role']:
            return jsonify({'message': 'You do not have permission to view this meeting'}), 403
        
        return jsonify({'meeting': meeting}), 200
    except Exception as e:
        print("Error getting meeting:", e)
        return jsonify({'message': 'Error getting meeting', 'error': str(e)}), 500

@app.route('/api/meetings/<meeting_id>', methods=['PUT'])
@token_required
def update_meeting(current_user, meeting_id):
    try:
        data = request.get_json()
        
        # Get meeting from database
        meeting = firebase.get_meeting_by_id(meeting_id)
        
        if not meeting:
            return jsonify({'message': 'Meeting not found'}), 404
        
        # Check if user has permission to update this meeting
        if meeting['requester_id'] != current_user['id'] and meeting['team_agent'] != current_user['role']:
            return jsonify({'message': 'You do not have permission to update this meeting'}), 403
        
        # Update meeting status
        if 'status' in data:
            firebase.update_meeting_status(meeting_id, data['status'])
            
            # If status is 'canceled' or 'completed', remove from local appointments.json
            if data['status'].lower() in ['canceled', 'cancelled', 'completed']:
                try:
                    # Load appointments
                    appointments = manage_appointments.load_appointments()
                    
                    # Delete the appointment with this meeting_id
                    success = manage_appointments.delete_appointment(appointments, appointment_id=meeting_id)
                    
                    if success:
                        print(f"Successfully removed canceled/completed meeting {meeting_id} from local file")
                    else:
                        print(f"Meeting {meeting_id} not found in local appointments file")
                except Exception as local_err:
                    print(f"Warning: Could not update local appointments file: {str(local_err)}")
        
        # Update meeting response
        if 'response' in data and current_user['role'] == meeting['team_agent']:
            firebase.update_meeting_response(meeting_id, data['response'])
        
        return jsonify({'message': 'Meeting updated successfully'}), 200
    except Exception as e:
        print("Error updating meeting:", e)
        return jsonify({'message': 'Error updating meeting', 'error': str(e)}), 500

# File upload routes
@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """Upload a file to Firebase Storage"""
    print("[DEBUG] Starting /api/upload-file endpoint")
    
    # Get the current user
    current_user = get_current_user()
    if current_user is None:
        print("[DEBUG] No user is logged in for file upload")
        return jsonify({"error": "No user is logged in"}), 401
    
    # Check if user is admin or team
    is_admin = current_user.get('role') == 'admin'
    is_team = current_user.get('role') == 'team'
    
    if not is_admin and not is_team:
        print(f"[DEBUG] User {current_user.get('email')} with role {current_user.get('role')} not authorized for file upload")
        return jsonify({"error": "Not authorized"}), 403

    # Check if file was uploaded
    if 'file' not in request.files:
        print("[DEBUG] No file part in request")
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # Check if file has a name
    if file.filename == '':
        print("[DEBUG] No file selected")
        return jsonify({"error": "No file selected"}), 400
    
    meeting_id = request.form.get('meeting_id')
    print(f"[DEBUG] Uploading file for meeting_id: {meeting_id}")
    
    # If this is a team upload and we have a meeting ID, get the team_agent
    team_agent = None
    if is_team and meeting_id:
        meeting = firebase.get_meeting_by_id(meeting_id)
        if meeting:
            team_agent = meeting.get('team_agent')
            print(f"[DEBUG] Found team_agent for meeting: {team_agent}")
    
    # Save file temporarily
    temp_dir = 'uploads'
    os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(filepath)
    
    # Set folder path based on role and team_agent
    if is_admin:
        folder = "attachments"
    elif team_agent:
        folder = f"responses/{team_agent}"  # Using team_agent for organization
    else:
        folder = "responses"
        
    if meeting_id:
        folder = f"meeting_files/{meeting_id}/{folder}"
    else:
        folder = f"meeting_files/{folder}"
    
    print(f"[DEBUG] Uploading to folder: {folder}")
    
    try:
        # Upload file to Firebase Storage
        content_type = file.content_type if hasattr(file, 'content_type') else None
        url = firebase.upload_file(
            file_path=filepath, 
            filename=secure_filename(file.filename), 
            folder=folder,
            content_type=content_type
        )
        
        # Remove temporary file
        os.remove(filepath)
        
        # If this is a team upload to a meeting, add it to the meeting response files too
        if is_team and meeting_id and team_agent:
            result = firebase.add_response_file_to_meeting(
                meeting_id, 
                {
                    "filename": secure_filename(file.filename),
                    "url": url,
                    "uploaded_by": current_user.get('email'),
                    "uploaded_at": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "team": team_agent
                }
            )
            if not result:
                print("[DEBUG] Failed to update meeting with response file")
        
        print(f"[DEBUG] File uploaded successfully. URL: {url}")
        response_data = {"url": url}
        if team_agent:
            response_data["team"] = team_agent
        return jsonify(response_data), 200
    except Exception as e:
        print(f"[DEBUG] Error in file upload: {str(e)}")
        # Clean up temp file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

@app.route('/api/team-upload', methods=['POST'])
def upload_team_file():
    current_user = get_current_user()
    print(f"[DEBUG] Current user: {current_user}")
    
    # For testing only - if no user found, use a test user
    if current_user is None:
        print("[DEBUG] No user found, using test user for demo")
        current_user = {
            "id": "test-user-id",
            "email": "test@example.com",
            "role": "product"  # Default role for testing
        }
    
    # Get user's role for the folder name
    user_role = current_user.get('role')
    if not user_role:
        print(f"[DEBUG] User {current_user.get('email')} has no role")
        return jsonify({"error": "User has no assigned role"}), 400
    
    # Force user role to uppercase first letter for consistency with Firebase folders
    user_role = user_role.capitalize()
    print(f"[DEBUG] Will upload files directly to folder: {user_role}")
    
    # Check if files were uploaded
    if 'files[]' not in request.files:
        print("[DEBUG] No files part in request")
        print(f"[DEBUG] Available keys in request.files: {list(request.files.keys())}")
        return jsonify({"error": "No files part"}), 400
    
    # Handle multiple files
    files = request.files.getlist('files[]')
    if not files or len(files) == 0 or files[0].filename == '':
        print("[DEBUG] No files selected for team upload")
        return jsonify({"error": "No files selected"}), 400
        
    print(f"[DEBUG] Received {len(files)} files for upload")
    for f in files:
        print(f"[DEBUG] File: {f.filename}, Content Type: {f.content_type}")
    
    # Get optional meeting ID for metadata only
    meeting_id = request.form.get('meeting_id')
    print(f"[DEBUG] Meeting ID: {meeting_id}")
    
    temp_dir = 'uploads'
    os.makedirs(temp_dir, exist_ok=True)
    
    # Track the results
    uploaded_files = []
    error_files = []
    
    # Process each file
    for file in files:
        if file.filename == '':
            continue
            
        try:
            # Save the file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(temp_dir, filename)
            file.save(filepath)
            
            # Use the user's role directly as the folder
            folder = user_role  # Already capitalized above
            print(f"[DEBUG] Uploading to folder: {folder} - File: {filename}")
            
            # Upload to Firebase Storage
            content_type = file.content_type if hasattr(file, 'content_type') else None
            url = firebase.upload_file(
                file_path=filepath,
                filename=filename,
                folder=folder,
                content_type=content_type
            )
            
            # Remove temporary file
            os.remove(filepath)
            
            # Add to meeting document if meeting_id is provided
            if meeting_id:
                file_data = {
                    "filename": filename,
                    "url": url,
                    "uploaded_by": current_user.get('email'),
                    "uploaded_at": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "team": user_role  # Use user_role as team, maintain capitalization
                }
                result = firebase.add_response_file_to_meeting(meeting_id, file_data)
                print(f"[DEBUG] Added file to meeting document: {result}")
            
            uploaded_files.append({
                "filename": filename,
                "url": url,
                "team": user_role
            })
            print(f"[DEBUG] File {filename} uploaded successfully. URL: {url}")
                
        except Exception as e:
            print(f"[DEBUG] Error uploading file {file.filename}: {str(e)}")
            error_files.append(file.filename)
            # Clean up temp file if it exists
            if os.path.exists(filepath):
                os.remove(filepath)
    
    # Return the results
    if len(uploaded_files) > 0:
        print(f"[DEBUG] {len(uploaded_files)} files uploaded successfully, {len(error_files)} failed")
        return jsonify({
            "message": f"{len(uploaded_files)} files uploaded successfully",
            "files": uploaded_files,
            "errors": error_files
        }), 200
    else:
        print("[DEBUG] No files were successfully uploaded")
        return jsonify({"error": "No files were successfully uploaded", "errors": error_files}), 500

@app.route('/api/meetings/attachment/<meeting_id>', methods=['DELETE'])
@token_required
def delete_attachment(current_user, meeting_id):
    try:
        # Get file URL from query params
        file_url = request.args.get('file_url')
        
        if not file_url:
            return jsonify({'message': 'File URL is required'}), 400
        
        # Check if meeting exists
        meeting = firebase.get_meeting_by_id(meeting_id)
        
        if not meeting:
            return jsonify({'message': 'Meeting not found'}), 404
        
        # Check if user has permission to delete from this meeting
        if meeting['requester_id'] != current_user['id'] and meeting['team_agent'] != current_user['role']:
            return jsonify({'message': 'You do not have permission to delete from this meeting'}), 403
        
        # Remove the attachment from the meeting
        firebase.remove_attachment_from_meeting(meeting_id, file_url)
        
        # Delete the file from Firebase Storage
        firebase.delete_file(file_url)
        
        return jsonify({'message': 'File deleted successfully'}), 200
    except Exception as e:
        print("Error deleting file:", e)
        return jsonify({'message': 'Error deleting file', 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get the status of the API and Firebase connections
    """
    storage_status = "OK" if firebase.bucket is not None and not firebase.mock_mode else "MOCK"
    firestore_status = "OK" if firebase.db is not None and not firebase.mock_mode else "MOCK"
    
    bucket_name = Config.FIREBASE_STORAGE_BUCKET
    
    response_data = {
        "api": "running",
        "firebase": {
            "storage": storage_status,
            "firestore": firestore_status,
            "mock_mode": firebase.mock_mode,
            "storage_bucket": bucket_name
        },
        "upload_folder": app.config['UPLOAD_FOLDER'],
        "version": "1.0.0"
    }
    
    # Return 500 status if in mock mode, to indicate service degradation
    status_code = 200 if not firebase.mock_mode else 207
    
    return jsonify(response_data), status_code

@app.route('/api/simple-upload', methods=['POST'])
def simple_upload_file():
    """
    Simplified endpoint to upload files directly to a folder named after the user's role.
    No meeting associations, just straight to Firebase Storage.
    """
    print("[DEBUG] Starting /api/simple-upload endpoint")
    print(f"[DEBUG] Request headers: {request.headers}")
    print(f"[DEBUG] Request files: {request.files}")
    print(f"[DEBUG] Request form: {request.form}")
    
    # Get the current user
    current_user = get_current_user()
    print(f"[DEBUG] Current user: {current_user}")
    
    # For testing only - if no user found, use a test user
    if current_user is None:
        print("[DEBUG] No user found, using test user for demo")
        current_user = {
            "id": "test-user-id",
            "email": "test@example.com",
            "role": "product"  # Default role for testing
        }
    
    user_role = current_user.get('role')
    if not user_role:
        print(f"[DEBUG] User {current_user.get('email')} has no role")
        return jsonify({"error": "User has no assigned role"}), 400
    
    # Force role to be capitalized for consistency with Firebase folders
    user_role = user_role.capitalize()
    print(f"[DEBUG] Will use folder: {user_role}")
    
    # Check if file was uploaded
    if 'file' not in request.files:
        print("[DEBUG] No file part in request")
        print(f"[DEBUG] Available keys in request.files: {list(request.files.keys())}")
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # Check if file has a name
    if file.filename == '':
        print("[DEBUG] No file selected")
        return jsonify({"error": "No file selected"}), 400
    
    print(f"[DEBUG] Will upload file directly to folder: {user_role}")
    print(f"[DEBUG] File: {file.filename}, Content Type: {file.content_type if hasattr(file, 'content_type') else 'unknown'}")
    
    # Save file temporarily
    temp_dir = 'uploads'
    os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(filepath)
    
    try:
        # Upload file to Firebase Storage directly to the role folder
        content_type = file.content_type if hasattr(file, 'content_type') else None
        url = firebase.upload_file(
            file_path=filepath, 
            filename=secure_filename(file.filename), 
            folder=user_role,  # Just the role name, nothing else
            content_type=content_type
        )
        
        # Remove temporary file
        os.remove(filepath)
        
        print(f"[DEBUG] File uploaded successfully to {user_role} folder. URL: {url}")
        return jsonify({"url": url, "role": user_role}), 200
        
    except Exception as e:
        print(f"[DEBUG] Error in simple file upload: {str(e)}")
        # Clean up temp file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/meeting/earliest', methods=['GET'])
def get_earliest_meeting():
    """
    Get the earliest meeting
    """
    appointment = manage_appointments.get_earliest_meeting()
    return jsonify({"appointment": appointment})

@app.route('/api/meeting-short-info/<meeting_id>', methods=['GET'])
def get_meeting_short_info(meeting_id):
    """
    Get short meeting information by ID
    """
    meeting_info = firebase.get_meeting_short_info(meeting_id)
    return jsonify(meeting_info)

# ================================================ API CALLING FOR THE AI TEAM ================================================
# File download endpoints
@app.route('/api/files/download', methods=['GET', 'POST'])
def download_files():
    """
    Download multiple files as a ZIP archive
    
    Two methods supported:
    1. POST: Request body should be a JSON with the following format:
        {
            "file_urls": ["url1", "url2", "url3"]
        }
    
    2. GET: Query parameters should contain one or more file_url parameters:
        /api/files/download?file_url=url1&file_url=url2&file_url=url3
    
    Returns a ZIP file containing all the requested files
    """
    try:
        file_urls = []
        
        # Handle POST request with JSON body
        if request.method == 'POST':
            print("Handling POST request for file download")
            data = request.json
            if not data or 'file_urls' not in data or not isinstance(data['file_urls'], list) or len(data['file_urls']) == 0:
                return jsonify({'error': 'Request must include a "file_urls" array with at least one URL'}), 400
                
            file_urls = data['file_urls']
        
        # Handle GET request with query parameters
        elif request.method == 'GET':
            print("Handling GET request for file download")
            file_urls = request.args.getlist('file_url')
            if not file_urls or len(file_urls) == 0:
                return jsonify({'error': 'Request must include at least one "file_url" query parameter'}), 400
        
        print(f"Received request to download {len(file_urls)} files")
        for i, url in enumerate(file_urls):
            print(f"  File {i+1}: {url}")
        
        # Create a ZIP file in memory
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Add each file to the ZIP
            for i, file_url in enumerate(file_urls):
                print(f"Processing file {i+1}/{len(file_urls)}: {file_url}")
                
                # Download the file
                file_content, content_type, filename = firebase.download_file_from_url(file_url)
                
                if file_content is None:
                    print(f"Failed to download file: {file_url}")
                    continue
                    
                # Ensure filename is unique in case of duplicates
                if not filename or filename == '':
                    filename = f"file_{i+1}"
                    
                # Add file extension if missing based on content type
                if '.' not in filename:
                    if content_type == 'application/pdf':
                        filename += '.pdf'
                    elif content_type == 'image/jpeg':
                        filename += '.jpg'
                    elif content_type == 'image/png':
                        filename += '.png'
                    elif content_type == 'text/plain':
                        filename += '.txt'
                    elif content_type == 'application/msword':
                        filename += '.doc'
                    elif content_type == 'application/vnd.ms-excel':
                        filename += '.xls'
                        
                # Add the file to the ZIP
                zf.writestr(filename, file_content)
                print(f"Added {filename} to ZIP ({len(file_content)} bytes)")
        
        # Seek to the beginning of the file
        memory_file.seek(0)
        
        # Send the ZIP file as a response
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'files_{timestamp}.zip'
        )
        
    except Exception as e:
        print(f"Error downloading files: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error downloading files: {str(e)}'}), 500

@app.route('/api/meetings/<meeting_id>/details', methods=['GET'])
def get_meeting_details(meeting_id):
    """
    Get a meeting by its ID
    
    Args:
        meeting_id: The unique identifier of the meeting
        
    Returns:
        The meeting data or a 404 error if not found
    """
    try:
        meeting = firebase.get_meeting_by_id(meeting_id)
        if not meeting:
            return jsonify({'error': f'Meeting with ID {meeting_id} not found'}), 404
        return jsonify({'meeting': meeting})
    except Exception as e:
        print(f"Error getting meeting details: {str(e)}")
        return jsonify({'error': f'Error getting meeting details: {str(e)}'}), 500

@app.route('/api/meetings/<meeting_id>/files', methods=['GET'])
def get_files_for_meeting(meeting_id):
    """
    Get all file URLs associated with a meeting
    
    Args:
        meeting_id: The unique identifier of the meeting
        
    Returns:
        A list of file URLs or a 404 error if meeting not found
    """
    try:
        files = firebase.get_files_urls_by_meeting_id(meeting_id)
        if files is None:
            return jsonify({'error': f'Meeting with ID {meeting_id} not found'}), 404
        return jsonify({'files': files})
    except Exception as e:
        print(f"Error getting meeting files: {str(e)}")
        return jsonify({'error': f'Error getting meeting files: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)