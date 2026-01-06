from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite', api_key=os.getenv('GEMINI_API_KEY'), temperature=0)

# Define tools
@tool
def multiply(a:int, b:int) -> int:
    """
    Multiply `a` and `b`
    
    :param a: First int
    :type a: int
    :param b: Second int
    :type b: int
    :return: multiplication result
    :rtype: int
    """
    
    return a * b

@tool
def add(a:int, b:int) -> int:
    """
    Adds `a` and `b`.
    
    :param a: First int
    :type a: int
    :param b: Second int
    :type b: int
    :return: addition result
    :rtype: int
    """

    return a + b

@tool
def divide(a:int, b:int) -> float:
    """
    Divide `a` and `b`.
    
    :param a: First int
    :type a: int
    :param b: Second int
    :type b: int
    :return: division result
    :rtype: float
    """

    return a / b

tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)

# Define state
# graph's state stores messages and number of LLM calls, it persists throughout agent execution

from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator

class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    node: Annotated[str, operator.add]
    llm_calls: int

# Define model node

from langchain.messages import SystemMessage

def llm_call(state: MessageState):
    
    """LLM decides whether to call a tool or not"""

    response = model_with_tools.invoke(
        [
            SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set a inputs.")
        ] + state["messages"]
    )

    return {
        "messages": [response], 
        "llm_calls": state.get('llm_calls', 0) + 1,
        "node": "llm_call"
    }

# Define tool node

from langchain.messages import ToolMessage

def tool_node(state: MessageState):
    result = []
    for tool_call in state["messages"][-1].tool_calls: # If the last message contains tool_calls
        tool = tools_by_name[tool_call["name"]] # extract name from tool_call and fetch the tool from tools_by_name dictionary
        observation = tool.invoke(tool_call["args"]) # extract args from tool_call and invoke the tool
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return { "messages": result, "node": "tool_node" }

# Define routing logic

from typing import Literal
from langgraph.graph import StateGraph, START, END

def should_continue(state: MessageState) -> Literal["tool_node", END]:

    last_message = state["messages"][-1]

    if last_message.tool_calls: # If the last message contains tool_calls, call the tool_node
        return "tool_node"
    
    return END

# Build and compile the agent

# workflow
agent_builder = StateGraph(MessageState)

# add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# add edge
agent_builder.set_entry_point("llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, {"tool_node":"tool_node", END:END})
agent_builder.add_edge("tool_node", "llm_call")

agent = agent_builder.compile()

# agent.get_graph().draw_mermaid_png(output_file_path="./quickstart.png")

from langchain.messages import HumanMessage
messages = [HumanMessage(content="Add 3 and 4.")]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    # m.pretty_print()
    print(m)