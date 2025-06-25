from langgraph.graph import StateGraph, END
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from typing import TypedDict
import os

# Set your Tavily API key
os.environ["TAVILY_API_KEY"] = "your-tavily-api-key-here"

# Define the state schema
class GraphState(TypedDict):
    query: str
    messages: list
    search_results: list
    final_answer: str

# Initialize Tavily tool
search_tool = TavilySearchResults(max_results=3)

def search_node(state: GraphState) -> GraphState:
    """Node that searches for information using Tavily"""
    query = state["query"]
    search_results = search_tool.invoke(query)
    
    return {
        **state,  # Preserve existing state
        "search_results": search_results,
        "messages": state["messages"] + [
            HumanMessage(content=f"Search results: {search_results}")
        ]
    }

def analysis_node(state: GraphState) -> GraphState:
    """Node that analyzes the search results"""
    results = state["search_results"]
    # Simple analysis - in practice, you'd use an LLM here
    summary = f"Found {len(results)} results about: {state['query']}"
    
    return {
        **state,
        "final_answer": summary
    }

# Build the graph
workflow = StateGraph(GraphState)
workflow.add_node("search", search_node)
workflow.add_node("analyze", analysis_node)

# Set entry point and edges
workflow.set_entry_point("search")
workflow.add_edge("search", "analyze")
workflow.add_edge("analyze", END)

# Compile and use
app = workflow.compile()

# Test it
if __name__ == "__main__":
    result = app.invoke({
        "query": "latest Python 3.12 features",
        "messages": [],
        "search_results": [],
        "final_answer": ""
    })
    
    print("Final Answer:", result["final_answer"])
    print("Search Results:", result["search_results"])

