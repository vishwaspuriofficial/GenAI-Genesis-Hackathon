"""
Test script to verify Firebase Storage uploads
"""
import os
import uuid
import json
from firebase_admin import credentials, storage, initialize_app, firestore
import firebase_admin
import sys
from config import Config

def test_direct_firebase_upload():
    """Test direct upload to Firebase Storage"""
    
    # Create a test file
    test_file_path = "./uploads/testing.pdf"
    with open(test_file_path, "w") as f:
        f.write("This is a test file for Firebase Storage upload.")
    
    print(f"Test file created: {test_file_path}")
    
    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        # Load credentials
        if os.path.exists('firebase-credentials.json'):
            cred_path = 'firebase-credentials.json'
            print(f"Loading Firebase credentials from: {cred_path}")
            cred = credentials.Certificate(cred_path)
        else:
            print("Firebase credentials file not found!")
            return False
        
        # Print available bucket formats for testing
        raw_bucket = Config.FIREBASE_STORAGE_BUCKET
        print(f"Raw bucket from config: {raw_bucket}")
        
        # Try multiple bucket formats
        bucket_formats = [
            raw_bucket,  # Original format
            raw_bucket.replace('gs://', '').split('.')[0],  # Extract name only
            raw_bucket.replace('gs://', ''),  # Remove gs:// prefix only
        ]
        
        success = False
        
        for bucket_format in bucket_formats:
            try:
                print(f"\nTrying bucket format: {bucket_format}")
                
                # Initialize Firebase app with this bucket format
                if firebase_admin._apps:
                    # Delete previous app if it exists
                    for app in list(firebase_admin._apps.values()):
                        firebase_admin.delete_app(app)
                
                app = initialize_app(cred, {
                    'storageBucket': bucket_format
                })
                
                # Test Firestore connection
                db = firestore.client()
                print("Firestore connection initialized")
                
                # Try to access a test collection
                test_ref = db.collection('_test').document('test')
                test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
                test_ref.get()
                test_ref.delete()
                print("Firestore connection verified successfully")
                
                # Test storage bucket access
                bucket = storage.bucket()
                print(f"Storage bucket initialized: {bucket.name}")
                
                try:
                    # Try to get bucket metadata
                    bucket.reload()
                    print("Storage bucket verified successfully")
                    
                    # Try uploading
                    unique_id = str(uuid.uuid4())
                    blob_name = f"test_uploads/{unique_id}_test.txt"
                    blob = bucket.blob(blob_name)
                    
                    with open(test_file_path, 'rb') as f:
                        blob.upload_from_file(f)
                    
                    blob.make_public()
                    print(f"File uploaded successfully to {blob_name}")
                    print(f"Public URL: {blob.public_url}")
                    success = True
                    break
                    
                except Exception as e:
                    print(f"Error accessing storage bucket: {str(e)}")
            
            except Exception as e:
                print(f"Error with bucket format '{bucket_format}': {str(e)}")
    
    else:
        # Firebase already initialized, use the existing app
        try:
            bucket = storage.bucket()
            print(f"Using existing Firebase app with bucket: {bucket.name}")
            
            # Try to get bucket metadata
            bucket.reload()
            print("Storage bucket verified successfully")
            
            # Try uploading
            unique_id = str(uuid.uuid4())
            blob_name = f"test_uploads/{unique_id}_test.txt"
            blob = bucket.blob(blob_name)
            
            with open(test_file_path, 'rb') as f:
                blob.upload_from_file(f)
            
            blob.make_public()
            print(f"File uploaded successfully to {blob_name}")
            print(f"Public URL: {blob.public_url}")
            success = True
            
        except Exception as e:
            print(f"Error using existing Firebase app: {str(e)}")
    
    # Clean up
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"Test file removed: {test_file_path}")
    
    return success

if __name__ == "__main__":
    success = test_direct_firebase_upload()
    print(f"\nTest result: {'Success' if success else 'Failed'}")
    sys.exit(0 if success else 1) 