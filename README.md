# DevOps Copilot AI 🚀
### AI-Powered Developer Assistant for Build Failure Diagnosis, Repository Inspection, Test Analysis, and MCP Streamable HTTP Tools
*Amazon Developer Hackathon — Alexa+ Track / Developer Tools*

![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![React](https://img.shields.io/badge/React-18-cyan.svg)
![Amazon Bedrock](https://img.shields.io/badge/Amazon%20Bedrock-Converse%20API-orange.svg)
![MCP](https://img.shields.io/badge/MCP-2025--11--25%20Streamable%20HTTP-purple.svg)

---

## 🌟 Overview

**DevOps Copilot AI** is a developer platform designed to eliminate the frustration of CI/CD pipeline failures, cryptic stack traces, broken unit tests, and obscure dependency conflicts. 

Equipped with direct integration to **Amazon Bedrock (Converse API)** and a self-hosted **Model Context Protocol (MCP)** server over **Streamable HTTP (Server-Sent Events)**, DevOps Copilot AI empowers engineers, automated agents, and Alexa+ devices to debug, inspect, and analyze codebases safely and transparently.

---

## ✨ Key Capabilities

### 1. 🔍 Build-Log Analyzer
- Parses massive build and CI logs (Docker, npm/Vite, Maven/Gradle, Python/Poetry).
- Extracts precise error spans, file coordinates, and surrounding context.
- Distinguishes **Observed Evidence** (exact logs, exit codes, file paths) from **AI-Generated Hypotheses**.
- Proposes prioritized debugging steps and drop-in code fixes.
- Includes automated **Secret Redaction** before sending any data to external models.

### 2. 🛡️ Safe Repository Inspector
- Inspects authorized local project directories with strict path-traversal safeguards.
- Auto-detects programming languages, frameworks, linters, package managers, and CI workflows.
- Evaluates Git working-tree status (modified files, untracked changes, unpushed commits, and branch diffs).
- Flags security issues (e.g., exposed credentials, missing `.gitignore` rules, dangerous scripts).
- Strictly read-only: never modifies code or runs arbitrary commands automatically.

### 3. 🧪 Test-Result Analyzer
- Ingests test outputs from `pytest`, `Jest`, `JUnit`, and generic runners.
- Summarizes total, passed, failed, and skipped tests with pass/fail ratios.
- Diagnoses root causes (assertion failures, timeout, network error, unhandled exception).
- Exports formatted reports in Markdown and JSON for CI/CD attachment.

### 4. 📚 Technical Documentation Assistant
- Search grounded, curated documentation (AWS Bedrock, Docker, FastAPI, MCP, Pytest).
- Cites exact verified sources with URLs.
- Separates verified source excerpts from AI synthesis without inventing false references.

### 5. 💬 Interactive AI Debugging Assistant
- Multi-turn conversational debugging linked to the active analysis.
- Powered by **Amazon Bedrock Converse API** (`anthropic.claude-3-5-sonnet-20241022-v2:0`).
- **Honest Demo Fallback Mode**: If AWS credentials are absent or restricted, automatically operates in an offline fallback mode with deterministic responses clearly tagged as such.

### 6. 🌐 Self-Hosted MCP Server (Streamable HTTP)
- Complies with MCP specification (version 2025-11-25+).
- Operates over Streamable HTTP (`/sse` and `/messages`) on port 8001.
- Exposes developer tools for Alexa+ and external MCP clients:
  - `analyze_build_log`
  - `inspect_repository`
  - `analyze_test_results`
  - `get_git_changes`
  - `search_documentation`
  - `propose_fix` (non-destructive patch proposal)

### 7. 💾 SQLite Analysis History & Reports
- Local persistence of past analyses without cloud lock-in.
- Search, filter, reopen, and download past diagnostic reports.

---

## 🏗️ Architecture

```
+-------------------------------------------------------------+
|               React 18 + TypeScript + Vite UI               |
|            (Port 5173 - Dark/Light Modern Theme)            |
+------------------------------+------------------------------+
                               | REST API (JSON)
                               v
+-------------------------------------------------------------+
|                     FastAPI Backend                         |
|                       (Port 8000)                           |
|  - Secret Redactor        - SQLite Analysis History         |
|  - Log & Test Parsers     - Path-Traversal Guard            |
+---------------+-----------------------------+---------------+
                |                             |
                v                             v
+-------------------------------+  +--------------------------+
|  Amazon Bedrock Converse API  |  | Self-Hosted MCP Server   |
|  - Claude 3.5 Sonnet / Haiku  |  | (Streamable HTTP / SSE)  |
|  - Transparent Demo Fallback  |  | (Port 8001)              |
+-------------------------------+  +--------------------------+
```

---

## 🚀 Quick Start (Windows PowerShell)

### Prerequisites
- Python 3.10+ (tested with 3.12)
- Node.js 18+ & npm
- Git

### 1. Clone & Setup Virtual Environment
```powershell
cd "devops-copilot-ai"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
# Backend & MCP Dependencies
pip install -r backend/requirements.txt
pip install -r mcp-server/requirements.txt

# Frontend Dependencies
cd frontend
npm install
cd ..
```

### 3. Configure Environment
```powershell
Copy-Item .env.example .env
# Edit .env with your AWS credentials if available (optional)
```

### 4. Run the Servers
Open three terminal windows (or use background processes):

**Terminal 1 — FastAPI Backend (Port 8000):**
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — MCP Streamable HTTP Server (Port 8001):**
```powershell
.\.venv\Scripts\Activate.ps1
python mcp-server/server.py
```

**Terminal 3 — React Frontend (Port 5173):**
```powershell
cd frontend
npm run dev
```

Visit **http://localhost:5173** to use the application!

---

## 🧪 Testing

Run backend and MCP test suites:
```powershell
.\.venv\Scripts\Activate.ps1
pytest backend/tests -v
pytest mcp-server/tests -v
```

---

## 🔒 Security & Privacy
- **Zero Accidental Secret Leakage**: All logs and test outputs pass through the regex-based `SecretRedactionService` before being sent to Bedrock or stored.
- **Path Traversal Protection**: Repository paths are resolved to their canonical paths and validated against authorized roots.
- **Read-Only Inspection**: Subprocess commands have timeouts and never execute arbitrary or destructive commands.
- **Transparent Demo Mode**: Clear visual indicators distinguish live Bedrock responses from deterministic local fallback responses.

---

## 📄 License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
