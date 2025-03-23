from langgraph.graph import START, StateGraph
from app.utils import retrieve, generate
from app.model.state import State

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()
