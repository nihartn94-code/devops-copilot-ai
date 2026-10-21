# Model Context Protocol (MCP) — Alexa+ & Streamable HTTP Integration

## 1. Hackathon Integration Context

This application implements a **self-hosted Model Context Protocol (MCP) server over Streamable HTTP** compliant with the MCP specification (version 2025-11-25+). It allows **Alexa+**, Claude Desktop, Cursor, and any MCP-compatible agent to consume real-time developer debugging tools.

---

## 2. Server Configuration

- **Host**: `127.0.0.1`
- **Port**: `8001`
- **SSE Transport Endpoint**: `http://127.0.0.1:8001/sse`
- **Message Post Endpoint**: `http://127.0.0.1:8001/messages/`

---

## 3. Registered Developer Tools

### 1. `analyze_build_log`
- **Description**: Parses a build failure log, redacts secrets, extracts core error lines, and returns root cause explanation and prioritized fixes.
- **Parameters**:
  - `log_content` (string, required): Raw text of the build log.
  - `build_tool` (string, optional): One of `docker`, `npm`, `maven`, `gradle`, `python`.

### 2. `inspect_repository`
- **Description**: Inspects an authorized repository directory to detect language stacks, config files, package dependencies, and potential security issues.
- **Parameters**:
  - `repo_path` (string, required): Absolute or relative path to authorized repository.

### 3. `analyze_test_results`
- **Description**: Analyzes test output (pytest, jest, junit) and extracts failed test names, assertion errors, stack trace summaries, and remedies.
- **Parameters**:
  - `test_output` (string, required): Raw test runner terminal output.
  - `test_framework` (string, optional): One of `pytest`, `jest`, `junit`.

### 4. `get_git_changes`
- **Description**: Safely checks Git status and recent commits/diffs for an authorized repository without modifying files.
- **Parameters**:
  - `repo_path` (string, required): Path to repository.

### 5. `search_documentation`
- **Description**: Searches developer documentation for technical guidance and returns excerpts with verified source links.
- **Parameters**:
  - `query` (string, required): Technical question or search term.
  - `max_results` (integer, optional, default: 3): Number of citations to return.

### 6. `propose_fix`
- **Description**: Proposes a non-destructive patch or configuration fix for a specific issue without applying it automatically.
- **Parameters**:
  - `issue_description` (string, required): Summary of the problem.
  - `code_context` (string, required): Relevant file content or error snippet.

---

## 4. How to Test with Alexa+ / MCP Inspector

### Option A: Using the MCP Inspector CLI
```powershell
npx @modelcontextprotocol/inspector http://127.0.0.1:8001/sse
```
The inspector web UI will open, allowing you to view and test all tools interactively.

### Option B: Using the Automated Test Script
Run our automated MCP integration tests:
```powershell
.\.venv\Scripts\Activate.ps1
pytest mcp-server/tests/test_mcp_tools.py -v
```

### Option C: Direct HTTP Testing
Connect to the SSE stream:
```powershell
curl -N http://127.0.0.1:8001/sse
```
