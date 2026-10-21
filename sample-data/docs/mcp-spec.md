# Model Context Protocol (MCP) — Streamable HTTP & Tools Specification

Source: https://spec.modelcontextprotocol.io/specification/2024-11-05/

## Protocol Overview
The Model Context Protocol (MCP) enables AI assistants and agents (such as Amazon Bedrock agents, Claude, and Alexa+) to securely connect to external data sources and developer tools.

## Transports
- **Streamable HTTP (Server-Sent Events / SSE)**: Uses HTTP POST for JSON-RPC message transmission and HTTP GET over `text/event-stream` for bidirectional streaming notifications.
- **Stdio Transport**: Used for local command-line sub-processes.

## Core Message Types
- `tools/list`: Requests list of registered tools with their input JSON Schema.
- `tools/call`: Executes a tool with provided arguments and returns structured content.

## Implementing Streamable HTTP in Python
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("devops-copilot-mcp", host="127.0.0.1", port=8001)

@mcp.tool()
def analyze_build_log(log_content: str) -> dict:
    """Analyze build failure logs and provide root cause diagnosis."""
    ...
```
