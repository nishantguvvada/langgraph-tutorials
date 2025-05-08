# Add runtime configuration to your graph to configure your agent when calling it
# Any configuration information needs to be passed inside configurable key

from langgraph.graph import MessagesState
from langgraph.graph import END, StateGraph, START
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

class AgentState(MessagesState):
    pass

models = {
    "anthropic": "open source",
    "openai": "private",
}

# config is meant to contain things are not part of the input (and therefore that we don't want to track as part of the state)
def _call_model(state: AgentState, config: RunnableConfig): 
    # response = model.invoke(state["messages"])
    # Access the config through the configurable key
    model_name = config["configurable"].get("model", "anthropic")
    response = models[model_name]
    return {"messages": AIMessage(f"Response from {response} model")}

builder = StateGraph(AgentState).add_node(_call_model).set_entry_point("_call_model")
graph = builder.compile()

result = graph.invoke({"messages": HumanMessage("Hello from human!")}, {"configurable": {"model": "openai"}})
print(result)

# We can define a config schema to specify the configuration options for the graph
# A config schema is useful for indicating which fields are available in the configurable dict inside the config

# class ConfigSchema(TypedDict):
#     model: Optional[str]
#     system_message: Optional[str]


# def _call_model(state: AgentState, config: RunnableConfig):
#     # Access the config through the configurable key
#     model_name = config["configurable"].get("model", "anthropic")
#     model = models[model_name]
#     messages = state["messages"]
#     if "system_message" in config["configurable"]:
#         messages = [
#             SystemMessage(content=config["configurable"]["system_message"])
#         ] + messages
#     response = model.invoke(messages)
#     return {"messages": [response]}

# workflow = StateGraph(AgentState, ConfigSchema)