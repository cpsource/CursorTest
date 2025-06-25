from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from typing import TypedDict
import os
from pathlib import Path

# Load environment variables from ~/.env file
try:
    from dotenv import load_dotenv
    env_path = Path.home() / '.env'
    load_dotenv(env_path)
    print(f"Loading environment variables from: {env_path}")
except ImportError:
    print("Please install: pip install python-dotenv")
    exit(1)

# Get API key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    print("⚠️  TAVILY_API_KEY not found in ~/.env file!")
    exit(1)

print("🔍 Testing Tavily clients...")

# Initialize the direct Tavily client
try:
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    print("✅ Direct Tavily client ready")
    DIRECT_CLIENT = True
except ImportError as e:
    print(f"❌ Direct Tavily client failed: {e}")
    DIRECT_CLIENT = False

# Initialize the LangChain Tavily client
try:
    from langchain_tavily import TavilySearch
    tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)
    print("✅ LangChain Tavily client ready")
    LANGCHAIN_CLIENT = True
except ImportError as e:
    print(f"❌ LangChain Tavily client failed: {e}")
    LANGCHAIN_CLIENT = False

if not DIRECT_CLIENT and not LANGCHAIN_CLIENT:
    print("Cannot proceed without at least one Tavily client")
    exit(1)

print(f"Using: {'Direct' if DIRECT_CLIENT else 'LangChain'} Tavily client")

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
        print(f"🔍 Searching for: '{query}'")
        
        # Use whichever client is available
        if DIRECT_CLIENT:
            response = tavily_client.search(query, max_results=3)
            search_results = response.get('results', [])
        elif LANGCHAIN_CLIENT:
            # TavilySearch returns results directly when invoked
            search_results = tavily_search.invoke(query)
        else:
            raise Exception("No Tavily client available")
        
        print(f"✅ Found {len(search_results)} results")
        
        return {
            **state,
            "search_results": search_results,
            "messages": state["messages"] + [
                HumanMessage(content=f"Found {len(search_results)} results for: {query}")
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
    
    print("📊 Analyzing search results...")
    print(f"Debug: Found {len(results)} results")
    
    # Debug: Print first result structure
    if results:
        print(f"Debug: First result keys: {list(results[0].keys())}")
        print(f"Debug: First result sample: {str(results[0])[:200]}...")
    
    # Check if results are valid (not error results)
    if results and len(results) > 0:
        # Check if any result has an error
        has_error = False
        for result in results:
            if isinstance(result, dict) and "error" in result:
                has_error = True
                break
        
        if not has_error:
            summaries = []
            for i, result in enumerate(results, 1):
                title = result.get("title", "No title")
                content = result.get("content", "No content")
                url = result.get("url", "No URL")
                
                # Truncate content if too long
                if len(content) > 200:
                    content = content[:200] + "..."
                    
                summaries.append(f"{i}. **{title}**")
                summaries.append(f"   {content}")
                summaries.append(f"   🔗 Source: {url}")
                summaries.append("")  # Empty line for spacing
            
            final_answer = f"🔍 **Search Results for '{state['query']}':**\n\n" + "\n".join(summaries)
            print("✅ Analysis completed successfully")
        else:
            error_msg = results[0].get("error", "Unknown error") if results else "No results returned"
            final_answer = f"❌ **Search Failed:** {error_msg}"
            print(f"❌ Analysis failed: {error_msg}")
    else:
        final_answer = f"❌ **Search Failed:** No results returned"
        print("❌ Analysis failed: No results returned")
    
    return {
        **state,
        "final_answer": final_answer
    }

def main():
    """Main function to run the LangGraph workflow"""
    
    print("🚀 Building LangGraph workflow...")
    
    # Build the LangGraph workflow
    workflow = StateGraph(GraphState)
    workflow.add_node("search", search_node)
    workflow.add_node("analyze", analysis_node)
    
    workflow.set_entry_point("search")
    workflow.add_edge("search", "analyze")
    workflow.add_edge("analyze", END)
    
    # Compile the graph
    app = workflow.compile()
    print("✅ LangGraph workflow compiled successfully")
    
    # Test queries
    test_queries = [
        "Furnished appartments to rent in San Francisco",
        "Available jobs for an Embedded AI software consultant",
        "Python 3.12 new features",
        "latest AI news 2025", 
        "best practices for LangGraph"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"🎯 Testing query: '{query}'")
        print('='*60)
        
        try:
            result = app.invoke({
                "query": query,
                "messages": [],
                "search_results": [],
                "final_answer": ""
            })
            
            print(result["final_answer"])
            print(f"\n📈 Stats: {len(result['search_results'])} results, {len(result['messages'])} messages")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        print("\n" + "="*60)
        
        # Ask if user wants to continue
        if query != test_queries[-1]:  # Not the last query
            continue_test = input("\nPress Enter to continue to next query, or 'q' to quit: ")
            if continue_test.lower() == 'q':
                break
    
    print("\n🎉 LangGraph with Tavily demo completed!")

if __name__ == "__main__":
    main()
