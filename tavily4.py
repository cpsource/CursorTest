from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from typing import TypedDict
import os
from pathlib import Path

# Load environment variables from ~/.env file
try:
    from dotenv import load_dotenv
    
    # Load from ~/.env file
    env_path = Path.home() / '.env'
    load_dotenv(env_path)
    print(f"Loading environment variables from: {env_path}")
    
except ImportError:
    print("Please install: pip install python-dotenv")
    exit(1)

# Now get the API key from environment
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    print("⚠️  TAVILY_API_KEY not found in ~/.env file!")
    print("Create ~/.env file with:")
    print("TAVILY_API_KEY=tvly-your-actual-key-here")
    exit(1)

# Use the direct tavily-python client
try:
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    print("✅ Tavily client initialized successfully")
except ImportError:
    print("Please install: pip install tavily-python")
    exit(1)

# Define the state schema
class GraphState(TypedDict):
    query: str
    messages: list
    search_results: list
    final_answer: str

def search_node(state: GraphState) -> GraphState:
    """Node that searches for information using Tavily"""
    query = state["query"]
    
    try:
        # Use Tavily client directly
        response = tavily_client.search(query, max_results=3)
        search_results = response.get('results', [])
        
        print(f"✅ Search completed: found {len(search_results)} results")
        
        return {
            **state,
            "search_results": search_results,
            "messages": state["messages"] + [
                HumanMessage(content=f"Found {len(search_results)} results")
            ]
        }
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return {
            **state,
            "search_results": [{"error": str(e)}],
            "messages": state["messages"] + [
                HumanMessage(content=f"Search failed: {e}")
            ]
        }

def analysis_node(state: GraphState) -> GraphState:
    """Node that analyzes the search results"""
    results = state["search_results"]
    
    if results and not any("error" in str(result) for result in results):
        summaries = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            content = result.get("content", "No content")
            url = result.get("url", "No URL")
            
            # Truncate content if too long
            if len(content) > 300:
                content = content[:300] + "..."
                
            summaries.append(f"{i}. **{title}**\n   {content}\n   Source: {url}\n")
        
        final_answer = f"Search results for '{state['query']}':\n\n" + "\n".join(summaries)
    else:
        final_answer = "Search failed or returned no results"
    
    return {
        **state,
        "final_answer": final_answer
    }

# Build the graph
workflow = StateGraph(GraphState)
workflow.add_node("search", search_node)
workflow.add_node("analyze", analysis_node)

workflow.set_entry_point("search")
workflow.add_edge("search", "analyze")
workflow.add_edge("analyze", END)

app = workflow.compile()

if __name__ == "__main__":
    print("🚀 Starting LangGraph with Tavily search...")
    
    result = app.invoke({
        "query": "Python 3.12 new features",
        "messages": [],
        "search_results": [],
        "final_answer": ""
    })
    
    print("=" * 60)
    print(result["final_answer"])
    print("=" * 60)

