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
            self.mock_mode = False  # Default to not using mock mode
            
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
                
            raw_bucket = Config.FIREBASE_STORAGE_BUCKET
            print(f"Raw Firebase Storage bucket URL: {raw_bucket}")
            
            self.original_bucket_url = raw_bucket
            
            if not raw_bucket:
                print("No Firebase Storage bucket URL found in configuration")
                self.mock_mode = True
                self.bucket = None
                return
                
            if raw_bucket.startswith('gs://'):
                bucket_name = raw_bucket.replace('gs://', '')
                print(f"Removed gs:// prefix from URL: {bucket_name}")
            else:
                bucket_name = raw_bucket
                
            self.bucket_name = bucket_name
            
            print(f"Using Firebase Storage bucket: {bucket_name}")
            
            if not bucket_name or bucket_name == "None" or '.' not in bucket_name:
                print("\nWARNING: Invalid Firebase Storage bucket name.")
                print(f"Current value: '{bucket_name}'")
                print("Setting Storage to MOCK MODE.\n")
                self.mock_mode = True
                self.db = None
                self.bucket = None
                self.users_collection = 'user'
                self.appointments_collection = 'appointment'
                return
            
            try:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': bucket_name
                })
                print("Firebase app initialized successfully")
            except Exception as e:
                print(f"Error initializing Firebase app: {str(e)}")
                print("Starting in MOCK MODE due to Firebase app initialization error.")
                self.mock_mode = True
                self.db = None
                self.bucket = None
                self.users_collection = 'user'
                self.appointments_collection = 'appointment'
                return
            
            # Initialize Firestore
            print("Initializing Firestore client...")
            try:
                self.db = firestore.client()
                self.mock_mode = False
            except Exception as e:
                print(f"Error creating Firestore client: {str(e)}")
                print("Firestore will be in MOCK MODE.")
                self.db = None
                self.mock_mode = True
            
            # Test Firestore connection
            if self.db:
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
            
            # Initialize Storage bucket
            try:
                print(f"Initializing Firebase Storage bucket: {bucket_name}")
                self.bucket = storage.bucket()
                
                # Try to access the bucket to verify it exists
                self.bucket.reload()
                print("Firebase Storage bucket successfully initialized")
                print(f"Firebase Storage bucket name: {self.bucket.name}")
            except Exception as e:
                print(f"ERROR: Could not access Firebase Storage bucket: {str(e)}")
                print("Possible solutions:")
                print("1. Make sure you've created a Storage bucket in the Firebase console")
                print("2. Verify that your Firebase credentials have permission to access Storage")
                print("3. Verify that the bucket name is correct in your config")
                print("4. Storage bucket name should match your Firebase project's default bucket")
                print("\nStorage uploads will use MOCK URLs instead.\n")
                self.bucket = None
                self.mock_mode = True
            
            print("Firebase initialized successfully")
            
            # Use these collection names for Firestore
            self.users_collection = 'user'  # Changed from 'users' to 'user'
            self.appointments_collection = 'appointment'
            self.filter_data_collection = 'filter_data'
            
            # Create Firestore collections references
            if self.db:
                self.users_ref = self.db.collection(self.users_collection)
                self.appointments_ref = self.db.collection(self.appointments_collection)
                self.filter_data_ref = self.db.collection(self.filter_data_collection)
                print(f"Firestore collections initialized: {self.users_collection}, {self.appointments_collection}")
            
            # Log final status
            if self.mock_mode:
                print("\nWARNING: Running in partial or full MOCK MODE")
                print(f"Firestore available: {self.db is not None}")
                print(f"Storage available: {self.bucket is not None}\n")
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
    def upload_file(self, file_path, filename=None, folder=None, content_type=None):
        """Upload a file to Firebase Storage and return the URL"""
        print(f"Starting upload_file: file_path={file_path}, filename={filename}, folder={folder}")
        
        try:
            file_size = os.path.getsize(file_path)
            print(f"File size: {file_size} bytes")
        except Exception as e:
            print(f"Error getting file size: {str(e)}")
        
        if not filename:
            filename = os.path.basename(file_path)
        
        # Generate a unique filename to avoid collisions
        unique_id = filename.split('.')[0]
        file_ext = filename.split('.')[-1] if '.' in filename else ''
        unique_filename = f"{unique_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}" if file_ext else unique_id
        
        if "/" in filename:
            blob_path = filename
        else:
            blob_path = f"{folder}/{unique_filename}" if folder else unique_filename
        
        print(f"Uploading to blob path: {blob_path}")
        
        # Create a storage reference
        blob = self.bucket.blob(blob_path)
        
        with open(file_path, 'rb') as file:
            if content_type:
                blob.upload_from_file(file, content_type=content_type)
            else:
                blob.upload_from_file(file)
        
        blob.make_public()
        
        bucket_name = self.bucket_name
        url = f"https://storage.googleapis.com/{bucket_name}/{blob_path}"
        
        print(f"File uploaded successfully. URL: {url}")
        return url
 
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
        meeting_ref = self.appointments_ref.document(meeting_id)
        meeting = meeting_ref.get()
        
        if meeting.exists:
            meeting_data = meeting.to_dict()
            meeting_data['id'] = meeting.id
            return meeting_data
            
        return None
    
    def get_files_urls_by_meeting_id(self, meeting_id):

        meeting_ref = self.appointments_ref.document(meeting_id)
        meeting = meeting_ref.get()

        if meeting.exists:
            meeting_data = meeting.to_dict()
            meeting_data['id'] = meeting.id
            raw_files_urls = meeting_data["response_files"]
            files_urls = [file_url.get("url") for file_url in raw_files_urls]
            return files_urls
            
        return None


    def get_meeting_short_info(self, meeting_id):
        """Get short meeting information by ID
        
        Note: This retrieves a document from the 'appointment' collection.
        """
        meeting_ref = self.appointments_ref.document(meeting_id)
        meeting = meeting_ref.get()

        if meeting.exists:
            meeting_data = meeting.to_dict()
            return {
                "meetingLink": meeting_data["meeting_link"],
                "teamName": meeting_data["team_agent"],
            }
            
        return None

    
    def download_files(self, files_urls):
        try:
            files_content = []
            for file_url in files_urls:
                if 'googleapis.com' in file_url:
                    path = file_url.split(f'{Config.FIREBASE_STORAGE_BUCKET}/o/')[1].split('?')[0]
                    path = path.replace('%2F', '/')

                    blob = self.bucket.blob(path)
                    blob.download_to_filename(file_url)
                    files_content.append(blob)
            return files_content
        
        except Exception as e:
            print(f"Error downloading files: {str(e)}")
            return None
        
    def get_file_content(self, file_url):
        """
        Get the content of a file from a Firebase Storage URL
        
        Args:
            file_url: URL of the file in Firebase Storage
            
        Returns:
            The file content as bytes or None if an error occurs
        """
        try:
            print(f"Attempting to get file content from URL: {file_url}")
            print(f"Current bucket name in config: {Config.FIREBASE_STORAGE_BUCKET}")
            
            # Extract the path more reliably
            if 'storage.googleapis.com' in file_url:
                # Format: https://storage.googleapis.com/BUCKET_NAME/PATH
                # Remove https://storage.googleapis.com/
                path = '/'.join(file_url.split('/')[4:])
                print(f"Parsed path using storage.googleapis.com format: {path}")
            elif 'firebasestorage.googleapis.com' in file_url:
                # Extract path from Firebase Storage URL
                if '/o/' in file_url:
                    # Handle URL format: https://firebasestorage.googleapis.com/v0/b/BUCKET/o/PATH?...
                    path = file_url.split('/o/')[1].split('?')[0]
                    path = path.replace('%2F', '/')
                    print(f"Parsed path using firebasestorage /o/ format: {path}")
                else:
                    # Handle direct URL format
                    parts = file_url.split('firebasestorage.googleapis.com/')
                    if len(parts) > 1:
                        path = parts[1]
                        if '?' in path:
                            path = path.split('?')[0]
                        print(f"Parsed path using firebasestorage direct format: {path}")
                    else:
                        print(f"Could not parse path from firebasestorage URL: {file_url}")
                        return None
            else:
                print(f"URL format not recognized: {file_url}")
                return None

            print(f"Final extracted path: {path}")
            
            # Get blob from bucket
            blob = self.bucket.blob(path)
            
            # Check if blob exists
            if not blob.exists():
                print(f"Blob does not exist: {path}")
                return None
                
            print(f"Blob exists, downloading content")
            # Download file content
            content = blob.download_as_bytes()
            print(f"Successfully downloaded {len(content)} bytes")
            return content
            
        except Exception as e:
            print(f"Error getting file content: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    def download_file_from_url(self, file_url):
        """
        Download file from URL and return content, content type, and filename
        
        Args:
            file_url: URL of the file to download
            
        Returns:
            Tuple of (file_content, content_type, filename) or (None, None, None) if error
        """
        try:
            print(f"Downloading file from URL: {file_url}")
            
            # Get file content
            file_content = self.get_file_content(file_url)
            if file_content is None:
                return None, None, None
                
            # Get filename from URL
            filename = file_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
                
            # Determine content type from extension
            extension = filename.split('.')[-1].lower() if '.' in filename else ''
            content_type = "application/octet-stream"  # Default
            
            if extension in ['pdf']:
                content_type = "application/pdf"
            elif extension in ['jpg', 'jpeg']:
                content_type = "image/jpeg"
            elif extension in ['png']:
                content_type = "image/png"
            elif extension in ['txt']:
                content_type = "text/plain"
            elif extension in ['doc', 'docx']:
                content_type = "application/msword"
            elif extension in ['xls', 'xlsx']:
                content_type = "application/vnd.ms-excel"
                
            return file_content, content_type, filename
            
        except Exception as e:
            print(f"Error downloading file from URL: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None, None
    
    def update_meeting_status(self, meeting_id, status):
        """Update meeting status
        
        Note: This updates a document in the 'appointment' collection.
        """
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
            
        # Add timestamp to attachment - use a string timestamp instead of SERVER_TIMESTAMP
        attachment_data['uploaded_at'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
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
        
    def add_response_file_to_meeting(self, meeting_id, file_data):
        """Add a response file to a meeting
        
        This adds files uploaded by team members to a separate 'response_files' array
        in the meeting document. These files are stored in team-specific folders.
        
        Args:
            meeting_id: The ID of the meeting to add the file to
            file_data: Dictionary containing file metadata (filename, file_url, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if self.mock_mode or self.db is None:
            print(f"Using mock database for add_response_file_to_meeting: {meeting_id}")
            return True
            
        try:
            # Get the meeting document
            meeting_ref = self.appointments_ref.document(meeting_id)
            meeting = meeting_ref.get()
            
            if not meeting.exists:
                print(f"Meeting {meeting_id} not found")
                return False
                
            # Initialize response_files array if it doesn't exist
            meeting_data = meeting.to_dict()
            if 'response_files' not in meeting_data:
                meeting_ref.update({
                    'response_files': []
                })
            
            # Add the response file to the response_files array
            meeting_ref.update({
                'response_files': firestore.ArrayUnion([file_data]),
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            return True
        except Exception as e:
            print(f"Error adding response file to meeting: {str(e)}")
            return False 