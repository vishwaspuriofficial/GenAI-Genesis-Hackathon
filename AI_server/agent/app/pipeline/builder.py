from langgraph.graph import START, END, StateGraph
from pipeline.tools import handle_generation, retrieve, generate
from model.state import State

# graph_builder = StateGraph(State)
# graph_builder.add_node(retrieve)
# graph_builder.add_node(generate)
# graph_builder.add_edge(START, "retrieve")
# graph_builder.add_conditional_edges("retrieve", handle_generation)
# graph_builder.add_edge("generate", END)
# graph = graph_builder.compile()

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()