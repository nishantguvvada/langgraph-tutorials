from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
from typing import Annotated, List
from operator import add
import uuid

class State(BaseModel):
    messages: Annotated[List, add]

def node_a(state: State):
    return { "messages": ["Message from Node A"] }

def approval_node(state: State):
    # pause and ask for approval
    approved = interrupt(value="Do you approve this action?")
    print("Approval Node received: ", approved)

    if approved:
        print("Going to node_b")
        return Command(goto="node_b", update=["Passed through approval node"])
    else:
        print("Going to the END")
        return Command(goto=END)

def node_b(state: State):
    return { "messages": ["Message from Node B"] }

checkpointer = InMemorySaver()
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

builder = StateGraph(State).add_node("node_a", node_a).add_node("node_b", node_b).add_node("approval_node", approval_node).set_entry_point("node_a").add_edge("node_a", "approval_node")
graph = builder.compile(checkpointer=checkpointer)

response = graph.invoke({"messages": ["Hi from human"]}, config=config)
print("Initial Response: \n", response, "\n\n")
print("Interrupt Value: \n", response["__interrupt__"], "\n\n")

print("Calling resume")
response = graph.invoke(Command(resume=True), config=config)
print("Response after interrupt: \n", response)

# print("State History: \n\n", list(graph.get_state_history(config=config)))