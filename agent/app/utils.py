from typing import TypedDict
from langchain_core.documents import Document
from langchain.globals import set_verbose, set_debug
from config.db import vector_store
from langchain_core.documents import Document
from langchain import hub
from config.model import llm
from model.state import State


def retrieve(state: State):
    if "context" in state:
        return {"context": state["context"]}
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    prompt = hub.pull("rlm/rag-prompt")
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


def debug():
    set_verbose(True)
    set_debug(True)
