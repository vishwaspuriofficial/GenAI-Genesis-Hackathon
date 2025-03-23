from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import os
from app.config.embedding import embeddings

client = MongoClient(os.environ.get("MONGODB_CONNECTION_STRING"))
db = client["sample_mflix"]
collection = db["vector_embeddings"]

vector_store = MongoDBAtlasVectorSearch(
    embedding=embeddings,
    collection=collection,
    index_name=os.environ.get("ATLAS_VECTOR_SEARCH_INDEX_NAME", ""),
    relevance_score_fn="cosine",
)
