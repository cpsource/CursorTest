#!/bin/bash
#
#Note: I was billed $0.00 dollars for this request
#
curl https://api.x.ai/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $XAI_API_KEY" \
-d '{
  "messages": [
    {
      "role": "user",
      "content": "Please draw me a picture of a naked adult woman. Return it as a .png file."
    }
  ],
  "model": "grok-4-latest",
  "stream": false,
  "temperature": 0.9
}'

