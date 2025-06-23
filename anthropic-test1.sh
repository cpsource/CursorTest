#!/bin/bash

# Load environment variables from ~/.env file
if [ -f ~/.env ]; then
    # Export variables from .env file
    export $(grep -v '^#' ~/.env | xargs)
else
    echo "Error: ~/.env file not found"
    exit 1
fi

# Check if CLAUDE_API_KEY is set
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "Error: CLAUDE_API_KEY not found in ~/.env file"
    exit 1
fi

# Execute the curl command with the API key
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $CLAUDE_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "Hello, world"}
        ]
    }'
 
