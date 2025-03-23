# db_utils.py

debug_mode = True

import os
import openai
import numpy as np

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embedding_model = openai.Embedding(api_key=OPENAI_API_KEY)

def get_embedding(text: str):
    """
    Given a text, return the embedding vector
    :param text: Input text
    :return: Embedding vector
    """
    text = text.replace("\n", " ")
    response = embedding_model.create(
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
    if debug_mode:
        return [
            {
                "source": "example_source",
                "category": "example_category",
                "date": "2022-01-01",
                "page_content": "This is an example page content."
            }
        ]
    else:
        # Query the actual database
        pass