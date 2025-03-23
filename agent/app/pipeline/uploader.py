import os
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from config.db import init
from config.embedding import embeddings


def upload_file(file_path: str):
    loader = PyPDFLoader(file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = loader.load()
    all_splits = text_splitter.split_documents(docs)


    init(docs).add_documents(documents=all_splits)
