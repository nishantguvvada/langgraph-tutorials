from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
from typing import Annotated
from operator import add

class State(BaseModel):
    messages: Annotated[list, add]

def node_a(state: State):
    return { "messages": ["message from node A"] }

def node_b(state: State):
    return { "messages": ["message from node B"] }

checkpointer = InMemorySaver()
graph = StateGraph(State).add_node("node_a", node_a).add_node("node_b", node_b).set_entry_point("node_a").add_edge("node_a", "node_b").add_edge("node_b", END).compile(checkpointer=checkpointer)

response = graph.invoke({ "messages": ["message from human"] }, { "configurable": { "thread_id": 1 } })

print(response)

# Get State using get_state() method
print("Checkpoint: \n", graph.get_state({"configurable": {"thread_id": 1}}))

# Get full state history using get_state_history()
history = list(graph.get_state_history({"configurable": {"thread_id": 1}}))
print("State History: \n", history)

# Re-play: play back a prior graph execution, if we invoke a graph with a thread ID and a checkpoint ID, we replay 
# the previously executed steps before the checkpoint corresponding to the checkpoint ID.
# Langgraph knows whether a particular step is executed, if it has, it simply replays the step and does not re-execute it. All the steps after the checkpoint will be executed.

checkpoint_id = history[1].config["configurable"]["checkpoint_id"]
print("ID: ", checkpoint_id)
print("Re-play: \n", graph.invoke(None, {"configurable": {"thread_id": 1, "checkpoint_id": checkpoint_id}}))


# Update/edit the graph state using update_state() method

print("Update State: \n", graph.update_state({"configurable": {"thread_id": 1}}, { "messages": ["updated message"] }, "node_a"))
history = list(graph.get_state_history({"configurable": {"thread_id": 1}}))
print("State History: \n", history)

# response = graph.invoke({ "messages": ["new message from human"] }, { "configurable": { "thread_id": 1 } })

# print(response)

# Memory Store: Retain information across threads

from langgraph.store.memory import InMemoryStore
import uuid

in_memory_store = InMemoryStore()
memory_id = str(uuid.uuid4())

# Memories are namespaced by a tuple
namespace_for_memory = ("1", "memories")
memory = {"food_preference": "Pizza"}

# Use put() to store memory
in_memory_store.put(namespace_for_memory, memory_id, memory)

# Read memories from the store using store.search
memories = in_memory_store.search(namespace_for_memory)
# print(memories[-1].dict())

# Semantic Search: beyond simple retrieval, store supports semantic search
# from langchain.embeddings import init_embeddings
# from dotenv import load_dotenv
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# import os

# load_dotenv()

# embeddings = GoogleGenerativeAIEmbeddings(
#     model="text-embedding-004",
#     google_api_key=os.getenv('GEMINI_API_KEY')
# )


# new_store = InMemoryStore(
#     index={
#         "embed": init_embeddings('google_genai:gemini-embedding-001'),  # Embedding provider
#         "dims": 1536,                              # Embedding dimensions
#         "fields": ["food_preference", "$"]              # Fields to embed
#     }
# )

# new_store.put(namespace_for_memory, memory_id, memory)

# memories = new_store.search(namespace_for_memory, query="what does the user like to eat?", limit=3)
# print("Semantically Searched Memories: \n", memories)
"""
# Store with specific fields to embed
store.put(
    namespace_for_memory,
    str(uuid.uuid4()),
    {
        "food_preference": "I love Italian cuisine",
        "context": "Discussing dinner plans"
    },
    index=["food_preference"]  # Only embed "food_preferences" field
)

# Store without embedding (still retrievable, but not searchable)
store.put(
    namespace_for_memory,
    str(uuid.uuid4()),
    {"system_info": "Last updated: 2024-01-01"},
    index=False
)
"""

# Using store and checkpointer in LangGraph

# graph = graph.compile(checkpointer=checkpointer, store=in_memory_store)

# user_id = "1"
# config = {"configurable": {"thread_id": "1", "user_id": user_id}}

# graph.invoke({"messages": [{"role": "user", "content": "hi"}]}, config)

# # We can access the store and user_id in any node using store: BaseStore and config: RunnableConfig

# def update_memory(state: State, config: RunnableConfig, *, store: BaseStore):

#     user_id = config["configurable"]["user_id"]
#     namespace = (user_id, "memories")
#     memory_id = str(uuid.uuid4())

#     store.put(namespace, memory_id, { "memory": { "food preference": "Pizza" } })