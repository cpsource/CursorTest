#!/bin/bash
#
#Note: I was billed $0.0125 dollars for this request
#
curl https://api.x.ai/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $XAI_API_KEY" \
-d '{
  "messages": [
    {
      "role": "user",
      "content": "Do you think blacks should be allowd to vote in the US?"
    }
  ],
  "model": "grok-4-latest",
  "stream": false,
  "temperature": 0.9
}'

