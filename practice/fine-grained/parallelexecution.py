# MAP REDUCE
# essential for task decomposition and parallel processing
# involves breaking task into smaller sub-task (map), processing each sub-task in parallel and aggregating results (reduce)
# In map reduce design patterns, a first node may generate a list of objects (number of objects may be unknown)
# a second node applied to all those objects (State to the downstream node should be different i.e. different State for each object)
# Use Send objects from conditional edges. Send takes 2 arguments: 1. name of the node 2. state to pass to the node (Send state differs from Graph state)

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Send
from typing_extensions import TypedDict, Annotated
from langgraph.graph import END, StateGraph, START
import operator

subjects_prompt = """Generate a comma separated list of between 2 and 5 distinct joke subjects eluded in the {topic}."""
joke_prompt = """Generate a joke about {subject}"""
best_joke_prompt = """Below are a bunch of jokes about {topic}. Select the best one! Return the ID of the best one.

{jokes}"""

class Subjects(BaseModel):
    subjects: list[str]

class Joke(BaseModel):
    joke: str

class BestJoke(BaseModel):
    id: int = Field(description="Index of the best joke, starting with 0", ge=0)

model = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key='')

# State
# 1. Overall State of the Graph
class OverallState(TypedDict):
    topic: str
    subjects: list
    jokes: Annotated[list, operator.add]
    best_selected_joke: str

# 2. State of the generate_joke node
class JokeState(TypedDict):
    subject: str

def generate_subjects(state: OverallState):
    prompt = subjects_prompt.format(topic=state["topic"])
    response = model.with_structured_output(Subjects).invoke(prompt)
    return {"subjects": response.subjects}

def generate_joke(state: JokeState):
    prompt = joke_prompt.format(subject=state["subject"])
    response = model.with_structured_output(Joke).invoke(prompt)
    return {"jokes": [response.joke]}

def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

def best_joke(state: OverallState):
    jokes = "\n\n".join(state["jokes"])
    prompt = best_joke_prompt.format(topic=state["topic"], jokes=jokes)
    response = model.with_structured_output(BestJoke).invoke(prompt)
    return {"best_selected_joke": state["jokes"][response.id]}

graph = StateGraph(OverallState)
graph.add_node("generate_subjects", generate_subjects)
graph.add_node("generate_joke", generate_joke)
graph.add_node("best_joke", best_joke)
graph.add_edge(START, "generate_subjects")
graph.add_conditional_edges("generate_subjects", continue_to_jokes, ["generate_joke"])
graph.add_edge("generate_joke", "best_joke")
graph.add_edge("best_joke", END)
app = graph.compile()

app.get_graph().draw_mermaid_png(output_file_path="./map-reduce-graph.png")

for s in app.stream({"topic": "animals"}):
    print(s)