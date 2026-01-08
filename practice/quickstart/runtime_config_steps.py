from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig
from langgraph.managed import RemainingSteps
from dataclasses import dataclass

class State(TypedDict):
    messages: str
    remaining_steps: RemainingSteps

@dataclass
class ContextSchema:
    llm_provider: str = "open-ai"

def example_node(state: State, runtime: Runtime[ContextSchema], config: RunnableConfig):
    print("Current Step Counter", config["metadata"]["langgraph_step"])
    print("Remaining Step", state["remaining_steps"])
    return { "messages": f"From node with {runtime.context.llm_provider}" }

graph = StateGraph(State, context_schema=ContextSchema).add_node("example_node", example_node).set_entry_point("example_node").compile()

output = graph.invoke({"messages": "Hi"}, context={"llm_provider": "anthropic"})
print(output)