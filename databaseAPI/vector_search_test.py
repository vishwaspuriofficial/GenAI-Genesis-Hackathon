import os
import dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from db_utils import get_embedding
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

dotenv.load_dotenv()

cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)
firestore_client = firestore.client()
collection = firestore_client.collection("filter_data")


if __name__ == '__main__':
    query = get_embedding(input("Enter your query: "))
    vector_query = collection.find_nearest(
        vector_field="vector",
        query_vector=Vector(query),
        distance_measure=DistanceMeasure.EUCLIDEAN,
        limit=5,
    )
    docs = vector_query.stream()
    for doc in docs:
        temp = doc.to_dict()
        temp = {key: value for key, value in temp.items() if key != "vector"}
        print(f"{doc.id} => {temp}")