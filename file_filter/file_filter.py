import os
import re
import json
import dotenv
from utils import *
from db_utils import query_database
from database_test import *
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI

# Load API Key
dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GEMINI_API_KEY)


# Load PDF file and extract content
def load_documents(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return [doc.page_content for doc in documents]
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return [f.read()]
    elif file_path.endswith(".png") or file_path.endswith(".jpg"):
        raise NotImplementedError("Image json_files are not supported yet")
    else:
        raise ValueError("Unsupported file format")

# Summarize and extract JSON
def __clean_json_text(text: str) -> str:
    return re.sub(r"```(?:json)?", "", text).strip()


def summarize_file(file_path: str):
    """
    Load the file and extract a list of important items from its contents. Return ONLY valid JSON.
    :param file_path: Path to the input file
    :return: List of important items
    """
    documents = load_documents(file_path)

    all_items = []
    for text in documents:
        prompt = f"""
Extract a list of important items from the following text. Return ONLY valid JSON.
Each item should at least include `name` and `date`. Other fields are optional.

Text:
\"\"\" 
{text}
\"\"\"
"""
        response = ""
        # for chunk in llm.astream(prompt):
        #     response += chunk.content
        response = llm.invoke(prompt)
        try:
            cleaned = __clean_json_text(response.content)
            parsed = json.loads(cleaned)
            for item in parsed:
                item["vector"] = get_embedding(json.dumps(item)).tolist()
            filtered = [item for item in parsed if "name" in item and "date" in item]
            all_items.extend(filtered)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON for document:\n{response}")
            continue

    return all_items


def check_in_database(document) -> bool:
    """
    Check if the document is already in the database
    :param document: Document object
    :return: True if the document is in the database, False otherwise
    """
    db_response = query_database(json.dumps(document))
    prompt = f"""
Check if the following document is already in the database:
\"\"\"
{json.dumps(document, indent=2)}
\"\"\"
The Database returned the following results:
\"\"\"
{json.dumps(db_response, indent=2)}
\"\"\"
"""
    response = llm.invoke(prompt)
    return "Yes" in response.content
    


def update_database_from_raw_files():
    """
    This function scans all the files present in the firebase (currently we mock it using the `raw_files` directory)
    and updates the database with the new entries.
    :return:
    """
    # load all the files
    files = os.listdir("raw_files")
    for file in files:
        print(f"Processing file: {file}") # for testing
        # if this file is loaded before, skip it
        if check_loaded(file):
            print(f"\tFile {file} already loaded")
            continue
        # load and format the file
        documents = summarize_file(os.path.join("raw_files", file))
        # for each document, check if it is already in the database
        # if not, insert it
        for d in documents:
            if check_in_database(d):
                print(f"\tDocument already in the database")
                continue
            insert_database(Document(d))
        # mark the file as loaded
        set_loaded(file)


if __name__ == "__main__":
    update_database_from_raw_files()
