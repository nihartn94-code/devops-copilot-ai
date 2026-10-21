import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

# Ensure parent directory is in sys.path so we can import backend services
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from mcp.server.mcpserver import MCPServer
from backend.app.services.build_log_service import build_log_service
from backend.app.services.doc_service import doc_service
from backend.app.services.redaction_service import redaction_service
from backend.app.services.repo_service import repo_inspector
from backend.app.services.test_analyzer_service import test_analyzer_service

# Initialize Model Context Protocol Server (2025-11-25+ Streamable HTTP spec)
mcp_server = MCPServer(
    name="devops-copilot-mcp",
    version="1.0.0",
    description="DevOps Copilot AI developer tools for build diagnosis, repo inspection, test analysis, and doc search."
)

@mcp_server.tool()
def analyze_build_log(log_content: str, build_tool: Optional[str] = None) -> Dict[str, Any]:
    """
    Parses build logs, redacts secrets, extracts error coordinates and context,
    and returns likely root cause with prioritized debugging recommendations.
    """
    if not log_content or not log_content.strip():
        return {"error": "log_content cannot be empty."}

    redacted = redaction_service.redact(log_content)
    clean_log = redacted.clean_text

    tool = build_log_service.detect_tool(clean_log, build_tool)
    evidence = build_log_service.extract_evidence(clean_log)
    hypothesis = build_log_service.generate_deterministic_hypothesis(evidence, tool)

    return {
        "status": "success",
        "tool_detected": tool,
        "secrets_redacted_count": redacted.secrets_detected,
        "observed_evidence": {
            "error_type": evidence.error_type,
            "primary_error_message": evidence.primary_error_message,
            "failed_command_or_file": evidence.failed_command_or_file,
            "line_number": evidence.line_number,
            "exit_code": evidence.exit_code,
            "context_snippet": evidence.context_snippet
        },
        "ai_hypothesis": {
            "likely_root_cause": hypothesis.likely_root_cause,
            "confidence_score": hypothesis.confidence_score,
            "explanation": hypothesis.explanation,
            "prioritized_debugging_steps": hypothesis.prioritized_debugging_steps,
            "recommended_fix_code": hypothesis.recommended_fix_code,
            "recommended_fix_description": hypothesis.recommended_fix_description
        }
    }

@mcp_server.tool()
def inspect_repository(repo_path: str) -> Dict[str, Any]:
    """
    Safely inspects an authorized repository directory.
    Detects language stacks, configuration files, Git status, and potential issues.
    Never executes arbitrary commands or traverses outside authorized boundaries.
    """
    try:
        resolved = repo_inspector.validate_and_resolve_path(repo_path)
    except (FileNotFoundError, ValueError, PermissionError) as e:
        return {"error": str(e), "status": "rejected"}

    data = repo_inspector.inspect(resolved)
    return {
        "status": "success",
        "repo_path": str(resolved),
        "languages_detected": data["languages_detected"],
        "frameworks_detected": data["frameworks_detected"],
        "config_files_found": data["config_files_found"],
        "git_status": data["git_status"],
        "potential_issues": data["potential_issues"],
        "recommendations": data["recommendations"]
    }

