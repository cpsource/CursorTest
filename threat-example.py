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

# Create the chain
security_chain = security_prompt | llm | StrOutputParser()

# Example usage function
def analyze_security_threat(log_entry):
    """Analyze a log entry for security threats"""
    result = security_chain.invoke({"log_entry": log_entry})
    return result

# Example log entries to test
sample_logs = [
    '107.181.141.136 - - [23/Jun/2025:00:39:32 +0000] "GET /.env HTTP/1.1" 404 456 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.140 Safari/537.36"',
    '192.168.1.100 - - [23/Jun/2025:09:15:22 +0000] "GET /login HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"',
    '10.0.0.5 - admin [23/Jun/2025:14:30:45 +0000] "POST /admin/users HTTP/1.1" 200 567 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"'
]

# Analyze each log entry
if __name__ == "__main__":
    print("Security Threat Analysis Results:")
    print("=" * 50)
    
    for i, log in enumerate(sample_logs, 1):
        print(f"\nLog Entry {i}:")
        print(f"Raw Log: {log}")
        print("Analysis:")
        
        try:
            analysis = analyze_security_threat(log)
            print(analysis)
        except Exception as e:
            print(f"Error analyzing log: {e}")
        
        print("-" * 40)

# Batch processing function
def batch_analyze_logs(log_entries):
    """Analyze multiple log entries at once"""
    results = []
    for log in log_entries:
        try:
            analysis = analyze_security_threat(log)
            results.append({
                "log": log,
                "analysis": analysis
            })
        except Exception as e:
            results.append({
                "log": log,
                "analysis": f"Error: {e}"
            })
    return results

# Advanced chain with structured output (optional)
from langchain_core.pydantic_v1 import BaseModel, Field

class ThreatAnalysis(BaseModel):
    """Structured output for threat analysis"""
    threat: str = Field(description="Yes or No")
    explanation: str = Field(description="Brief explanation of the assessment")
    severity: str = Field(description="Low, Medium, or High if threat is Yes, otherwise N/A")

# Structured output chain (uncomment to use)
# structured_chain = security_prompt | llm.with_structured_output(ThreatAnalysis)

# def analyze_security_threat_structured(log_entry):
#     """Analyze with structured output"""
#     result = structured_chain.invoke({"log_entry": log_entry})
#     return result

