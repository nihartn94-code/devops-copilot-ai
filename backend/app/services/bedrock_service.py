import logging
from typing import Any, Dict, List, Optional, Tuple
import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from backend.app.config import settings
from backend.app.services.redaction_service import redaction_service

logger = logging.getLogger("bedrock_service")

class BedrockService:
    """
    Manages Amazon Bedrock Converse API invocations with automatic
    credential verification and an honest, transparent demo fallback engine.
    """

    SYSTEM_PROMPT = (
        "You are DevOps Copilot AI, an expert site reliability and devops engineer. "
        "Your task is to analyze build failures, test results, and technical codebases. "
        "Distinguish between observed facts and hypotheses. Provide actionable, safe, "
        "and prioritized debugging steps with copy-pasteable code fixes."
    )

    def __init__(self):
        self._client = None
        self._credentials_checked = False
        self._has_live_credentials = False

    def _get_client(self):
        if self._client is not None:
            return self._client

        # Check configuration
        if settings.bedrock_mode == "force_demo":
            logger.info("Bedrock running in forced demo mode by configuration.")
            return None

        try:
            session_kwargs = {"region_name": settings.aws_region}
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
                session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
                if settings.aws_session_token:
                    session_kwargs["aws_session_token"] = settings.aws_session_token

            client = boto3.client("bedrock-runtime", **session_kwargs)
            self._client = client
            self._has_live_credentials = True
            return client
        except Exception as e:
            logger.warning(f"Unable to initialize AWS Bedrock client: {e}. Falling back to demo mode.")
            self._has_live_credentials = False
            return None

    def converse(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        context_data: Optional[str] = None
    ) -> Tuple[str, str, str, bool]:
        """
        Sends conversation messages to Amazon Bedrock Converse API.
        Returns: (response_text, provider_name, model_id, is_fallback)
        """
        # Step 1: Ensure all messages have sensitive secrets redacted before sending
        sanitized_messages = []
        for msg in messages:
            redacted = redaction_service.redact(msg["content"])
            sanitized_messages.append({
                "role": msg["role"],
                "content": [{"text": redacted.clean_text}]
            })

        # Check if we should use fallback mode
        if settings.bedrock_mode == "force_demo":
            fallback_text = self._generate_fallback_response(messages, context_data)
            return fallback_text, "deterministic_fallback", "offline-rule-engine", True

        client = self._get_client()
        if not client:
            fallback_text = self._generate_fallback_response(messages, context_data)
            return fallback_text, "deterministic_fallback", "offline-rule-engine", True

        sys_prompt = system_prompt or self.SYSTEM_PROMPT
        if context_data:
            redacted_context = redaction_service.redact(context_data).clean_text
            sys_prompt += f"\n\nRelevant Context:\n{redacted_context}"

        try:
            response = client.converse(
                modelId=settings.bedrock_model_id,
                messages=sanitized_messages,
                system=[{"text": sys_prompt}],
                inferenceConfig={"temperature": 0.2, "maxTokens": 2048}
            )
            output_text = response["output"]["message"]["content"][0]["text"]
            return output_text, "amazon_bedrock", settings.bedrock_model_id, False

        except (NoCredentialsError, ClientError, BotoCoreError) as e:
            logger.warning(f"Amazon Bedrock Converse call failed ({type(e).__name__}): {e}. Using deterministic fallback.")
            fallback_text = self._generate_fallback_response(messages, context_data, error_reason=str(e))
            return fallback_text, "deterministic_fallback", "offline-rule-engine", True

    def _generate_fallback_response(
        self,
        messages: List[Dict[str, str]],
        context_data: Optional[str] = None,
        error_reason: Optional[str] = None
    ) -> str:
        """
        Generates deterministic, helpful responses when AWS credentials are not active.
        """
        last_user_msg = messages[-1]["content"] if messages else ""
        query_lower = last_user_msg.lower()

        header = "[Demo Fallback Mode — Deterministic Assistant]"
        if error_reason:
            header += f"\n*(Notice: Amazon Bedrock was unreachable: {error_reason})*\n"

        if "rust" in query_lower or "cryptography" in query_lower:
            return (
                f"{header}\n\n"
                "### Root Cause Diagnosis\n"
                "The build failure occurs because the package `cryptography` requires compiling native extensions using the Rust toolchain (`cargo` / `rustc`). "
                "The base container environment does not contain the Rust compiler.\n\n"
                "### Recommended Solution\n"
                "1. **Upgrade Pip**: Outdated pip versions cannot fetch prebuilt `manylinux` wheels.\n"
                "```dockerfile\n"
                "RUN pip install --upgrade pip setuptools wheel\n"
                "```\n"
                "2. **Or install the Rust compiler** in your Dockerfile build stage:\n"
                "```dockerfile\n"
                "RUN apt-get update && apt-get install -y cargo rustc build-essential\n"
                "```"
            )

        if "docker" in query_lower or "dockerfile" in query_lower:
            return (
                f"{header}\n\n"
                "### Docker Optimization & Debugging\n"
                "1. **Multi-stage builds**: Use a builder stage with full toolchains (`build-essential`, `gcc`) and copy only artifacts into the slim runtime image.\n"
                "2. **Cache invalidation**: Place `COPY requirements.txt .` before copying the rest of your application code.\n"
                "3. **Inspect exit code**: Exit code 1 indicates a command failure inside the RUN step; re-run with `DOCKER_BUILDKIT=1 docker build --progress=plain .`."
            )

        if "pytest" in query_lower or "test" in query_lower:
            return (
                f"{header}\n\n"
                "### Test Diagnostic Summary\n"
                "1. **Validation Mismatch**: An unhandled `ValidationError` yielded HTTP 500 instead of HTTP 422.\n"
                "2. **Database Refusal**: The PostgreSQL service at `127.0.0.1:5432` was offline. In automated tests, use SQLite in-memory fixtures or testcontainers."
            )

        return (
            f"{header}\n\n"
            f"I have received your inquiry: *\"{last_user_msg}\"*\n\n"
            "**Recommended Diagnostic Workflow**:\n"
            "1. Inspect the stack trace coordinates and error logs for failing module imports.\n"
            "2. Verify that environment variables and required system packages are present.\n"
            "3. Redact any credentials from logs before sharing in CI/CD reports.\n\n"
            "*To enable live Amazon Bedrock responses with Claude 3.5 Sonnet, configure your AWS credentials in `.env`.*"
        )

bedrock_service = BedrockService()
