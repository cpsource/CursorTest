import os
from dotenv import load_dotenv
from langchain import hub
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
home_dir = os.path.expanduser("~")
env_file_path = os.path.join(home_dir, ".env")
load_dotenv(env_file_path)

# Set up LangSmith API key (if you want to use LangSmith features)
langsmith_api_key = os.environ.get("LANGSMITH_API_KEY")
if langsmith_api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key

# Method 1: Pull the prompt directly from LangChain Hub
try:
    # Pull the chain-of-density prompt from the hub
    prompt = hub.pull("nicobutes/chain-of-density-prompt")
    print("Successfully pulled prompt from LangChain Hub!")
    print(f"Prompt type: {type(prompt)}")
    print(f"Prompt template: {prompt}")
except Exception as e:
    print(f"Error pulling from hub: {e}")
    print("Creating manual version of chain-of-density prompt...")
    
    # Method 2: Manual recreation based on chain-of-density technique
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at creating increasingly dense summaries. You will be given an article and need to create 5 increasingly dense summaries of the same length (~50 words each), where each iteration adds more specific details and entities while maintaining the same word count.

Follow this process:
1. First summary: High-level overview with minimal entities
2. Second summary: Add 1-2 key entities/details
3. Third summary: Add 2-3 more specific entities/details  
4. Fourth summary: Add 2-3 more entities/details
5. Fifth summary: Maximum density with all key entities/details

Each summary should be approximately 50 words and progressively more informative."""),
        ("user", "Article to summarize:\n\n{article}")
    ])

# Set up the LLM 
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=api_key,
    max_tokens=1000,
    temperature=0.3
)

# Create the chain
chain = prompt | llm | StrOutputParser()

# Function to use the chain-of-density prompt
def create_dense_summaries(article_text):
    """Create increasingly dense summaries using chain-of-density technique"""
    result = chain.invoke({"article": article_text})
    return result

# Example usage
if __name__ == "__main__":
    # Example article for testing
    sample_article = """
    Artificial Intelligence (AI) has experienced remarkable growth in recent years, particularly with the advent of large language models like GPT-4 and Claude. These models have demonstrated unprecedented capabilities in natural language understanding, code generation, and complex reasoning tasks. The technology has found applications across numerous industries, from healthcare and finance to education and entertainment.

    However, the rapid advancement of AI has also raised important questions about safety, ethics, and the future of work. Researchers and policymakers are grappling with how to ensure AI systems remain beneficial and aligned with human values as they become more powerful. The development of AI safety research has become a critical priority, with organizations like Anthropic, OpenAI, and DeepMind investing heavily in this area.

    The economic impact of AI is projected to be substantial, with some estimates suggesting it could contribute trillions of dollars to global GDP over the next decade. At the same time, concerns about job displacement have led to discussions about retraining programs and new social safety nets. As AI continues to evolve, society must navigate the balance between harnessing its benefits and mitigating potential risks.
    """
    
    print("Creating chain-of-density summaries...")
    print("=" * 60)
    
    try:
        summaries = create_dense_summaries(sample_article)
        print(summaries)
    except Exception as e:
        print(f"Error creating summaries: {e}")

# Alternative: Direct API call to LangSmith (if you have access)
def get_playground_directly():
    """
    Alternative method if you have LangSmith API access
    You would need to inspect the network requests in the browser
    to see the exact API endpoints being used
    """
    # This would require LangSmith API access and the specific organization permissions
    # The URL suggests it's from organization ID: fba4452d-b6f9-4302-b4ba-5afde3d26118
    pass

# Method 3: Manual prompt extraction
# If you can't access the hub, you can manually recreate the prompt
# by looking at the playground interface and copying the prompt template

print("\nTo use this playground:")
print("1. Set ANTHROPIC_API_KEY in your ~/.env file")
print("2. Optionally set LANGSMITH_API_KEY for tracing")
print("3. Run this script with your article text")
print("4. The chain will create 5 increasingly dense summaries")

