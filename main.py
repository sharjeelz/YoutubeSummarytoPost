from langgraph.graph import StateGraph
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda
from dotenv import load_dotenv
from typing import TypedDict
import os

load_dotenv()

class AppState(TypedDict):
    url: str
    transcript: str
    summary: str
    post: str

# Step 1: Define State
initial_state = {
    "url": None,
    "transcript": None,
    "summary": None,
    "post": None
}

# Step 2: Define Node Functions
def fetch_transcript(state: AppState) -> AppState:
    url = state["url"]
    if "v=" in url:
        video_id = url.split("v=")[-1].split("&")[0]
    elif "youtu.be" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL format")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        raise RuntimeError(f"Transcript fetch failed: {e}")

    full_text = " ".join([entry['text'] for entry in transcript])
    state["transcript"] = full_text
    return state

def summarize_transcript(state: AppState) -> AppState:
    transcript = state["transcript"]
    # print(transcript)  # Debugging: Print the transcript
    prompt = PromptTemplate.from_template("Summarize the following YouTube transcript:\n{transcript}\n gont squeeze the summary, let is be as elborative as possible")
    chain = prompt | ChatOpenAI()
    summary = chain.invoke({"transcript": transcript})
    state["summary"] = summary.content
    return state

def generate_post(state: AppState) -> AppState:
    summary = state["summary"]
    print(summary)  # Debugging: Print the summary
    post_prompt = PromptTemplate.from_template("Create a post for linked in on this summary:\n{summary}")
    chain = post_prompt | ChatOpenAI()
    post = chain.invoke({"summary": summary})
    state["post"] = post.content
    return state

# Step 3: Define LangGraph
builder = StateGraph(AppState)
builder.add_node("fetch_transcript", RunnableLambda(fetch_transcript))
builder.add_node("summarize_transcript", RunnableLambda(summarize_transcript))
builder.add_node("generate_post", RunnableLambda(generate_post))

builder.set_entry_point("fetch_transcript")
builder.add_edge("fetch_transcript", "summarize_transcript")
builder.add_edge("summarize_transcript", "generate_post")
builder.set_finish_point("generate_post")

# Step 4: Compile Graph
app = builder.compile()

# Step 5: Run
if __name__ == "__main__":
    input_state = initial_state.copy()
    print(input_state)
    input_state["url"] = "https://www.youtube.com/watch?v=TQjLFNpu4r8"  # Replace with actual video
    print(input_state)
    result = app.invoke(input_state)
    print("\nGenerated Social Media Post:\n")
    print(result["post"])
