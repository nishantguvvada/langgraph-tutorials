from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import AIMessage
from typing_extensions import TypedDict
import operator
from typing import Annotated, Any

class State(TypedDict):
    aggregate: Annotated[list, operator.add]

# class State(MessagesState):
#     pass

# class State(TypedDict):
#     aggregate: Annotated[list[AnyMessage], add_message]

def a(state: State):
    print(f"Adding A to {state["aggregate"]}")
    return { "aggregate": ["A"] }

def b(state: State):
    print(f"Adding B to {state["aggregate"]}")
    return { "aggregate": ["B"] }

def c(state: State):
    print(f"Adding C to {state["aggregate"]}")
    return {"aggregate": ["C"]}


def d(state: State):
    print(f"Adding D to {state["aggregate"]}")
    return {"aggregate": ["D"]}

def b_2(state: State):
    print(f'Adding "B_2" to {state["aggregate"]}')
    return {"aggregate": ["B_2"]}


graph_builder = StateGraph(State)
graph_builder.add_node(a).add_node(b).add_node(b_2).add_node(c).add_node(d)
# graph_builder.add_edge(START, "a").add_edge("a", "b").add_edge("a", "c").add_edge("b", "b_2").add_edge("b_2", "d").add_edge("c", "d").add_edge("d", END)
# Adding A to ['E']
# Adding B to ['E', 'A']
# Adding C to ['E', 'A']
# Adding "B_2" to ['E', 'A', 'B', 'C']
# Adding D to ['E', 'A', 'B', 'C']
# Adding D to ['E', 'A', 'B', 'C', 'B_2', 'D']
# result:  {'aggregate': ['E', 'A', 'B', 'C', 'B_2', 'D', 'D']}

# We use add_edge(["b_2", "c"], "d") here to force node "d" to only run when both nodes "b_2" and "c" have finished execution. 
# If we added two separate edges, node "d" would run twice: after node b2 finishes and once again after node c (in whichever order those nodes finish).
graph_builder.add_edge(START, "a").add_edge("a", "b").add_edge("a", "c").add_edge("b", "b_2").add_edge(["b_2","c"], "d").add_edge("d", END)
graph = graph_builder.compile()


result = graph.invoke({ "aggregate": ["E"] })
print("result: ", result)

# FOR CONDITIONAL BRANCHING

# Callback function to return the next node
# def route_bc_or_cd(state: State) -> Sequence[str]:
#     if state["which"] == "cd":
#         return ["c", "d"]
#     return ["b", "c"]


# intermediates = ["b", "c", "d"]
# builder.add_conditional_edges(
#     "a",
#     route_bc_or_cd,
#     intermediates,
# )