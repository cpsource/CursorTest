#!/usr/bin/env python3
"""
Famous Person Age at Death Query Tool
Usage: 
  - In Jupyter: query_person_interactive("Albert Einstein")
  - In Python: python person_age_query.py (will prompt for input)
"""

import sys
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from typing import TypedDict
import os
import re

class PersonAgeQuery:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the query tool with Claude API."""
        if api_key:
            self.llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                api_key=api_key,
                max_tokens=1024
            )
        else:
            # Try to get from environment variable
            self.llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                max_tokens=1024
            )
        
        self.output_parser = StrOutputParser()
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "How old was {person_name} when they died? Please provide a clear, factual answer.")
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser

    def get_system_prompt(self) -> str:
        """Get the system prompt for querying person's age at death."""
        return """You are a helpful assistant that provides factual information about famous people's ages at death.

When asked about a person's age at death, provide:
1. Their exact age when they died
2. Their birth year and death year
3. The date of death if known
4. A brief context about who they were

Format your response clearly and concisely. If the person is still alive, mention that fact.
If you're not certain about the information, say so and provide what you know with appropriate caveats.

Example response format:
"[Person Name] died at age [X] in [year]. They were born in [birth year] and passed away on [death date]. [Brief description of who they were]."
"""

    def query_person_age(self, person_name: str) -> str:
        """Query Claude for a person's age at death."""
        try:
            result = self.chain.invoke({"person_name": person_name})
            return result
        except Exception as e:
            return f"Error querying information: {str(e)}"

    def extract_age_from_response(self, response: str) -> Optional[int]:
        """Extract the numerical age from Claude's response."""
        # Look for patterns like "died at age 56" or "was 56 when"
        age_patterns = [
            r'died at age (\d+)',
            r'was (\d+) when (?:he|she|they) died',
            r'age (\d+) in \d{4}',
            r'(\d+) years old when'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None

class QueryState(TypedDict):
    """State for the query workflow."""
    person_name: str
    response: str
    age: Optional[int]
    completed: bool

def create_workflow():
    """Create a LangGraph workflow for the query process."""
    
    def query_node(state: QueryState) -> QueryState:
        """Node that queries Claude for person information."""
        person_name = state["person_name"]
        query_tool = PersonAgeQuery()
        
        response = query_tool.query_person_age(person_name)
        age = query_tool.extract_age_from_response(response)
        
        return {
            "person_name": person_name,
            "response": response,
            "age": age,
            "completed": True
        }
    
    def format_output_node(state: QueryState) -> QueryState:
        """Node that formats the final output."""
        person_name = state["person_name"]
        response = state["response"]
        age = state["age"]
        
        print(f"\n{'='*50}")
        print(f"QUERY RESULT FOR: {person_name}")
        print(f"{'='*50}")
        print(f"\nClaude's Response:")
        print(f"{response}")
        
        if age:
            print(f"\nExtracted Age: {age} years old")
        else:
            print(f"\nNote: Could not extract specific age from response")
        
        print(f"\n{'='*50}")
        
        return state
    
    # Create the graph with StateGraph
    workflow = StateGraph(QueryState)
    
    # Add nodes
    workflow.add_node("query", query_node)
    workflow.add_node("format", format_output_node)
    
    # Add edges
    workflow.add_edge("query", "format")
    workflow.add_edge("format", END)
    
    # Set entry point
    workflow.set_entry_point("query")
    
    return workflow.compile()

def main():
    """Main function to run the program."""
    # Check if API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: Anthropic API key is required.")
        print("Set it via ANTHROPIC_API_KEY environment variable.")
        return
    
    # Get person name from user input (Jupyter-friendly)
    try:
        person_name = input("Enter the name of a famous person: ").strip()
        
        if not person_name:
            print("Error: Please enter a valid name.")
            return
        
        print(f"\nQuerying information for: {person_name}")
        print("Please wait...")
        
        # Create and run the workflow
        workflow = create_workflow()
        
        # Run the workflow
        result = workflow.invoke({
            "person_name": person_name,
            "response": "",
            "age": None,
            "completed": False
        })
        
    except KeyboardInterrupt:
        print("\nQuery cancelled by user.")
    except Exception as e:
        print(f"Error: {str(e)}")

def query_person_interactive(person_name: str = None):
    """
    Jupyter-friendly function to query a person's age at death.
    
    Args:
        person_name: Optional name to query. If None, will prompt for input.
        
    Example usage in Jupyter:
        query_person_interactive("Albert Einstein")
        query_person_interactive()  # Will prompt for input
    """
    if person_name is None:
        person_name = input("Enter the name of a famous person: ").strip()
    
    if not person_name:
        print("Error: Please enter a valid name.")
        return
    
    # Check if API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: Anthropic API key is required.")
        print("Set it via ANTHROPIC_API_KEY environment variable.")
        return
    
    try:
        print(f"\nQuerying information for: {person_name}")
        print("Please wait...")
        
        # Create and run the workflow
        workflow = create_workflow()
        
        # Run the workflow
        result = workflow.invoke({
            "person_name": person_name,
            "response": "",
            "age": None,
            "completed": False
        })
        
        return result
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    main()
