from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routers import build_logs, chat, dashboard, docs, history, repo, test_results
from backend.app.services.bedrock_service import bedrock_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    await init_db()
    yield

app = FastAPI(
    title="DevOps Copilot AI — API",
    description="Intelligent developer assistant for build log diagnosis, repo inspection, test analysis, and Bedrock AI reasoning.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)
app.include_router(build_logs.router)
app.include_router(repo.router)
app.include_router(test_results.router)
app.include_router(docs.router)
app.include_router(chat.router)
app.include_router(history.router)

@app.get("/health")
async def health_check():
    has_aws_creds = bool(settings.aws_access_key_id and settings.aws_secret_access_key)
    return {
        "status": "healthy",
        "app_name": "DevOps Copilot AI",
        "version": "1.0.0",
        "bedrock_mode": settings.bedrock_mode,
        "bedrock_model_id": settings.bedrock_model_id,
        "aws_credentials_configured": has_aws_creds,
        "mcp_server_target": f"http://{settings.mcp_host}:{settings.mcp_port}{settings.mcp_endpoint}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.backend_host, port=settings.backend_port, reload=True)