@mcp_server.tool()
def analyze_test_results(test_output: str, test_framework: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes unit or integration test outputs (pytest, Jest, JUnit, etc.).
    Extracts failed test names, assertion errors, stack traces, and proposed patches.
    """
    if not test_output or not test_output.strip():
        return {"error": "test_output cannot be empty."}

    redacted = redaction_service.redact(test_output)
    clean_output = redacted.clean_text

    result = test_analyzer_service.analyze(clean_output, test_framework)
    failed_details = [
        {
            "test_name": t.test_name,
            "file_path": t.file_path,
            "failure_message": t.failure_message,
            "assertion_type": t.assertion_type
        }
        for t in result["failed_tests"]
    ]

    return {
        "status": "success",
        "framework": result["framework"],
        "total_tests": result["total_tests"],
        "passed": result["passed"],
        "failed": result["failed"],
        "skipped": result["skipped"],
        "failed_tests": failed_details,
        "root_cause_summary": result["root_cause_summary"],
        "next_steps": result["next_steps"],
        "remedy_patch": result["remedy_patch"]
    }

@mcp_server.tool()
def get_git_changes(repo_path: str) -> Dict[str, Any]:
    """
    Safely checks the working tree status and recent commits for an authorized repository.
    Read-only operation with strict subprocess timeout.
    """
    try:
        resolved = repo_inspector.validate_and_resolve_path(repo_path)
    except (FileNotFoundError, ValueError, PermissionError) as e:
        return {"error": str(e), "status": "rejected"}

    git_info = repo_inspector._get_git_status(resolved)
    return {
        "status": "success",
        "repo_path": str(resolved),
        "git_info": git_info
    }

@mcp_server.tool()
def search_documentation(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Searches curated developer documentation (Amazon Bedrock, Docker, FastAPI, MCP)
    and returns matching excerpts with verified source links.
    """
    if not query or not query.strip():
        return {"error": "query cannot be empty."}

    results, ai_answer = doc_service.search(query, max_results=max_results)
    serialized_results = [
        {
            "title": r.title,
            "source_file": r.source_file,
            "source_url": r.source_url,
            "relevance_score": r.relevance_score,
            "excerpt": r.excerpt
        }
        for r in results
    ]

    return {
        "status": "success",
        "query": query,
        "results": serialized_results,
        "ai_answer": ai_answer
    }

@mcp_server.tool()
def propose_fix(issue_description: str, code_context: str) -> Dict[str, Any]:
    """
    Proposes a non-destructive patch or configuration fix without applying it automatically.
    The user or developer can review the proposed diff and apply it at their discretion.
    """
    if not issue_description or not code_context:
        return {"error": "issue_description and code_context are required."}

    redacted_context = redaction_service.redact(code_context).clean_text
    lower_issue = issue_description.lower()

    if "rust" in lower_issue or "cryptography" in lower_issue:
        proposed_patch = (
            "--- Dockerfile.orig\n"
            "+++ Dockerfile\n"
            "@@ -8,4 +8,5 @@\n"
            "+RUN pip install --upgrade pip setuptools wheel\n"
            " RUN pip install --no-cache-dir -r requirements.txt\n"
        )
        rationale = "Upgrading pip enables pulling precompiled wheels so local rustc compilation is avoided."
    elif "typescript" in lower_issue or "ts2322" in lower_issue or "ts2307" in lower_issue:
        proposed_patch = (
            "--- src/services/api.ts.orig\n"
            "+++ src/services/api.ts\n"
            "@@ -42,1 +42,1 @@\n"
            "-  authToken: process.env.API_SECRET_TOKEN,\n"
            "+  authToken: process.env.API_SECRET_TOKEN ?? '',\n"
        )
        rationale = "Provide a fallback string to satisfy TypeScript string non-undefined contract."
    else:
        proposed_patch = (
            f"// Proposed fix for: {issue_description}\n"
            "// Review and verify before applying.\n"
        )
        rationale = f"Suggested remediation based on provided context: {issue_description}"

    return {
        "status": "proposal_generated",
        "applied": False,
        "review_required": True,
        "issue_description": issue_description,
        "rationale": rationale,
        "proposed_diff": proposed_patch,
        "verification_steps": [
            "Review the diff against the target file.",
            "Apply the patch manually or through git apply.",
            "Run automated tests to confirm the fix."
        ]
    }

async def health_endpoint(request):
    tools = await mcp_server.list_tools()
    return JSONResponse({
        "status": "healthy",
        "server": "devops-copilot-mcp",
        "mcp_version": "2025-11-25",
        "registered_tools": [t.name for t in tools],
        "transports": {
            "streamable_http": "/mcp",
            "server_sent_events": "/sse",
            "messages": "/messages/"
        }
    })

# Unified ASGI application: Streamable HTTP (/mcp) and SSE (/sse, /messages)
def create_app() -> Starlette:
    streamable_app = mcp_server.streamable_http_app()
    sse_app = mcp_server.sse_app()

    return Starlette(
        routes=[
            Route("/health", endpoint=health_endpoint, methods=["GET"]),
            Mount("/mcp", app=streamable_app),
            Mount("/sse", app=sse_app),
            Mount("/messages", app=sse_app),
        ]
    )

app = create_app()

if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8001"))
    print(f"Starting DevOps Copilot MCP Server on http://{host}:{port} ...")
    uvicorn.run("mcp-server.server:app", host=host, port=port, reload=True)
