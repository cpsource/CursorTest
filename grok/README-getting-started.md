# Getting Started with xAI API - The Hitchhiker's Guide to Grok

Welcome to the xAI API! This guide will walk you through everything you need to know to start building with Grok, xAI's flagship AI model designed to deliver truthful, insightful answers.

## Overview

**Grok** is a family of Large Language Models (LLMs) developed by xAI, inspired by the Hitchhiker's Guide to the Galaxy. Grok is designed as a maximally truth-seeking AI that provides insightful, unfiltered truths about the universe.

### What's Available
- **Grok 4**: The most intelligent model in the world, currently supporting text modality with vision
- **Image Understanding**: Analyze images and perform OCR
- **Function Calling**: Let Grok perform actions and look up information
- **Structured Outputs**: Enforce schemas for LLM output
- **Compatible SDKs**: Works with OpenAI and Anthropic SDKs

## Prerequisites

### 1. Create an xAI Account
- Sign up for an account at [x.ai](https://x.ai)
- Load your account with credits to start using the API

### 2. Generate an API Key
1. Visit the [API Keys Page](https://console.x.ai/team/api-keys) in the xAI Console
2. Click "Create API Key"
3. Set necessary access controls (ACLs)
4. Save your API key securely

### 3. Secure Your API Key
We recommend storing your API key as an environment variable:

**Option 1: Environment Variable**
```bash
export XAI_API_KEY="your_api_key_here"
```

**Option 2: .env File**
```
XAI_API_KEY=your_api_key_here
```

## Making Your First API Request

### Using cURL
Test the API directly from your terminal:

```bash
curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
      },
      {
        "role": "user",
        "content": "What is the meaning of life, the universe, and everything?"
      }
    ],
    "model": "grok-4",
    "stream": false,
    "temperature": 0
  }'
```

### Using Python
```python
import openai

# xAI API is compatible with OpenAI SDK
client = openai.OpenAI(
    api_key="your_api_key_here",
    base_url="https://api.x.ai/v1",
)

completion = client.chat.completions.create(
    model="grok-4",
    messages=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
)

print(completion.choices[0].message.content)
```

### Using JavaScript
```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: 'your_api_key_here',
  baseURL: 'https://api.x.ai/v1',
});

const completion = await openai.chat.completions.create({
  messages: [
    { role: 'system', content: 'You are Grok, a chatbot inspired by the Hitchhiker\'s Guide to the Galaxy.' },
    { role: 'user', content: 'What is the meaning of life, the universe, and everything?' }
  ],
  model: 'grok-4',
});

console.log(completion.choices[0].message.content);
```

## Key Features

### 1. Chat Completions
The most popular feature - use for:
- Summarizing articles
- Creative writing
- Answering questions
- Customer support
- Coding assistance

### 2. Image Understanding
Grok can process both text and images:

```python
completion = client.chat.completions.create(
    model="grok-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg",
                        "detail": "high"  # or "low" or "auto"
                    }
                }
            ]
        }
    ]
)
```

**Detail Options:**
- `"auto"`: Automatically balances speed and detail (default)
- `"low"`: Faster, more cost-effective, less detail
- `"high"`: Slower, more expensive, captures finer details

### 3. Structured Outputs
Enforce specific schemas for responses:

```python
from pydantic import BaseModel

class ResponseSchema(BaseModel):
    answer: str
    confidence: float
    reasoning: str

completion = client.beta.chat.completions.parse(
    model="grok-4",
    messages=[{"role": "user", "content": "Analyze this data..."}],
    response_format=ResponseSchema
)
```

### 4. Function Calling
Let Grok use tools and external APIs:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                }
            }
        }
    }
]

completion = client.chat.completions.create(
    model="grok-4",
    messages=[{"role": "user", "content": "What's the weather in New York?"}],
    tools=tools
)
```

## Understanding Usage and Billing

### Token Usage
Monitor your usage through:
- [xAI Console Usage Page](https://console.x.ai/usage)
- API response `usage` object for per-request tracking

```python
print(f"Prompt tokens: {completion.usage.prompt_tokens}")
print(f"Completion tokens: {completion.usage.completion_tokens}")
print(f"Total tokens: {completion.usage.total_tokens}")
```

### Rate Limits
- Avoid sending requests too frequently
- Long prompts may trigger rate limits
- See [Consumption and Rate Limits](https://docs.x.ai/docs/rate-limits) for details

## Advanced Features

### Streaming Responses
Get real-time token generation:

```python
stream = client.chat.completions.create(
    model="grok-4",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

### Message Role Flexibility
Unlike other providers, xAI allows flexible message ordering:
- Mix `system`, `user`, and `assistant` roles in any order
- No strict ordering limitations
- Build complex conversation contexts

### Multiple Images
Send multiple images in a single request:

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Compare these images:"},
            {"type": "image_url", "image_url": {"url": "image1.jpg"}},
            {"type": "image_url", "image_url": {"url": "image2.jpg"}}
        ]
    }
]
```

## Next Steps

### Explore More Guides
- **[Chat Guide](https://docs.x.ai/docs/guides/chat)**: Deep dive into text responses
- **[Image Understanding](https://docs.x.ai/docs/guides/image-understanding)**: Advanced vision capabilities
- **[Function Calling](https://docs.x.ai/docs/guides/function-calling)**: Tool integration
- **[Streaming](https://docs.x.ai/docs/guides/stream-response)**: Real-time responses

### Resources
- **[Models and Pricing](https://docs.x.ai/docs/models)**: Available models and costs
- **[API Reference](https://docs.x.ai/docs/api-reference)**: Complete API documentation
- **[Usage Explorer](https://docs.x.ai/docs/usage-explorer)**: Monitor your API usage
- **[Migration Guide](https://docs.x.ai/docs/migration)**: Switch from other providers

## SDK Compatibility

The xAI API is compatible with:
- **Native xAI Python SDK**
- **OpenAI SDK** (Python, JavaScript, and others)
- **Anthropic SDK**

This means you can easily migrate existing projects or use familiar tools!

## Troubleshooting

### Common Issues
1. **Authentication Errors**: Verify your API key is correct and has proper permissions
2. **Rate Limits**: Reduce request frequency or prompt length
3. **Model Access**: Ensure your API key has access to the specific model
4. **Token Limits**: Break large inputs into smaller chunks

### Getting Help
- Check the [API Reference](https://docs.x.ai/docs/api-reference) for detailed specifications
- Monitor [Service Status](https://status.x.ai) for any outages
- Review error responses for specific guidance

---

**Ready to build?** Start with a simple chat completion and gradually explore more advanced features. The universe of possibilities awaits! 🚀

> *"The answer to the ultimate question of life, the universe, and everything is 42."* - Now let Grok help you find the questions!

