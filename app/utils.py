from typing import TypedDict
from langchain_core.documents import Document
from langchain.globals import set_verbose, set_debug
from app.config.db import vector_store
from langchain_core.documents import Document
from langchain import hub
from app.config.model import llm
from app.model.state import State


def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    prompt = hub.pull("rlm/rag-prompt")
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    if response.content == "I don't know.":
        query_db(state["question"])
    return {"answer": response.content}

def query_db(question: str):
    raise NotImplementedError()

def debug():
    set_verbose(True)
    set_debug(True)
