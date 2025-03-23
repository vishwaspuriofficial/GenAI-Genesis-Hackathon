import os
import re
import json
import dotenv
import asyncio
from utils import *
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


async def summarize_file(file_path: str):
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
        async for chunk in llm.astream(prompt):
            response += chunk.content
        try:
            cleaned = __clean_json_text(response)
            parsed = json.loads(cleaned)
            for item in parsed:
                item["vector"] = get_embedding(json.dumps(item)).tolist()
                item["id"] = get_id(json.dumps(item))
            filtered = [item for item in parsed if "name" in item and "date" in item]
            all_items.extend(filtered)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON for document:\n{response}")
            continue

    return all_items



def get_id(text: str):
    """
    Given a text, return the unique identifier
    :param text: Input text
    :return: Unique identifier
    """
    return hash(text)


# Main function
async def main():
    all_items = await summarize_file("json_files/data1.pdf")

    # Save to JSON file
    with open("json_files/data2.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)



def check_loaded(file) -> bool:
    """
    Check if the file is loaded before
    :param file: File name
    :return: True if the file is loaded before, False otherwise
    """
    # with open("json_files/database_test.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
    #     for d in data:
    #         if d["name"] == file:
    #             return True
    # return False
    return False # temporary


def update_database():
    """
    This function scans all the files present in the firebase (currently we mock it using the `raw_files` directory)
    and updates the database with the new entries.
    :return:
    """
    # load all the files
    files = os.listdir("json_files/raw_files")
    for file in files:
        # if this file is loaded before, skip it
        if check_loaded(file):
            continue
        # load and format the file
        summarize_file(os.path.join("json_files/raw_files", file))


if __name__ == "__main__":
    asyncio.run(main())
