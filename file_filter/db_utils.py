# db_utils.py

import os
import dotenv
import numpy as np
import firebase_admin
from openai import OpenAI
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)
firestore_client = firestore.client()
collection = firestore_client.collection("filter_data")


def get_embedding(text: str):
    """
    Given a text, return the embedding vector
    :param text: Input text
    :return: Embedding vector
    """
    text = text.replace("\n", " ")
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    embedding = np.array(response.data[0].embedding)
    return embedding


def query_database(query: str):
    """
    Given a query, return the results from the database
    :param query: Input query
    :return: List of results
    """
    query_vec = get_embedding(query)
    vector_query = collection.find_nearest(
        vector_field="vector",
        query_vector=Vector(query_vec),
        distance_measure=DistanceMeasure.EUCLIDEAN,
        limit=5,
    )
    docs = vector_query.stream()
    answers = []
    for doc in docs:
        temp = doc.to_dict()
        temp = {key: value for key, value in temp.items() if key != "vector"}
        answers.append(temp)
    return answers


if __name__ == '__main__':
    query = input("Enter your query: ")
    response = query_database(query)
    print(response)
