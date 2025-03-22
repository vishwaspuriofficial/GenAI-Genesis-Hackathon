from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, email, password, name, role="requester"):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.role = role  # "requester" or "responder"
        self.created_at = datetime.utcnow()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "password_hash": self.password_hash,
            "created_at": self.created_at
        }

class Meeting:
    def __init__(self, team_agent, prompt_text, meeting_goal, meeting_link, requester_name, status="pending"):
        self.team_agent = team_agent
        self.prompt_text = prompt_text
        self.meeting_goal = meeting_goal
        self.meeting_link = meeting_link
        self.requester_name = requester_name
        self.status = status
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "team_agent": self.team_agent,
            "prompt_text": self.prompt_text,
            "meeting_goal": self.meeting_goal,
            "meeting_link": self.meeting_link,
            "requester_name": self.requester_name,
            "status": self.status,
            "created_at": self.created_at
        } 