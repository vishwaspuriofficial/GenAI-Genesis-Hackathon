"""
Firebase configuration for database and file storage
"""
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import json
from datetime import datetime
from config import Config

class FirebaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize Firebase with service account credentials"""
        try:
            cred = None
            if Config.FIREBASE_CREDENTIALS_JSON:
                try:
                    cred_json = json.loads(Config.FIREBASE_CREDENTIALS_JSON)
                    cred = credentials.Certificate(cred_json)
                    print("Using Firebase credentials from environment variable")
                except json.JSONDecodeError:
                    if os.path.exists(Config.FIREBASE_CREDENTIALS_JSON):
                        cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_JSON)
                        print(f"Using Firebase credentials from file: {Config.FIREBASE_CREDENTIALS_JSON}")
            
            if cred is None:
                cred_paths = [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase-credentials.json'),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase_credentials.json'),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service-account.json'),
                ]
                
                for path in cred_paths:
                    if os.path.exists(path):
                        cred = credentials.Certificate(path)
                        print(f"Using Firebase credentials from file: {path}")
                        break
            
            # If credentials still not found, enter mock mode
            if cred is None:
                print("\nERROR: Firebase credentials not found.")
                print("To use Firebase, you need a service account key file.")
                print("1. Create a service account in your Firebase project")
                print("2. Generate a private key (JSON format)")
                print("3. Save the JSON file as 'firebase-credentials.json' in the backend directory\n")
                print("Starting in MOCK MODE - no real Firebase will be used\n")
                self.mock_mode = True
                
                # Create mock attributes
                self.db = None
                self.bucket = None
                self.users_collection = 'user'
                self.appointments_collection = 'appointment'
                return
                
            # Initialize the app
            print(f"Initializing Firebase app with storage bucket: {Config.FIREBASE_STORAGE_BUCKET}")
            firebase_admin.initialize_app(cred, {
                'storageBucket': Config.FIREBASE_STORAGE_BUCKET
            })
            
            # Initialize Firestore and Storage
            print("Initializing Firestore client...")
            self.db = firestore.client()
            
            # Set mock mode to False
            self.mock_mode = False
            
            try:
                print("Testing Firestore connection...")
                test_ref = self.db.collection('_test').document('test')
                test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
                test_ref.get()  # If this succeeds, connection is working
                test_ref.delete()  # Clean up test document
                print("Firestore connection verified successfully")
            except Exception as e:
                print(f"WARNING: Could not verify Firestore connection: {str(e)}")
                print("Possible solutions:")
                print("1. Make sure you've created a Firestore database in the Firebase console")
                print("2. Verify that your Firebase credentials have permission to access Firestore")
                print("3. Check if you have the correct project ID in your credentials file")
                print("Continuing anyway, as this might be normal for a new database.")
            
            self.bucket = storage.bucket()
            
            print("Firebase initialized successfully")
            
            # Use these collection names for Firestore
            self.users_collection = 'user'  # Changed from 'users' to 'user'
            self.appointments_collection = 'appointment'
            
            # Create Firestore collections references
            self.users_ref = self.db.collection(self.users_collection)
            self.appointments_ref = self.db.collection(self.appointments_collection)
            
            print(f"Firestore collections initialized: {self.users_collection}, {self.appointments_collection}")
        except Exception as e:
            print(f"Error initializing Firebase: {str(e)}")
            print("\nStarting in MOCK MODE - no real Firebase will be used\n")
            # Create placeholders for development if Firebase isn't configured
            self.db = None
            self.bucket = None
            self.users_collection = 'user'
            self.appointments_collection = 'appointment'
            self.users_ref = None
            self.appointments_ref = None
            self.mock_mode = True
    
    # File Storage methods
    def upload_file(self, file_data, filename, folder="meeting_files"):
        """Upload a file to Firebase Storage
        
        Args:
            file_data: The binary data of the file
            filename: The name of the file
            folder: The folder path in Firebase Storage
            
        Returns:
            The public URL of the uploaded file
        """
        if self.mock_mode or self.bucket is None:
            # For development without Firebase
            print("Firebase Storage not configured, using mock upload")
            return f"https://example.com/mock-firebase/{folder}/{filename}"
            
        # Create a storage reference
        blob_path = f"{folder}/{filename}"
        blob = self.bucket.blob(blob_path)
        
        # Upload the file
        blob.upload_from_string(file_data)
        
        # Make the file publicly accessible
        blob.make_public()
        
        # Return the public URL
        return blob.public_url
    
    def delete_file(self, file_url):
        """Delete a file from Firebase Storage based on its URL
        
        Args:
            file_url: The public URL of the file to delete
        """
        if self.mock_mode or self.bucket is None:
            print("Firebase Storage not configured, skipping deletion")
            return
            
        # Extract the path from the URL
        if 'googleapis.com' in file_url:
            path = file_url.split(f'{Config.FIREBASE_STORAGE_BUCKET}/o/')[1].split('?')[0]
            path = path.replace('%2F', '/')
            
            # Delete the file
            blob = self.bucket.blob(path)
            blob.delete()
    
    # User methods
    def create_user(self, user_data):
        """Create a new user in Firestore
        
        Note: This creates a document in the 'user' collection.
        """
        if self.mock_mode or self.db is None:
            print("Using mock database for create_user")
            return "mock-user-id-12345"
            
        # Check if email already exists
        email_query = self.users_ref.where('email', '==', user_data['email']).limit(1).get()
        if len(list(email_query)) > 0:
            raise ValueError("Email already exists")
            
        # Add timestamp
        user_data['created_at'] = firestore.SERVER_TIMESTAMP
        
        # Add user to Firestore
        user_ref = self.users_ref.document()
        user_ref.set(user_data)
        
        return user_ref.id
        
    def get_user_by_email(self, email):
        """Get a user by email
        
        Note: This queries the 'user' collection.
        """
        if self.mock_mode or self.db is None:
            print("Using mock database for get_user_by_email")
            if email == "test@example.com":
                return {
                    "id": "mock-user-id-12345",
                    "email": "test@example.com",
                    "password_hash": "$2b$12$1234567890123456789012",  # Mock hash
                    "role": "product",
                    "name": "Test User",
                    "created_at": datetime.utcnow()
                }
            return None
            
        users = self.users_ref.where('email', '==', email).limit(1).get()
        for user in users:
            # Return user data with ID
            user_data = user.to_dict()
            user_data['id'] = user.id
            return user_data
            
        return None
    
    # Meeting methods
    def create_meeting(self, meeting_data):
        """Create a new meeting in Firestore
        
        Note: This creates a document in the 'appointment' collection.
        """
        if self.mock_mode or self.db is None:
            print("Using mock database for create_meeting")
            return "mock-meeting-id-12345"
            
        # Add timestamps
        meeting_data['created_at'] = firestore.SERVER_TIMESTAMP
        meeting_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        # Add meeting to Firestore
        meeting_ref = self.appointments_ref.document()
        meeting_ref.set(meeting_data)
        
        return meeting_ref.id
    
    def get_all_meetings(self):
        """Get all meetings
        
        Note: This queries the 'appointment' collection.
        """
        if self.mock_mode or self.db is None:
            print("Using mock database for get_all_meetings")
            return [
                {
                    "id": "mock-meeting-id-12345",
                    "title": "Mock Meeting 1",
                    "description": "This is a mock meeting for testing",
                    "date": "2025-01-15",
                    "time": "14:00",
                    "duration": 60,
                    "requester_id": "mock-user-id-12345",
                    "requester_name": "Test User",
                    "requester_role": "product",
                    "team_agent": "engineering",
                    "status": "pending",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "attachments": [
                        {
                            "filename": "mock_document.pdf",
                            "file_url": "https://example.com/mock-firebase/meeting_files/mock_document.pdf",
                            "file_type": "application/pdf",
                            "uploaded_at": datetime.utcnow()
                        }
                    ]
                }
            ]
            
        meetings = []
        for meeting in self.appointments_ref.get():
            meeting_data = meeting.to_dict()
            meeting_data['id'] = meeting.id
            meetings.append(meeting_data)
        return meetings
    
    def get_meetings_by_team_or_requester(self, role, status=None):
        """Get meetings where either:
        1. The user's team is the assigned team_agent, or
        2. The user's role matches the requester's role
        
        Optionally filter by status.
        Note: This is querying the 'appointment' collection.
        """
        if self.mock_mode or self.db is None:
            print("Using mock database for get_meetings_by_team_or_requester")
            mock_meetings = self.get_all_meetings()
            if status:
                return [m for m in mock_meetings if m.get('team_agent') == role or 
                      m.get('requester_role') == role and m.get('status') == status]
            return [m for m in mock_meetings if m.get('team_agent') == role or 
                  m.get('requester_role') == role]
            
        # We'll do two separate queries and combine the results
        team_query = self.appointments_ref.where('team_agent', '==', role)
        requester_query = self.appointments_ref.where('requester_role', '==', role)
        
        # If status filter provided, add it to both queries
        if status:
            team_query = team_query.where('status', '==', status)
            requester_query = requester_query.where('status', '==', status)
        
        # Get results from both queries
        team_meetings = [doc.to_dict() | {'id': doc.id} for doc in team_query.get()]
        requester_meetings = [doc.to_dict() | {'id': doc.id} for doc in requester_query.get()]
        
        combined = {}
        for meeting in team_meetings + requester_meetings:
            combined[meeting['id']] = meeting
            
        return list(combined.values())
    
    def get_meeting_by_id(self, meeting_id):
        """Get a meeting by ID
        
        Note: This retrieves a document from the 'appointment' collection.
        """
        if self.mock_mode or self.db is None:
            print("Using mock database for get_meeting_by_id")
            mock_meetings = self.get_all_meetings()
            for meeting in mock_meetings:
                if meeting.get('id') == meeting_id:
                    return meeting
            return None
            
        meeting_ref = self.appointments_ref.document(meeting_id)
        meeting = meeting_ref.get()
        
        if meeting.exists:
            meeting_data = meeting.to_dict()
            meeting_data['id'] = meeting.id
            return meeting_data
            
        return None
    
    def update_meeting_status(self, meeting_id, status):
        """Update meeting status
        
        Note: This updates a document in the 'appointment' collection.
        """
        if self.mock_mode or self.db is None:
            print(f"Using mock database for update_meeting_status: {meeting_id} to {status}")
            return
            
        self.appointments_ref.document(meeting_id).update({
            'status': status,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
    
    def update_meeting_response(self, meeting_id, response):
        """Update meeting response from team agent
        
        Note: This updates a document in the 'appointment' collection.
        """
        if self.mock_mode or self.db is None:
            print(f"Using mock database for update_meeting_response: {meeting_id}")
            return
            
        self.appointments_ref.document(meeting_id).update({
            'response': response,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
    
    def add_attachment_to_meeting(self, meeting_id, attachment_data):
        """Add a file attachment to a meeting
        
        Note: This updates a document in the 'appointment' collection.
        """
        if self.mock_mode or self.db is None:
            print(f"Using mock database for add_attachment_to_meeting: {meeting_id}")
            return True
            
        # Add timestamp to attachment
        attachment_data['uploaded_at'] = firestore.SERVER_TIMESTAMP
        
        self.appointments_ref.document(meeting_id).update({
            'attachments': firestore.ArrayUnion([attachment_data]),
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return True
    
    def remove_attachment_from_meeting(self, meeting_id, file_url):
        """Remove a file attachment from a meeting
        
        Note: This updates a document in the 'appointment' collection.
        This requires getting the meeting, modifying the attachments list,
        and updating the document since ArrayRemove requires the exact object.
        """
        if self.mock_mode or self.db is None:
            print(f"Using mock database for remove_attachment_from_meeting: {meeting_id}")
            return True
            
        # Get the meeting
        meeting_ref = self.appointments_ref.document(meeting_id)
        meeting = meeting_ref.get()
        
        if meeting.exists:
            meeting_data = meeting.to_dict()
            attachments = meeting_data.get('attachments', [])
            
            # Find and remove the attachment with the matching URL
            updated_attachments = [a for a in attachments if a.get('file_url') != file_url]
            
            # Update the meeting document
            meeting_ref.update({
                'attachments': updated_attachments,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
        return True 