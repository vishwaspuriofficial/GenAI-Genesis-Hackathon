from langgraph.graph import START, StateGraph
from utils import retrieve, generate
from model.state import State

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()
