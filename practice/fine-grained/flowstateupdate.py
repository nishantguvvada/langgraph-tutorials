# Combine control flow and state updates
# Perform state updates and decide which node to go to next

# LangGraph facilitates by returning a Command object from the node function

# Navigate from a node within a subgraph to a different subgraph (a different node in the parent graph)

# def my_node(state: State) -> Command[Literal["my_other_node"]]:
#     return Command(
#         update={"messages":"messages"},
#         goto="other_subgraph",
#         graph=Command.PARENT
#     )

# When you send updates from a subgraph node to a parent graph node for a key that's shared by both parent and subgraph state schemas,
# you must define a reducer for the key you're updating in the parent graph state. 

from typing_extensions import TypedDict, Annotated, Literal
from langgraph.graph import END, StateGraph, START
from langgraph.types import Command
import operator
import random

class State(TypedDict):
    messages: Annotated[list[str], operator.add]

def node_a(state: State) -> Command[Literal["node_b","node_c"]]: # necessary for graph rendering
    print("Called A")
    value = random.choice(["b", "c"])
    if value == "b":
        goto = "node_b"
    else:
        goto = "node_c"

    return Command(
        update={"messages": [f"{value} sent from A"]},
        goto=goto
    )

def node_b(state: State):
    print("Called B")
    return {"messages": ["sent from B"]}

def node_c(state: State):
    print("Called C")
    return {"messages": ["sent from C"]}

graph = StateGraph(State).add_node(node_a).add_node(node_b).add_node(node_c).add_edge(START, "node_a")
graph = graph.compile()

result = graph.invoke({"messages": ["Hi from the user"]})

print(result)