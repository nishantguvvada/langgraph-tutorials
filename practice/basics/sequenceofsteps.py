from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage
from typing_extensions import TypedDict

class State(TypedDict):
    value_1: str
    value_2: int

# Each node can just specify the value of the key it wishes to update

def step_1(state: State):
    return { "value_1": f"a {state["value_1"]}" }

def step_2(state: State):
    current_value_1 = state["value_1"]
    return { "value_1": f"{current_value_1} b" }

def step_3(state: State):
    return { "value_2": 10 }


# To add a sequence of nodes, use .add_node and .add_edge

graph_builder = StateGraph(State)

# add nodes
graph_builder.add_node(step_1)
graph_builder.add_node(step_2)
graph_builder.add_node(step_3)

# add edges
graph_builder.add_edge(START, "step_1")
graph_builder.add_edge("step_1", "step_2")
graph_builder.add_edge("step_2", "step_3")

# or use .add_sequence([step_1, step_2, step_3]) followed by .add_edge(START, "step_1")

graph = graph_builder.compile()

# graph = StateGraph(State).add_node(node).set_entry_point("node").compile()

result = graph.invoke({ "value_1": "z" })

print("result: ", result)



