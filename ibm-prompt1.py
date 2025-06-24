import os
from dotenv import load_dotenv
from langchain_ibm import WatsonxLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

# Get the home directory and construct path to .env file
home_dir = os.path.expanduser("~")
env_file_path = os.path.join(home_dir, ".env")

# Load environment variables from ~/.env file
load_dotenv(env_file_path)

# Load IBM credentials from environment
ibm_api_key = os.environ.get("IBM_API_KEY")
project_id = os.environ.get("IBM_PROJECT_ID", "839fdc16-c311-4693-aaa0-120c337fe937")
url = os.environ.get("IBM_URL", "https://us-south.ml.cloud.ibm.com")

if not ibm_api_key:
    raise ValueError("IBM_API_KEY environment variable not set. Check your .env file.")

# Initialize the IBM Granite LLM
llm = WatsonxLLM(
    model_id="ibm/granite-3-8b-instruct",
    url=url,
    apikey=ibm_api_key,
    project_id=project_id,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 200,
        "min_new_tokens": 0,
        "repetition_penalty": 1
    }
)

# Create the prompt template (matching the IBM example)
security_prompt = PromptTemplate(
    input_variables=["log_entry"],
    template="""System: You are the IT security manager for a Fortune 500 company. Sometimes, a sysadmin brings you an entry from /var/log/apache2, and he wants to know if it's a security violation.
Here is a sample log line: '{log_entry}'
"""
)

# Create the chain
security_chain = security_prompt | llm | StrOutputParser()

# Function to analyze security threats
def analyze_security_threat(log_entry):
    """Analyze a log entry for security threats using IBM Granite"""
    result = security_chain.invoke({"log_entry": log_entry})
    return result

# Structured output model (optional)
class ThreatAnalysis(BaseModel):
    """Structured output for threat analysis"""
    threat: str = Field(description="Yes or No")
    explanation: str = Field(description="Brief explanation of the assessment")
    severity: str = Field(description="Low, Medium, or High if threat is Yes, otherwise N/A")

# Function for structured analysis (requires additional parsing)
def analyze_security_threat_structured(log_entry):
    """Analyze with attempted structured parsing"""
    raw_result = analyze_security_threat(log_entry)
    
    # Simple parsing logic (you might need to adjust based on actual IBM output)
    threat = "Yes" if any(word in raw_result.lower() for word in ["threat", "violation", "attack", "suspicious"]) else "No"
    
    return {
        "threat": threat,
        "explanation": raw_result.strip(),
        "severity": "Medium" if threat == "Yes" else "N/A"
    }

# Sample log entries for testing
sample_logs = [
    '107.181.141.136 - - [23/Jun/2025:00:39:32 +0000] "GET /.env HTTP/1.1" 404 456 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.140 Safari/537.36"',
    '192.168.1.100 - - [23/Jun/2025:09:15:22 +0000] "GET /login HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"',
    '10.0.0.5 - admin [23/Jun/2025:14:30:45 +0000] "POST /admin/users HTTP/1.1" 200 567 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"'
]

# Main execution
if __name__ == "__main__":
    print("IBM Granite Security Threat Analysis")
    print("=" * 50)
    
    # Test with the exact log from the IBM example
    test_log = '107.181.141.136 - - [23/Jun/2025:00:39:32 +0000] "GET /.env HTTP/1.1" 404 456 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.140 Safari/537.36"'
    
    try:
        print(f"Analyzing log: {test_log[:80]}...")
        result = analyze_security_threat(test_log)
        print(f"\nRaw Analysis:\n{result}")
        
        print("\n" + "-" * 40)
        
        # Try structured analysis
        structured_result = analyze_security_threat_structured(test_log)
        print(f"Structured Analysis:")
        print(f"Threat: {structured_result['threat']}")
        print(f"Explanation: {structured_result['explanation']}")
        print(f"Severity: {structured_result['severity']}")
        
    except Exception as e:
        print(f"Error analyzing log: {e}")
        print("Make sure you have IBM_API_KEY in your ~/.env file")

# Batch processing function
def batch_analyze_logs(log_entries):
    """Analyze multiple log entries"""
    results = []
    for i, log in enumerate(log_entries, 1):
        try:
            print(f"\nProcessing log {i}/{len(log_entries)}...")
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

# Example of batch processing (uncomment to use)
# if __name__ == "__main__":
#     batch_results = batch_analyze_logs(sample_logs)
#     for i, result in enumerate(batch_results, 1):
#         print(f"\n--- Log {i} ---")
#         print(f"Analysis: {result['analysis']}")

