# Perform both state updates AND decide which node to go to next in the SAME node.

import random
from typing_extensions import TypedDict, Literal, Annotated
import operator
from langgraph.graph import StateGraph, START
from langgraph.types import Command

class State(TypedDict):
    messages: Annotated[list, operator.add]

def node_a(state: State) -> Command[Literal["node_b", "node_c"]]: # return type annotations is required
    print("Called A")
    value = random.choice(["c","b"])
    if value == "b":
        goto = "node_b"
    else:
        goto = "node_c"

    # Command returns the update and the next node
    return Command(
        update={"messages": [f"Going to {goto}"]},
        goto=goto
    )

def node_b(state: State):
    print("Called B")
    return {"messages": ["Arrived at B"]}

def node_c(state: State):
    print("Called C")
    return {"messages": ["Arrived at C"]}

builder = StateGraph(State).add_node(node_a).add_node(node_b).add_node(node_c).add_edge(START, "node_a")
# No edges between nodes A, B and C. 

# Notice that the graph doesn't have conditional edges for routing! 
# This is because control flow is defined with Command inside node_a.

graph = builder.compile()

respond = graph.invoke({"messages": ["Hi"]})

print(respond)