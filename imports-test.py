print('Testing imports...')

try:
    from tavily import TavilyClient
    print('✅ tavily-python works')
except ImportError as e:
    print(f'❌ tavily-python failed: {e}')

try:
    from langchain_tavily import TavilySearchAPIWrapper
    print('✅ langchain-tavily works')
except ImportError as e:
    print(f'❌ langchain-tavily failed: {e}')

try:
    from langgraph.graph import StateGraph, END
    print('✅ langgraph works')
except ImportError as e:
    print(f'❌ langgraph failed: {e}')
