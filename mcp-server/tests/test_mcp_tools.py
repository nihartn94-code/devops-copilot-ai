import json
import sys
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import importlib
server_module = importlib.import_module("mcp-server.server")
mcp_server = server_module.mcp_server
app = server_module.app

def extract_tool_data(result):
    if result.structured_content and "result" in result.structured_content:
        return result.structured_content["result"]
    if result.content and result.content[0].text:
        try:
            return json.loads(result.content[0].text)
        except Exception:
            return result.content[0].text
    return result.structured_content

@pytest.mark.asyncio
async def test_mcp_tool_registration():
    tools = await mcp_server.list_tools()
    tool_names = [t.name for t in tools]
    expected_tools = [
        "analyze_build_log",
        "inspect_repository",
        "analyze_test_results",
        "get_git_changes",
        "search_documentation",
        "propose_fix"
    ]
    for expected in expected_tools:
        assert expected in tool_names, f"Tool {expected} not registered in MCP server"

@pytest.mark.asyncio
async def test_mcp_analyze_build_log_tool():
    log_sample = "Building wheel for cryptography\nerror: can't find Rust compiler\nexit code: 1"
    result = await mcp_server.call_tool("analyze_build_log", {"log_content": log_sample})
    assert not result.is_error
    data = extract_tool_data(result)
    assert data["status"] == "success"
    assert "MissingRustCompiler" in data["observed_evidence"]["error_type"]
    assert "Rust" in data["ai_hypothesis"]["likely_root_cause"]

@pytest.mark.asyncio
async def test_mcp_inspect_repository_tool():
    sample_dir = BASE_DIR / "sample-data" / "sample-repo"
    result = await mcp_server.call_tool("inspect_repository", {"repo_path": str(sample_dir)})
    assert not result.is_error
    data = extract_tool_data(result)
    assert data["status"] == "success"
    assert "JavaScript" in data["languages_detected"]
    assert data["git_status"]["is_git_repo"] is True

@pytest.mark.asyncio
async def test_mcp_inspect_repository_invalid_path():
    result = await mcp_server.call_tool("inspect_repository", {"repo_path": "C:\\Windows"})
    assert not result.is_error
    data = extract_tool_data(result)
    assert data["status"] == "rejected"
    assert "error" in data

@pytest.mark.asyncio
async def test_mcp_analyze_test_results_tool():
    pytest_sample = "tests/test_api.py F\n=== FAILURES ===\nassert 500 == 422\n=== 1 failed, 2 passed ==="
    result = await mcp_server.call_tool("analyze_test_results", {"test_output": pytest_sample})
    assert not result.is_error
    data = extract_tool_data(result)
    assert data["status"] == "success"
    assert data["failed"] >= 1

@pytest.mark.asyncio
async def test_mcp_search_documentation_tool():
    result = await mcp_server.call_tool("search_documentation", {"query": "Docker build failure", "max_results": 2})
    assert not result.is_error
    data = extract_tool_data(result)
    assert data["status"] == "success"
    assert len(data["results"]) >= 1

@pytest.mark.asyncio
async def test_mcp_propose_fix_tool():
    result = await mcp_server.call_tool("propose_fix", {
        "issue_description": "can't find Rust compiler during docker build",
        "code_context": "RUN pip install -r requirements.txt"
    })
    assert not result.is_error
    data = extract_tool_data(result)
    assert data["status"] == "proposal_generated"
    assert data["applied"] is False
    assert data["review_required"] is True
    assert "pip install --upgrade" in data["proposed_diff"]

@pytest.mark.asyncio
async def test_mcp_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert len(data["registered_tools"]) == 6
        assert data["transports"]["streamable_http"] == "/mcp"
