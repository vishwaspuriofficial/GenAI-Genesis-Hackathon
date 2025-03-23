import os
import json
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

"""
Note for the check_loaded and set_loaded functions:
here we maintain a list of loaded files in a JSON file.
file path: json_files/loaded_files.json
"""
def check_loaded(file_path: str) -> bool:
    """
    Check if the file is loaded before
    :param file: File name
    :return: True if the file is loaded before, False otherwise
    """
    with open("json_files/loaded_files.json", "r", encoding="utf-8") as json_file:
        with open(file_path, "rb") as f:
            if file in data:
                return True
            return False

    return False


def set_loaded(file):
    """
    Set the file as loaded
    :param file: File name
    :return:
    """
    # with open("json_files/database_test.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
    # data.append({"name": file})
    # with open("json_files/database_test.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
    return # temporary