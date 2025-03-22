import os
import openai
import numpy as np

__all__ = ['get_embedding']

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
        model="text-embedding-3-small"  # 请根据实际可用的模型名称进行替换
    )
    embedding = np.array(response.data[0].embedding)
    return embedding