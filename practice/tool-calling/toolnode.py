# Use LangGraph's prebuilt ToolNode

# ToolNode is a LangChain Runnable that takes graph state and outputs state update with the result  of tool calls.
# ToolNode works well with LangGraph's prebuilt ReAct agent
# ToolNode also works with StateGraph as long as state has messages key with reduce (MessagesState)

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

@tool
def get_weather(location: str):
    """ Call to get the current weather """
    if location.lower() in ["sf", "san francisco"]:
        return "It's 60 degrees and foggy"
    else:
        return "It's 90 degrees and sunny"
    
@tool
def get_coolest_cities():
    """ Get a list of coolest cities """
    return "nyc, sf"

tools = [get_weather, get_coolest_cities]
tool_node = ToolNode(tools)

# ToolNode operates on graph state with a list of messages
# It expects the last message in the list to be an AIMessage with tool_calls parameter.

# message_with_single_tool_call = AIMessage(
#     content='',
#     tool_calls=[
#         {
#             "name": "get_weather",
#             "args": {"location":"sf"},
#             "id": "tool_call_id",
#             "type": "tool_call"
#         }
#     ]
# )

message_with_multiple_tool_calls = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "get_coolest_cities",
            "args": {},
            "id": "tool_call_id_1",
            "type": "tool_call",
        },
        {
            "name": "get_weather",
            "args": {"location": "sf"},
            "id": "tool_call_id_2",
            "type": "tool_call",
        },
    ],
)

# result = tool_node.invoke({"messages": [message_with_multiple_tool_calls]})

# print(result)

llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key='')

model_with_tools = llm.bind_tools(tools)

# print(model_with_tools.invoke("what's the weather in sf?").tool_calls)

# print(tool_node.invoke({"messages": [model_with_tools.invoke("what's the weather in sf?")]}))

from langgraph.graph import StateGraph, MessagesState, START, END

class State(MessagesState):
    pass

def call_model(state: State):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    else:
        return END

graph = StateGraph(State).add_node("agent", call_model).add_node("tools", tool_node).set_entry_point("agent").add_conditional_edges("agent", should_continue, ["tools", END]).add_edge("tools", "agent")
app = graph.compile()

for chunk in app.stream(
    {"messages": [HumanMessage("what's the weather in the coolest cities?")]}, stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
