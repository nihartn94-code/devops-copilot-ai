import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter, File, HTTPException, UploadFile
from backend.app.config import settings
from backend.app.database import save_analysis
from backend.app.models import BuildLogAnalysisRequest, BuildLogAnalysisResponse
from backend.app.services.bedrock_service import bedrock_service
from backend.app.services.build_log_service import build_log_service
from backend.app.services.redaction_service import redaction_service

router = APIRouter(prefix="/api/build-logs", tags=["Build Logs"])

@router.post("/analyze", response_model=BuildLogAnalysisResponse)
async def analyze_log(req: BuildLogAnalysisRequest):
    """
    Parses build logs, redacts secrets, extracts evidence, and diagnoses root cause.
    """
    # Enforce line limits
    lines = req.log_content.splitlines()
    if len(lines) > settings.max_log_lines:
        truncated_content = "\n".join(lines[:settings.max_log_lines])
    else:
        truncated_content = req.log_content

    # Redact secrets
    redacted = redaction_service.redact(truncated_content)
    clean_log = redacted.clean_text

    # Detect tool & extract observed evidence
    tool = build_log_service.detect_tool(clean_log, req.build_tool)
    evidence = build_log_service.extract_evidence(clean_log)

    # Generate hypothesis: try Bedrock Converse if configured; otherwise use deterministic fallback
    analysis_id = f"build-{uuid.uuid4().hex[:10]}"
    now_str = datetime.now(timezone.utc).isoformat()

    if settings.bedrock_mode != "force_demo" and bedrock_service._get_client() is not None:
        prompt = (
            f"Diagnose this {tool} build failure.\n"
            f"Primary Error: {evidence.primary_error_message}\n"
            f"Error Type: {evidence.error_type}\n"
            f"Failed Command: {evidence.failed_command_or_file}\n\n"
            f"Log Context Snippet:\n{evidence.context_snippet}\n\n"
            "Provide:\n"
            "1. Likely root cause\n"
            "2. Detailed explanation\n"
            "3. Prioritized debugging steps (list of 3)\n"
            "4. Recommended fix code"
        )
        ai_resp, provider, model_id, is_fallback = bedrock_service.converse(
            messages=[{"role": "user", "content": prompt}]
        )
        # Parse into structured hypothesis
        hypothesis = build_log_service.generate_deterministic_hypothesis(evidence, tool)
        hypothesis.explanation = ai_resp
    else:
        hypothesis = build_log_service.generate_deterministic_hypothesis(evidence, tool)
        provider = "deterministic_fallback"
        model_id = "offline-rule-engine"
        is_fallback = True

    resp = BuildLogAnalysisResponse(
        id=analysis_id,
        tool_detected=tool,
        secrets_redacted_count=redacted.secrets_detected,
        observed_evidence=evidence,
        ai_hypothesis=hypothesis,
        provider=provider,
        model_id=model_id,
        is_fallback=is_fallback,
        created_at=now_str
    )

    # Persist in SQLite
    await save_analysis(
        analysis_id=analysis_id,
        analysis_type="build_log",
        title=f"{tool.upper()} Build: {evidence.error_type}",
        summary=evidence.primary_error_message,
        raw_input=clean_log[:4000],
        structured_output=resp.model_dump(),
        provider=provider,
        model_id=model_id,
        secrets_redacted_count=redacted.secrets_detected
    )

    return resp

@router.post("/upload", response_model=BuildLogAnalysisResponse)
async def upload_log_file(file: UploadFile = File(...)):
    """
    Accepts text build log files up to the configured size limit.
    """
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content_bytes = await file.read(max_bytes + 1)
    if len(content_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed upload size of {settings.max_upload_size_mb} MB"
        )

    try:
        log_text = content_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode log file as text: {e}")

    return await analyze_log(BuildLogAnalysisRequest(log_content=log_text))

@router.get("/samples")
async def get_sample_logs() -> List[Dict[str, str]]:
    """
    Returns available pre-packaged sample build logs for demo testing.
    """
    samples_dir = Path(__file__).resolve().parent.parent.parent.parent / "sample-data" / "logs"
    samples = []
    if samples_dir.exists():
        for f in samples_dir.glob("*.log"):
            try:
                samples.append({
                    "id": f.stem,
                    "filename": f.name,
                    "content": f.read_text(encoding="utf-8")
                })
            except Exception:
                continue
    return samples
