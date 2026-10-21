# Amazon Bedrock Converse API Documentation

Source: https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html

## Overview
The Amazon Bedrock Converse API provides a consistent, unified API for conversational inference across multiple foundation models, including Anthropic Claude 3.5 Sonnet, Anthropic Claude 3 Haiku, Amazon Nova, and Meta Llama.

## Key Features
- **Unified Schema**: Single request and response structure regardless of the underlying foundation model provider.
- **Multi-turn Context**: Supports passing structured message history (`user` and `assistant` roles).
- **System Prompts**: Pass system instructions to guide model persona and constraints.
- **Inference Configuration**: Control `temperature`, `maxTokens`, and `topP`.
- **Tool Use (Function Calling)**: Define tool specifications with JSON schemas so models can request external actions.

## Python Boto3 Converse Invocation Example
```python
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

response = client.converse(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    messages=[
        {"role": "user", "content": [{"text": "Explain this build failure..."}]}
    ],
    system=[{"text": "You are DevOps Copilot AI, an expert site reliability and devops engineer."}],
    inferenceConfig={"temperature": 0.2, "maxTokens": 2048}
)

output_text = response["output"]["message"]["content"][0]["text"]
```

## Common Error Codes and Handling
- `AccessDeniedException`: The AWS IAM principal lacks `bedrock:InvokeModel` permissions or the specified model has not been enabled in the AWS Bedrock Model Access console.
- `ValidationException`: Input parameters exceed token limits or have invalid types.
- `ThrottlingException`: Request rate or token quotas exceeded. Implement exponential backoff with jitter.
- `ModelNotReadyException` / `ResourceNotFoundException`: Check the region and exact model ID string.
