import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    backend_host: str = Field(default="127.0.0.1", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS"
    )

    # MCP settings
    mcp_host: str = Field(default="127.0.0.1", alias="MCP_HOST")
    mcp_port: int = Field(default=8001, alias="MCP_PORT")
    mcp_endpoint: str = Field(default="/sse", alias="MCP_ENDPOINT")

    # AWS Bedrock settings
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_session_token: Optional[str] = Field(default=None, alias="AWS_SESSION_TOKEN")
    bedrock_model_id: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0",
        alias="BEDROCK_MODEL_ID"
    )
    bedrock_mode: str = Field(default="auto", alias="BEDROCK_MODE")  # auto | force_demo | force_bedrock

    # Security & Repo inspection
    authorized_repo_roots: str = Field(default="", alias="AUTHORIZED_REPO_ROOTS")
    max_upload_size_mb: int = Field(default=5, alias="MAX_UPLOAD_SIZE_MB")
    max_log_lines: int = Field(default=5000, alias="MAX_LOG_LINES")
    subprocess_timeout_seconds: int = Field(default=15, alias="SUBPROCESS_TIMEOUT_SECONDS")

    # Database
    db_path: str = Field(default="devops_copilot.db", alias="DB_PATH")

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def authorized_roots_list(self) -> List[str]:
        if not self.authorized_repo_roots.strip():
            # Default to the project directory and scratch folder
            current_dir = Path(__file__).resolve().parent.parent.parent
            return [str(current_dir)]
        return [r.strip() for r in self.authorized_repo_roots.split(",") if r.strip()]

settings = Settings()
