import os
import json
import hashlib
from openai import OpenAI
import numpy as np

__all__ = ['get_embedding', 'check_loaded', 'set_loaded']

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_file_md5(file_path):
    """
    Calculate the MD5 hash of a given file.

    :param file_path: Path to the file
    :return: 32-character hexadecimal MD5 hash string, or None if file not found
    """
    md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            # Read the file in chunks to avoid memory issues with large files
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def get_embedding(text: str):
    """
    Given a text, return the embedding vector
    :param text: Input text
    :return: Embedding vector
    """
    text = text.replace("\n", " ")
    response = openai_client.embeddings.create(
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
        fingerprint = get_file_md5(os.path.join("raw_files", file_path))
        data = json.load(json_file)
        if fingerprint in data:
            return True
    return False


def set_loaded(file_path):
    """
    Set the file as loaded
    :param file: File name
    :return:
    """
    with open("json_files/loaded_files.json", "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    with open("json_files/loaded_files.json", "w", encoding="utf-8") as json_file:
        fingerprint = get_file_md5(os.path.join("raw_files", file_path))
        data.append(fingerprint)
        json.dump(data, json_file, ensure_ascii=False, indent=4)