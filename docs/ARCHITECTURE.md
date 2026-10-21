# DevOps Copilot AI — Architecture Specification

## 1. System Overview

DevOps Copilot AI is built as a modular micro-architecture consisting of three distinct layers:
1. **Frontend Presentation Layer**: Modern React 18 SPA with TypeScript, Tailwind CSS, Lucide icons, dark/light themes, and responsive design.
2. **Core API & Engine Layer**: FastAPI Python service handling ingestion, parsing, sanitization, threat mitigation, and local SQLite persistence.
3. **AI & MCP Protocols Layer**:
   - **Amazon Bedrock Converse API**: Multi-turn conversational intelligence, automated error explanation, and fix generation.
   - **Model Context Protocol (MCP)**: Server-Sent Events (SSE) / Streamable HTTP endpoint for external developer tool orchestration (Alexa+, Bedrock Agents, IDE plugins).

---

## 2. Component Diagram

```
+---------------------------------------------------------------------------------+
|                                 USER INTERFACES                                 |
|                                                                                 |
|   +-------------------------------------+   +-------------------------------+   |
|   |   React + Vite Web Application      |   |  Alexa+ / MCP Client Tool Host|   |
|   |         (Port 5173)                 |   |    (External / Simulated)     |   |
|   +------------------+------------------+   +---------------+---------------+   |
+----------------------|--------------------------------------|-------------------+
                       |                                      |
                       | HTTP / REST (JSON)                   | Streamable HTTP (SSE)
                       v                                      v
+------------------------------------------+  +-----------------------------------+
|             FASTAPI BACKEND              |  |            MCP SERVER             |
|               (Port 8000)                |  |            (Port 8001)            |
|                                          |  |                                   |
|  +------------------------------------+  |  |  +-----------------------------+  |
|  |           Routers / API            |  |  |  |    FastMCP Tools Engine     |  |
|  |  /api/build-logs    /api/repo      |  |  |  |  - analyze_build_log        |  |
|  |  /api/test-results  /api/docs      |  |  |  |  - inspect_repository       |  |
|  |  /api/chat          /api/history   |  |  |  |  - analyze_test_results     |  |
|  +-----------------+------------------+  |  |  |  - get_git_changes          |  |
|                    |                     |  |  |  - search_documentation     |  |
|  +-----------------v------------------+  |  |  |  - propose_fix              |  |
|  |       Analysis & Parser Core       |  |  |  +--------------+--------------+  |
|  |  - Log Context & Error Extractor   |  |  |                 |                 |
|  |  - Safe Git Inspector              |<-+--------------------+                 |
|  |  - Test Output Parser              |  |   Shared Core Library & Logic        |
|  |  - Doc Keyword & Source Indexer    |  |                                      |
|  +-----------------+------------------+  +--------------------------------------+
|                    |                                                            
|  +-----------------v------------------+                                         
|  |     Secret Redaction Service       |                                         
|  |  (Strips AWS keys, tokens, auth)   |                                         
|  +-----------------+------------------+                                         
|                    |                                                            
|  +-----------------v------------------+     +-------------------------------+   
|  |      Amazon Bedrock Client         |---->| Amazon Bedrock Converse API   |   
|  |  (or Deterministic Demo Fallback)  |     | (Claude 3.5 Sonnet / Haiku)   |   
|  +-----------------+------------------+     +-------------------------------+   
|                    |                                                            
|  +-----------------v------------------+                                         
|  |     SQLite Async Persistence       |                                         
|  |       (devops_copilot.db)          |                                         
|  +------------------------------------+                                         
+------------------------------------------+
```

---

## 3. Security Architecture & Threat Model

### Data Protection & Secret Redaction
Before any log, test result, or code snippet is stored in SQLite or sent to Amazon Bedrock, it is processed by the `SecretRedactionService`.
- **AWS Credentials**: `AKIA[0-9A-Z]{16}` and base64 session tokens are replaced with `[REDACTED_AWS_KEY]`.
- **Bearer & Auth Tokens**: JWTs, GitHub PATs (`ghp_*`), and API keys are replaced with `[REDACTED_TOKEN]`.
- **Private Keys**: PEM formatted RSA/DSA/EC blocks are stripped.

### Path Traversal Defense
When inspecting repositories, arbitrary paths are prohibited. The path undergoes:
1. `os.path.realpath()` canonicalization.
2. Verification against `AUTHORIZED_REPO_ROOTS` or project subdirectories.
3. System directories (`C:\Windows`, `C:\Program Files`, `/etc`, `/usr`) are strictly denied.

### Subprocess Safety
Git commands are executed through safe wrappers with explicit timeouts (15 seconds maximum) and restricted to non-mutating commands (`git status`, `git diff`, `git log -n 5`).
No shell command recommended by AI is ever executed automatically.

---

## 4. MCP Streamable HTTP Specification

The MCP server adheres to the **Model Context Protocol** specification (version 2025-11-25+):
- **Endpoint**: `http://127.0.0.1:8001/sse` for SSE connection.
- **Messages**: `http://127.0.0.1:8001/messages/` for JSON-RPC 2.0 requests.
- **Transport**: Streamable HTTP with Server-Sent Events.
- **Tools**:
  - `analyze_build_log(log_content: str, build_tool: Optional[str])`
  - `inspect_repository(repo_path: str)`
  - `analyze_test_results(test_output: str, test_framework: Optional[str])`
  - `get_git_changes(repo_path: str)`
  - `search_documentation(query: str, max_results: int)`
  - `propose_fix(issue_description: str, code_context: str)`
