from langchain.messages import AnyMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.types import Overwrite
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
import operator

# class State(TypedDict):
#     # messages: Annotated[AnyMessage, operator.add]
#     messages: Annotated[AnyMessage, add_messages]
#     extra_field: int

# class State(MessagesState):
#     extra_field: int

# def node(state: State):
#     messages = state["messages"]
#     new_message = AIMessage("Hello from AI")
#     return { "messages": [new_message], "extra_field": 10 }

# builder = StateGraph(State)
# builder.add_node("node", node)
# builder.set_entry_point("node")
# graph = builder.compile()

# def add_first_message(state: State):
#     output = AIMessage(["first_message"])
#     return { "messages": output }

# def add_second_message(state: State):
#     print("first node: ", state["messages"])
#     return { "messages": AIMessage(["second_message"]) }

# def replace_message(state: State):
#     print("second node: ", state["messages"])
#     return { "messages": Overwrite(["replaced_message"]) }

# builder = StateGraph(State)
# builder.add_node("first", add_first_message)
# builder.add_node("second", add_second_message)
# builder.add_node("replace", replace_message)
# builder.set_entry_point("first")
# builder.add_edge("first", "second")
# builder.add_edge("second", "replace")
# graph = builder.compile()

# result = graph.invoke({ "messages": ["initial_message"]})

# result = graph.invoke({ "messages": [HumanMessage("Hi from Human")]})
# print(result)

# for message in result["messages"]:
#     message.pretty_print()

# class InputState(TypedDict):
#     question: str

# class OutputState(TypedDict):
#     answer: str

# class OverallState(InputState, OutputState):
#     pass

# class State(TypedDict):
#     message: str

# def answer_question(state: InputState):
#     return { "answer": "bye", "question": state["question"] }

# builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
# builder.add_node("answer_question", answer_question)
# builder.set_entry_point("answer_question")
# graph = builder.compile()

# print(graph.invoke({ "question": "Hi" }))

class PrivateState(TypedDict):
    private: str
    flag: bool

class GeneralState(TypedDict):
    messages: Annotated[AnyMessage, operator.add]

def node_a(state: GeneralState):
    extracted_input = state['messages']
    return { "private": f"PRIVATE MESSAGE: `{extracted_input}`", "flag": False }

def node_b(state: PrivateState):
    if state["flag"]:
        return { "messages": AIMessage(["End of message: No Secret Message"])}
    else:
        return { "messages": AIMessage([f"SECRET MESSAGE: {state["private"]}"])}
    
builder = StateGraph(GeneralState).add_node("a", node_a).add_node("b", node_b).set_entry_point("a")
builder.add_edge("a", "b")
graph = builder.compile()

print(graph.invoke({ "messages": HumanMessage(["Hi from Human"]) }))