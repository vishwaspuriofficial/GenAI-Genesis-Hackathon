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
@app.route('/api/meetings/upload/<meeting_id>', methods=['POST'])
@token_required
def upload_file(current_user, meeting_id):
    try:
        # Check if meeting exists
        meeting = firebase.get_meeting_by_id(meeting_id)
        
        if not meeting:
            return jsonify({'message': 'Meeting not found'}), 404
        
        # Check if user has permission to upload to this meeting
        if meeting['requester_id'] != current_user['id'] and meeting['team_agent'] != current_user['role']:
            return jsonify({'message': 'You do not have permission to upload to this meeting'}), 403
        
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400
            
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
            
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'message': 'File type not allowed'}), 400
            
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Save the file locally
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Upload the file to Firebase Storage
        with open(file_path, 'rb') as file_data:
            file_url = firebase.upload_file(file_data.read(), unique_filename)
        
        # Delete the local file
        os.remove(file_path)
        
        # Add the attachment to the meeting
        attachment = Attachment(
            filename=filename,
            file_url=file_url,
            file_type=file.content_type
        )
        
        firebase.add_attachment_to_meeting(meeting_id, attachment.to_dict())
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_url': file_url,
            'filename': filename
        }), 200
    except Exception as e:
        print("Error uploading file:", e)
        return jsonify({'message': 'Error uploading file', 'error': str(e)}), 500

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

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG) 