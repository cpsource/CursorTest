#!/usr/bin/env python3
"""
Famous Person Age at Death Query Tool
Usage: python person_age_query.py "Albert Einstein"
"""

import sys
import argparse
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import Graph, END
from langgraph.prebuilt import ToolNode
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

def create_workflow():
    """Create a LangGraph workflow for the query process."""
    
    def query_node(state):
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
    
    def format_output_node(state):
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
    
    # Create the graph
    workflow = Graph()
    
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
    parser = argparse.ArgumentParser(
        description="Query Claude for a famous person's age at death",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python person_age_query.py "Albert Einstein"
  python person_age_query.py "Ludwig van Beethoven"
  python person_age_query.py "Marie Curie"
        """
    )
    
    parser.add_argument(
        "person_name",
        help="Name of the famous person to query"
    )
    
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Check if API key is available
    if not args.api_key and not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: Anthropic API key is required.")
        print("Set it via --api-key argument or ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)
    
    try:
        # Create and run the workflow
        workflow = create_workflow()
        
        # Run the workflow
        result = workflow.invoke({
            "person_name": args.person_name,
            "response": "",
            "age": None,
            "completed": False
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

