With **LangChain**, function calling becomes much more streamlined using **tools**. Here's how it works:

## Basic LangChain Function Calling

```python
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Define a tool (function)
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your weather API call here
    return f"It's 15°C and rainy in {city}"

@tool  
def calculate(expression: str) -> str:
    """Perform mathematical calculations."""
    try:
        result = eval(expression)  # Be careful with eval in production!
        return str(result)
    except:
        return "Invalid calculation"

# Set up the LLM with tools
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key="your-key"
)

# Bind tools to the model
llm_with_tools = llm.bind_tools([get_weather, calculate])

# Use it
response = llm_with_tools.invoke([
    HumanMessage(content="What's the weather in Paris and what's 25 * 4?")
])
```

## Using LangChain Agents (Recommended)

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

# Define tools
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Mock weather API
    return f"The weather in {city} is 22°C and sunny"

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Mock web search
    return f"Search results for: {query}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to} with subject '{subject}'"

# Create the agent
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to various tools."),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

tools = [get_weather, search_web, send_email]
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use the agent
result = agent_executor.invoke({
    "input": "Check the weather in Tokyo, then send an email to john@example.com about it"
})
```

## Real-World Example (Similar to Commander)

```python
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
import subprocess
import os

@tool
def run_command(command: str) -> str:
    """Execute a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"Exit code: {result.returncode}\nOutput: {result.stdout}\nError: {result.stderr}"
    except Exception as e:
        return f"Error running command: {e}"

@tool
def read_file(filename: str) -> str:
    """Read the contents of a file."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def write_file(filename: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {e}"

# Create agent with development tools
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
tools = [run_command, read_file, write_file]

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use it
result = agent_executor.invoke({
    "input": "Create a simple Python script that prints 'Hello World' and then run it"
})
```

## Key LangChain Advantages

1. **Simple tool definition** - Just use `@tool` decorator
2. **Automatic parameter extraction** - LangChain handles the JSON schema
3. **Agent orchestration** - Can chain multiple tool calls
4. **Built-in error handling** - Graceful failure management
5. **Conversation memory** - Maintains context across calls

## Comparison

**Raw API:**
```python
# You manually handle function call detection and execution
if response.function_call:
    result = execute_function(response.function_call.name, response.function_call.arguments)
    # Send result back to continue conversation
```

**LangChain:**
```python
# LangChain handles everything automatically
result = agent_executor.invoke({"input": "Do complex multi-step task"})
```

LangChain abstracts away the complexity and lets you focus on **what** your tools do rather than **how** to integrate them with the LLM!

