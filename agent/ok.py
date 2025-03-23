import getpass
from multiprocessing import process
import os
from dotenv import load_dotenv

load_dotenv()
os.getenv('ATLAS_VECTOR_SEARCH_INDEX_NAME')

import getpass
import os

if not os.environ.get("COHERE_API_KEY"):
    os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("command-r-plus", model_provider="cohere")

import getpass
import os

if not os.environ.get("COHERE_API_KEY"):
    os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")

from langchain_cohere import CohereEmbeddings

embeddings = CohereEmbeddings(model="embed-english-v3.0")

from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch

client = MongoClient(os.environ.get("MONGODB_CONNECTION_STRING"))

db = client["sample_mflix"]
collection = db["vector_embeddings"]
databases = client.list_database_names()


import bs4
from langchain import hub
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate


# Load and chunk contents of the blog
loader = PyPDFLoader("../test.pdf")
docs = loader.load()
# print(docs[0].page_content)
vector_store = MongoDBAtlasVectorSearch.from_documents(
    documents=docs,
    embedding=embeddings,
    collection=collection,
    index_name=os.environ.get("ATLAS_VECTOR_SEARCH_INDEX_NAME", ""),
    relevance_score_fn="cosine",
)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# Index chunks
_ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
prompt = PromptTemplate.from_template(
    """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that 'I'm sorry, I don't have that information at the moment. Let me check and get back to you with the details.'. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:"""
)

print(vector_store.similarity_search("What is the name of the ml paper?"))


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    print(docs_content)
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

response = graph.invoke({"question": "who wrote the ML paper?"})
print(response["answer"])