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

