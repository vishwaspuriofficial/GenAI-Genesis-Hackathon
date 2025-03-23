import os
import json
import dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.vector import Vector

dotenv.load_dotenv()

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)
db = firestore.client()

def upload_json_to_firestore(json_file_path, collection_path):
    # Read JSON data from the local file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Convert the vector into a Vector object
    data = [__regulate_json(doc) for doc in data]

    # Ensure the data is a list of documents
    if isinstance(data, list):
        for doc in data:
            db.collection(collection_path).add(doc)
    elif isinstance(data, dict):
        db.collection(collection_path).add(data)
    else:
        print("Unsupported JSON format. Must be a list or dictionary.")

    print("Data uploaded successfully.")


def __regulate_json(json_dict: dict):
    """
    This function is used to convert the vector into a Vector object.
    """
    for key, value in json_dict.items():
        if isinstance(value, dict):
            __regulate_json(value)
        elif isinstance(value, list):
            if all(isinstance(i, float) for i in value):
                json_dict[key] = Vector(value)
        else:
            pass
    return json_dict


if __name__ == "__main__":
    # Replace with your JSON file path and collection path
    json_file_path = "test.json"
    collection_path = "filter_data"
    upload_json_to_firestore(json_file_path, collection_path)