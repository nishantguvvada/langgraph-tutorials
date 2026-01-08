# LangGraph supports caching of tasks/nodes. To use caching:
# 1. specify cache when compiling the graph
# 2. specify cache policy for the node

import time
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

class State(TypedDict):
    x: int
    result: int

builder = StateGraph(State)

def expensive_node(state: State):
    time.sleep(2)
    return { "result": state["x"] * 2}

builder.add_node("expensive_node", expensive_node, cache_policy=CachePolicy(ttl=3))
builder.set_entry_point("expensive_node")
builder.set_finish_point("expensive_node")

graph = builder.compile(cache=InMemoryCache())

print(graph.invoke({ "x": 5 }, stream_mode="updates"))
print("\n"*5)
print(graph.invoke({ "x": 5 }, stream_mode="updates"))