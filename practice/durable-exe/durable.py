# There are 3 durability modes in LangGraph.
# exit - LangGraph stores/saves the state at the end of the graph execution i.e. intermediate steps are not saved (Only 1 StateSnapshot object will be available in the history)
# async - LangGraph stores/saves the state at every workflow step asynchronously while the next step executes. The risk of unsaved checkpoints if process crashed during execution.
# sync - LangGraph stores/saves the state at every workflow step synchronously before the next step executes. Stores all the checkpoints but has performance overhead
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import task
from typing import TypedDict, Annotated
from operator import add
import uuid
import time

class State(TypedDict):
    messages: Annotated[list, add]

def node_a(state: State):
    return { "messages": ["Message from Node A"] }

@task
def expensive_operation():
    time.sleep(2)
    print("Within Task")
    return "Output From Task"

def node_b(state: State):
    # time.sleep(2) # sleep for 2 seconds to mock expensive operation
    # Use task for side effects (file writes, DB writes, API calls etc.)
    response = expensive_operation()
    print(response)
    print(response.result())
    return { "messages": ["Message from Node B"] }

def node_c(state: State):
    return { "messages": ["Message from Node C"] }


builder = StateGraph(State)
builder.add_node("node_a", node_a).add_node("node_b", node_b).add_node("node_c", node_c).set_entry_point("node_a").add_edge("node_a", "node_b").add_edge("node_b", "node_c")

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

thread_id = str(uuid.uuid4())
config = { "configurable": { "thread_id": thread_id }}

response = graph.invoke({"messages": ["Message from Human"]}, config=config, durability='exit')
print("Response: \n\n", response)

history = graph.get_state_history(config=config)
print("History: \n\n", list(history))