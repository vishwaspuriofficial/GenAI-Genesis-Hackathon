from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, email, password, name, role="requester"):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.role = role  # User's role/team (e.g., "product", "engineering")
        self.created_at = datetime.utcnow()

    def verify_password(self, password_hash, password):
        """Verify that the provided password matches the stored hash"""
        return check_password_hash(password_hash, password)

    def to_dict(self):
        """Convert user object to dictionary for Firestore storage"""
        return {
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "password_hash": self.password_hash,
        }

class Meeting:
    def __init__(self, title, description, date, time, duration, requester_id, 
                 requester_name, requester_role, team_agent, meeting_link, status="pending"):
        self.title = title
        self.description = description
        self.date = date
        self.time = time
        self.duration = duration
        self.requester_id = requester_id
        self.requester_name = requester_name
        self.requester_role = requester_role
        self.team_agent = team_agent
        self.status = status
        self.response = ""
        self.attachments = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.meeting_link = meeting_link

    def to_dict(self):
        """Convert meeting object to dictionary for Firestore storage"""
        return {
            "title": self.title,
            "description": self.description,
            "date": self.date,
            "time": self.time,
            "duration": self.duration,
            "requester_id": self.requester_id,
            "requester_name": self.requester_name,
            "requester_role": self.requester_role,
            "team_agent": self.team_agent,
            "status": self.status,
            "response": self.response,
            "attachments": self.attachments,
            "meeting_link": self.meeting_link,
            # created_at and updated_at will be set by Firestore SERVER_TIMESTAMP
        }

class Attachment:
    def __init__(self, filename, file_url, file_type):
        self.filename = filename
        self.file_url = file_url
        self.file_type = file_type
        self.uploaded_at = datetime.utcnow()
        
    def to_dict(self):
        """Convert attachment object to dictionary for Firestore storage"""
        return {
            "filename": self.filename,
            "file_url": self.file_url,
            "file_type": self.file_type,
            # uploaded_at will be set by Firestore SERVER_TIMESTAMP
        } 