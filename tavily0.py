from langgraph import StateGraph, END
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage

# Initialize Tavily tool
search_tool = TavilySearchResults(max_results=3)

def search_node(state):
    """Node that searches for information using Tavily"""
    query = state["query"]
    search_results = search_tool.invoke(query)
    
    return {
        "search_results": search_results,
        "messages": state["messages"] + [
            HumanMessage(content=f"Search results: {search_results}")
        ]
    }

def analysis_node(state):
    """Node that analyzes the search results"""
    # Your LLM would process the search results here
    results = state["search_results"]
    # ... analysis logic
    return {"final_answer": "Analyzed response based on search"}

# Build the graph
workflow = StateGraph({
    "query": str,
    "messages": list,
    "search_results": list,
    "final_answer": str
})

workflow.add_node("search", search_node)
workflow.add_node("analyze", analysis_node)
workflow.add_edge("search", "analyze")
workflow.add_edge("analyze", END)

# Use it
app = workflow.compile()
result = app.invoke({
    "query": "latest Python 3.12 features",
    "messages": []
})
