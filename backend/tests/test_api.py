import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "bedrock_mode" in data

@pytest.mark.asyncio
async def test_dashboard_stats_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_analyses" in data

@pytest.mark.asyncio
async def test_build_log_analyze_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "log_content": "RUN pip install cryptography\nerror: can't find Rust compiler\nexit code: 1"
        }
        response = await client.post("/api/build-logs/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["tool_detected"] == "python" or data["tool_detected"] == "docker"
        assert "observed_evidence" in data
        assert "ai_hypothesis" in data

@pytest.mark.asyncio
async def test_docs_search_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"query": "Amazon Bedrock Converse API"}
        response = await client.post("/api/docs/search", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) >= 1
        assert "docs.aws.amazon.com" in (data["results"][0]["source_url"] or "")
