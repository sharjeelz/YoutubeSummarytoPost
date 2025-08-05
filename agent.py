from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
import math
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and return the result."""
    return a * b

def divide(a: int, b: int) -> float:
    """Divide two numbers and return the result."""
    return a / b

def sqrt(a: float) -> float:
    """Compute the square root of a number."""
    if a < 0:
        raise ValueError("Cannot take square root of a negative number.")
    return math.sqrt(a)
def subscract(a: int, b: int) -> int:
    """Subtract two numbers and return the result."""
    return a - b
def mod(a: int, b: int) -> int:
    """Calculate the remainder of two numbers and return the result."""
    return a % b

def factorial(n: int) -> int:
    """Calculate the factorial of a number."""
    if n < 0:
        raise ValueError("Cannot calculate factorial of a negative number.")
    if n == 0:
        return 1
    return n * factorial(n - 1)

tools = [add, multiply, divide, sqrt]

# LLM with tool binding
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# System message to guide behavior
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Assistant node logic
def assistant(state: MessagesState):
    return {
        "messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]
    }

# Build LangGraph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define flow logic
from langgraph.graph import START
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# Compile
graph = builder.compile()

# Run it
if __name__ == "__main__":
    input_msg = HumanMessage(content="fictorial of 3")
    result = graph.invoke({"messages": [input_msg]})

    print("\nConversation:")
    for m in result["messages"]:
        print(f"\n{m.type.upper()}:\n{m.content}")
