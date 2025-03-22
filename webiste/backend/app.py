from flask import Flask, request, jsonify
from database import Database
from models import Meeting, User
from flask_cors import CORS
from bson import ObjectId, json_util
import json
from datetime import datetime, timedelta
from functools import wraps
import jwt

app = Flask(__name__)
CORS(app)
db = Database()

# Add secret key for JWT
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(" ")[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.get_user_by_email(data['email'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    try:
        user = User(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            role=data['role']
        )
        user_id = db.create_user(user.to_dict())
        return jsonify({"message": "User created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Could not create user"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = db.get_user_by_email(data['email'])
    
    if user and User("", "", "").verify_password(data['password']):
        token = jwt.encode({
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({
            'token': token,
            'user': {
                'email': user['email'],
                'name': user['name'],
                'role': user['role']
            }
        })
    return jsonify({"error": "Invalid credentials"}), 401

# Custom JSON encoder for MongoDB objects
def custom_json_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

@app.route('/api/meetings', methods=['POST'])
@token_required
def create_meeting(current_user):
    if current_user['role'] != 'requester':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    meeting = Meeting(
        team_agent=data['team_agent'],
        prompt_text=data['prompt_text'],
        meeting_goal=data['meeting_goal'],
        meeting_link=data['meeting_link'],
        requester_name=current_user['name']
    )
    meeting_id = db.create_meeting(meeting.to_dict())
    return jsonify({"id": meeting_id, "message": "Meeting request created successfully"})

@app.route('/api/meetings', methods=['GET'])
def get_meetings():
    status = request.args.get('status')
    if status == 'pending':
        meetings = db.get_pending_meetings()
    else:
        meetings = db.get_all_meetings()
    # Use json_util.dumps to properly handle MongoDB objects
    return app.response_class(
        response=json_util.dumps(meetings),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/meetings/<meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    data = request.json
    db.update_meeting_status(meeting_id, data['status'])
    return jsonify({"message": "Meeting status updated successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 