# When creating a graph with a loop, we require a mechanism to terminate execution
# This is most commonly done by adding a conditional edge that routes to the END node

import operator
from typing import Annotated, Literal

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    aggregate: Annotated[list, operator.add]

def a(state: State):
    print(f"Node A sees {state["aggregate"]}")
    return { "aggregate": ["A"] }

def b(state: State):
    print(f"Node B sees {state["aggregate"]}")
    return { "aggregate": ["B"] }


def c(state: State):
    print(f'Node C sees {state["aggregate"]}')
    return {"aggregate": ["C"]}


def d(state: State):
    print(f'Node D sees {state["aggregate"]}')
    return {"aggregate": ["D"]}

builder = StateGraph(State).add_node(a).add_node(b).add_node(c).add_node(d)

def route(state: State):
    if len(state["aggregate"]) < 7:
        return "b"
    else:
        return END
    
builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b","c")
builder.add_edge("b","d")
builder.add_edge(["c","d"], "a")
graph = builder.compile()

result = graph.invoke({ "aggregate": [] })

# Reaching a given termination condition is not guaranteed, we can set graph recursion limit, this will raise a GraphRecursionError after a given number of supersteps
from langgraph.errors import GraphRecursionError

try:
    graph.invoke({"aggregate": []}, {"recursion_limit": 4})
except GraphRecursionError:
    print("Recursion Error")