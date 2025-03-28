from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import os
from config.embedding import embeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

vector_store = None

def init(docs=None):
    global vector_store
    if vector_store is not None:
        return vector_store

    client = MongoClient(os.environ.get("MONGODB_CONNECTION_STRING"))
    db = client["sample_mflix"]
    collection = db["vector_embeddings"]

    loader = PyPDFLoader("./test.pdf")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    if not docs:
        docs = loader.load()
    all_splits = text_splitter.split_documents(docs)
    print("docs: ", docs)
    print(os.environ.get("ATLAS_VECTOR_SEARCH_INDEX_NAME", ""))
    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=embeddings,
        collection=collection,
        index_name=os.environ.get("ATLAS_VECTOR_SEARCH_INDEX_NAME", ""),
        relevance_score_fn="cosine",
    )

    vector_store.add_documents(documents=all_splits)

    return vector_store
