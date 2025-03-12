# Update Graph State from Nodes

# State in Langgraph can be TypedDict, Pydantic or dataclass
# By default, graphs will have same input and output schema and state determines that schema

from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict

class State(TypedDict):
    messages: list[AnyMessage]
    extra_field: int

# Define graph structure
# a graph with a single node (a node is a python function that reads graph state and makes updates to it)

from langchain_core.messages import AIMessage

def node(state: State):
    messages = state["messages"]
    new_message = AIMessage("Hello!")

    return {"messages": messages + [new_message], "extra_field": 10} # manually appending the new message to the state["messages"] list

# Define StateGraph

from langgraph.graph import StateGraph

graph_builder = StateGraph(State)
graph_builder.add_node(node)
graph_builder.set_entry_point("node")
graph = graph_builder.compile()

# Simple invocation

from langchain_core.messages import HumanMessage

result = graph.invoke({"messages": [HumanMessage("Hi")]})
print("result: ", result)

# inspect the messages
for message in result["messages"]:
    message.pretty_print()

# Process state updates with reducers
# each key in the state can have it's own reducer function which controls how updates from nodes are applied.
# WITHOUT reducer specified it is assumed all updates to the key should override it

from typing_extensions import Annotated

def add(left, right):
    return left + right

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add]
    extra_field: int

def node(state: State):
    new_message = AIMessage("Hello again from AI")
    return {"messages": [new_message], "extra_field": 10} # removed the append new message logic
    # the returned message from the node gets parsed to the add reducer

from langgraph.graph import START

# graph_builder = StateGraph(State)
# graph_builder.add_node(node)
# graph_builder.add_edge(START, "node") # equivalent to set_entry_point()
# graph = graph_builder.compile()

graph = StateGraph(State).add_node(node).set_entry_point("node").compile()

result = graph.invoke({"messages": [HumanMessage("Hi")]})

print("result with reducer: ", result)

for message in result["messages"]:
    message.pretty_print()

# Instead of creating a reducer (add function created above), langgraph's built-in reducer: add_messages can be used

# from langgraph.graph.message import add_messages

# class State(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]
#     extra_field: int

# a pre-built MessagesState from langgraph includes the reducer function
# the State class is updated to not include messages now

from langgraph.graph import MessagesState

class State(MessagesState):
    extra_field: int

def node(state: State):
    new_message = AIMessage("Hello for the 3rd time!")
    return { "messages": [new_message], "extra_field": 20 }

graph = StateGraph(State).add_node(node).set_entry_point("node").compile()

# result = graph.invoke({"messages": [HumanMessage("Hi")]})
input_message = {"role": "user", "content": "Hi"} # equivalent to HumanMessage("Hi")

result = graph.invoke({"messages": [input_message]})

print("result from add_message: ", result)

for message in result["messages"]:
    message.pretty_print()