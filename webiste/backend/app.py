from flask import Flask, request, jsonify, send_file
from firebase_config import FirebaseService
from models import User, Meeting, Attachment
from werkzeug.utils import secure_filename
from functools import wraps
from config import Config
import jwt
import os
import uuid
import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.secret_key = Config.SECRET_KEY

# Initialize Firebase
firebase = FirebaseService()

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Configure CORS
from flask_cors import CORS
CORS(app)

# Helper function to check if a file extension is allowed
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
        required_fields = ['title', 'description', 'date', 'time', 'duration', 'team_agent']
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
            team_agent=data['team_agent']
        )
        
        # Add meeting to database
        meeting_id = firebase.create_meeting(meeting.to_dict())
        
        return jsonify({
            'message': 'Meeting created successfully',
            'meeting_id': meeting_id
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
    """Upload files directly to a folder named after the team role"""
    print("[DEBUG] Starting /api/team-upload endpoint with simplified folder structure")
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
    
    # Create upload folder if it doesn't exist
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
    
    # Get user's role for the folder name
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

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG) 