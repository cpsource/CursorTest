#!/usr/bin/env python3
"""
panel_discussion.py

Fully runnable script forcing an LLM (via LangChain) to speak strictly in JSON
for a panel discussion about AGI architecture.
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Define the JSON template as a LangChain prompt
json_template = """
You are a computer scientist participating in an AGI panel discussion.
Respond ONLY in JSON following this format:

{
  "turn": {TURN_NUMBER},
  "speaker": "{SPEAKER_NAME}",
  "message": {
    "topic": "{TOPIC}",
    "content": "{CONTENT}",
    "references": [
      {
        "title": "{REFERENCE_TITLE}",
        "author": "{REFERENCE_AUTHOR}",
        "year": {REFERENCE_YEAR},
        "link": "{REFERENCE_LINK}"
      }
    ],
    "questions": [
      "{QUESTION_1}",
      "{QUESTION_2}"
    ]
  },
  "timestamp": "{TIMESTAMP_ISO8601}"
}

Provide all fields with values. Do NOT include explanations outside the JSON.
Now generate Turn {turn_number} as {speaker_name} on topic: {topic}.
"""

# Build the LangChain prompt template
prompt = ChatPromptTemplate.from_template(json_template)

# Create the OpenAI chat model (ensure OPENAI_API_KEY is set in environment)
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.8,
)

# Example user inputs for the panel discussion
inputs = {
    "turn_number": 1,
    "speaker_name": "DrSmith",
    "topic": "AGI Memory Architecture"
}

# Create and run the chain
chain = prompt | llm
response = chain.invoke(inputs)

# Display the raw text response
print("\n=== RAW MODEL RESPONSE ===\n")
print(response.content)

# Attempt to parse JSON
try:
    data = json.loads(response.content)
    print("\n=== PARSED JSON ===\n")
    print(json.dumps(data, indent=2))
except json.JSONDecodeError as e:
    print("\nERROR: Invalid JSON returned by model")
    print("Details:", e)
    print("\nOriginal Text:\n", response.content)


