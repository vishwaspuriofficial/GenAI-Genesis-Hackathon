from pymongo import MongoClient
from config import Config
from bson import ObjectId
import json
from bson import json_util

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client.meeting_system
        self.meetings = self.db.meetings
        self.users = self.db.users
        
        # Create unique index for email
        self.users.create_index("email", unique=True)

    # User methods
    def create_user(self, user_data):
        try:
            result = self.users.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            if "duplicate key error" in str(e):
                raise ValueError("Email already exists")
            raise e

    def get_user_by_email(self, email):
        return self.users.find_one({"email": email})

    def create_meeting(self, meeting_data):
        result = self.meetings.insert_one(meeting_data)
        return str(result.inserted_id)

    def get_all_meetings(self):
        meetings = list(self.meetings.find())
        return meetings  # json_util.dumps will handle the conversion in the route

    def get_pending_meetings(self):
        meetings = list(self.meetings.find({"status": "pending"}))
        return meetings

    def update_meeting_status(self, meeting_id, status):
        self.meetings.update_one(
            {"_id": ObjectId(meeting_id)},
            {"$set": {"status": status}}
        )

    def get_meeting_by_id(self, meeting_id):
        meeting = self.meetings.find_one({"_id": ObjectId(meeting_id)})
        return meeting 