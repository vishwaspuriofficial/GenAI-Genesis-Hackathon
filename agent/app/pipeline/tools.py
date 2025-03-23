from calendar import c
from re import M
from typing import Literal, TypedDict
from langchain_core.documents import Document
from langchain.globals import set_verbose, set_debug
from langchain_core.documents import Document
from langchain import hub
from config.db import init
from config.model import llm
from model.state import State
from langchain_core.prompts import PromptTemplate

temp_state = []

vector_store = init()
def retrieve(state: State):
    global temp_state
    # TODO: Implement a retrieval mechanism
    # if "context" in state:
    #     return {"context": state["context"]}
    if not temp_state:
        temp_state.append(state)
    else:
        state = temp_state[0]
    print("state: ", state)
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    prompt = PromptTemplate.from_template(
        """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that 'I'm sorry, I don't have that information at the moment. Let me check and get back to you with the details.'. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:"""
    )
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


MAX_RETRIES = 5
current_retries = 0


def handle_generation(state: State) -> Literal["retrieve", "generate"]:
    global current_retries
    if current_retries <= MAX_RETRIES:
        return "generate"
    prompt = PromptTemplate.from_template(
        """You are an assistant for providing better queries for question-answering tasks if needed. Use the following pieces of retrieved context to assess whether there is enough context for the question to be answered. If you require more context, only generate a new search query to be used by RAG. If you are confident that the context is enough, only say 'Enough context' NOTHING MORE NOTHING LESS.
Question: {question} 
Context: {context}
"""
    )
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    if response.content != "Enough context":
        current_retries += 1
        temp_state[0] = {"question": response.content}
        return "retrieve"
    return "generate"
