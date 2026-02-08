from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from typing import List, Annotated
from pydantic import BaseModel
from operator import add
import uuid
import asyncio

class State(BaseModel):
    messages: Annotated[List, add]

def node_a(state: State):
    return { "messages": ["Hi from Node A"] }

def node_b(state: State):
    return { "messages": ["Hi from Node B"] }

def approval_node(state: State):
    print("Initiating approval!")
    user_decision = interrupt(value="Approve or Deny?")
    if user_decision:
        return Command(goto="node_c", update={ "messages": ["Approved by the user"] })
    else:
        return Command(goto="node_d")
    
def node_c(state: State):
    return { "messages": ["Hi from Node C"] }

def node_d(state: State):
    return { "messages": ["You are Denied!"] }

checkpointer = InMemorySaver()
thread_id = str(uuid.uuid4())
config = { "configurable": {"thread_id": thread_id} }

builder = StateGraph(State).add_node("node_a", node_a).add_node("node_b", node_b).add_node("approval_node", approval_node).add_node("node_c", node_c).add_node("node_d", node_d).set_entry_point("node_a").add_edge("node_a", "node_b").add_edge("node_b", "approval_node").add_edge("node_c", END).add_edge("node_d", END)
graph = builder.compile(checkpointer=checkpointer)

# response = graph.invoke({"messages":["Hi from Humans"]}, config)
# print(response)

async def main():
    initial_input = {"messages": ["Hi from Humans"]}
    resuming = False

    while True:
        async for metadata, mode, chunk in graph.astream(
            initial_input,
            stream_mode=["messages", "updates"],
            subgraphs=True,
            config=config
        ):

            if mode == "updates":
                print("UPDATE:", chunk)
                if "__interrupt__" in chunk:
                    decision = input("Approve or Deny? (T/F): ")
                    initial_input = Command(resume=(decision == "T"))
                    resuming = True
                    break
        else:
            # Graph ended naturally
            break

        # IMPORTANT: after resume cycle, do NOT keep resuming
        if resuming:
            resuming = False
        else:
            break

asyncio.run(main())