import os
import re
import json
import dotenv
import asyncio
from utils import *
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
        raise NotImplementedError("Image files are not supported yet")
    else:
        raise ValueError("Unsupported file format")

# Summarize and extract JSON
def __clean_json_text(text: str) -> str:
    return re.sub(r"```(?:json)?", "", text).strip()


async def summarize(text: str):
    """
    Given a text, extract a list of important items. Return ONLY valid JSON.
    :param text: Input text
    :return: List of important items
    """
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
        # parsed["vector"] = get_embedding(text).tolist()
        for (i, item) in enumerate(parsed):
            item["vector"] = get_embedding(json.dumps(item)).tolist()
            item["id"] = get_id(json.dumps(item))
        filtered = [item for item in parsed if "name" in item and "date" in item]
        return filtered
    except json.JSONDecodeError as e:
        print("❌ Failed to parse JSON, raw output:\n", response)
        return []


def get_id(text: str):
    """
    Given a text, return the unique identifier
    :param text: Input text
    :return: Unique identifier
    """
    return hash(text)


# Main function
async def main():
    documents = load_documents("files/data1.pdf")

    all_items = []
    for doc in documents:
        items = await summarize(doc)
        all_items.extend(items)

    # Save to JSON file
    with open("files/data2.json", "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
