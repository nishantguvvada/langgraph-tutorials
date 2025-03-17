from typing_extensions import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
import random

# def add(left, right):
#     return left + right

# class State(TypedDict):
#     messages: Annotated[list[AnyMessage], add]

# class State(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]

class State(MessagesState):
    pass

class MyNode:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, state: State): # __call__ method allows the instance to assume function behaviour
        return {"messages": [("assistant", f"Called node {self.name}")]}
    
def route(state: State):
    if len(state["messages"]) > 10:
        return "__end__"
    return "entry_node"

def add_fractal_nodes(builder, current_node, level, max_level):
    if level > max_level:
        return
    
    num_nodes = random.randint(1, 3)
    for i in range(num_nodes):
        nm = ["A","B","C"][i]
        node_name = f"node_{current_node}_{nm}"
        builder.add_node(node_name, MyNode(node_name))
        builder.add_edge(current_node, node_name)

        r = random.random()
        if r > 0.2 and level + 1 < max_level:
            add_fractal_nodes(builder, node_name, level + 1, max_level)
        elif r > 0.05:
            builder.add_conditional_edges(node_name, route, node_name)
        else:
            builder.add_edge(node_name, "__end__")

def build_fractal_graph(max_level: int):
    builder = StateGraph(State)
    entry_point = "entry_node"
    builder.add_node(entry_point, MyNode(entry_point))
    builder.add_edge(START, entry_point)

    add_fractal_nodes(builder, entry_point, 1, max_level)

    builder.add_edge(entry_point, END)

    return builder.compile()

app = build_fractal_graph(3)

app.get_graph().draw_mermaid_png(output_file_path="./graph.png")



