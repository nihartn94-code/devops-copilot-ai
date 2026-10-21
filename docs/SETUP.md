# DevOps Copilot AI — Local Setup & Execution Guide (Windows PowerShell)

Follow these step-by-step instructions to configure, run, and test **DevOps Copilot AI** on Windows.

---

## 📋 System Prerequisites
- **Python**: 3.10+ (tested with Python 3.12)
- **Node.js**: 18+ & npm (tested with Node v24 & npm 11)
- **Git**: Installed and in PATH

---

## 🛠️ Step 1: Virtual Environment Setup

Open Windows PowerShell and navigate to the project directory:

```powershell
cd "C:\Users\NIKHIL T N\.gemini\antigravity-ide\scratch\devops-copilot-ai"

# Create a clean virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

> [!NOTE]
> If your PowerShell restricts script execution, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## 📦 Step 2: Install Dependencies

```powershell
# 1. Install Backend and MCP Server requirements
pip install -r backend/requirements.txt
pip install -r mcp-server/requirements.txt

# 2. Install Frontend dependencies
cd frontend
npm install
cd ..
```

---

## ⚙️ Step 3: Configure Environment Variables

```powershell
Copy-Item .env.example .env
```

Open `.env` in your text editor:

```ini
# Server configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
MCP_HOST=127.0.0.1
MCP_PORT=8001

# Amazon Bedrock credentials (Optional)
# If blank, DevOps Copilot runs in a transparent, labeled Demo Fallback mode.
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_MODE=auto
```

---

## 🚀 Step 4: Start the Services

Open three PowerShell terminal windows:

### Terminal 1: FastAPI Backend (Port 8000)
```powershell
cd "C:\Users\NIKHIL T N\.gemini\antigravity-ide\scratch\devops-copilot-ai"
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Health Check*: Open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) or Swagger docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Terminal 2: MCP Streamable HTTP Server (Port 8001)
```powershell
cd "C:\Users\NIKHIL T N\.gemini\antigravity-ide\scratch\devops-copilot-ai"
.\.venv\Scripts\Activate.ps1
python mcp-server/server.py
```
*MCP Endpoint*: Streamable HTTP at `http://127.0.0.1:8001/mcp` and SSE at `http://127.0.0.1:8001/sse`.

### Terminal 3: React + Vite Frontend (Port 5173)
```powershell
cd "C:\Users\NIKHIL T N\.gemini\antigravity-ide\scratch\devops-copilot-ai\frontend"
npm run dev
```
*Web App URL*: Open **[http://localhost:5173/](http://localhost:5173/)** in your browser.

---

## 🧪 Step 5: Run Automated Tests

Execute both the backend and MCP test suites from the project root:

```powershell
cd "C:\Users\NIKHIL T N\.gemini\antigravity-ide\scratch\devops-copilot-ai"
.\.venv\Scripts\Activate.ps1

# 1. Run Backend Unit & Integration Tests (19 tests)
pytest backend/tests -v

# 2. Run Model Context Protocol (MCP) Tool Tests (8 tests)
pytest mcp-server/tests -v
```

---

## 🛡️ Security Verification

1. **Secret Redaction**:
   - Paste any sample log containing `AKIAIOSFODNN7EXAMPLE` or database passwords.
   - The UI automatically flags: `Zero Secret Leakage Protection: N sensitive credentials redacted`.
2. **Path Traversal Protection**:
   - Enter `C:\Windows` in the Repo Inspector.
   - The system strictly refuses inspection with a `403 Forbidden` error.
3. **Non-Destructive Proposals**:
   - Code patches and remedies are displayed as diffs for manual developer review and never executed automatically without approval.
