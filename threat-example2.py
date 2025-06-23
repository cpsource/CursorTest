import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Get the home directory and construct path to .env file
home_dir = os.path.expanduser("~")
env_file_path = os.path.join(home_dir, ".env")

# Load environment variables from ~/.env file
load_dotenv(env_file_path)

# Load API key from environment
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set. Check your .env file or environment variables.")

# Initialize the LLM
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=api_key,
    max_tokens=20000,
    temperature=1
)

# Create the prompt template
security_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an IT professional. Occasionally, a computer administrator will send you a log entry. 
    You determine if it's a security threat or not. 
    You respond by Threat: Yes or No. 
    Explanation: A few sentences."""),
    ("user", "Is this line a security threat? {log_entry}")
])

# Advanced chain with structured output
from pydantic import BaseModel, Field

class ThreatAnalysis(BaseModel):
    """Structured output for threat analysis"""
    threat: str = Field(description="Yes or No")
    explanation: str = Field(description="Brief explanation of the assessment")
    severity: str = Field(description="Low, Medium, or High if threat is Yes, otherwise N/A")

# Structured output chain
structured_chain = security_prompt | llm.with_structured_output(ThreatAnalysis)

def analyze_security_threat_structured(log_entry):
    """Analyze with structured output"""
    result = structured_chain.invoke({"log_entry": log_entry})
    return result

# Analyze log entry
if __name__ == "__main__":
    log_entry = '107.181.141.136 - - [23/Jun/2025:00:39:32 +0000] "GET /.env HTTP/1.1" 404 456 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.140 Safari/537.36"'
    
    try:
        result = analyze_security_threat_structured(log_entry)
        print(f"Threat: {result.threat}")
        print(f"Explanation: {result.explanation}")
        print(f"Severity: {result.severity}")
        print(f"\nFull result object: {result}")
    except Exception as e:
        print(f"Error analyzing log: {e}")
