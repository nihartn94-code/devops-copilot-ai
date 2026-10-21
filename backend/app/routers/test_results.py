import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from backend.app.database import save_analysis
from backend.app.models import TestAnalysisRequest, TestAnalysisResponse
from backend.app.services.redaction_service import redaction_service
from backend.app.services.test_analyzer_service import test_analyzer_service

router = APIRouter(prefix="/api/test-results", tags=["Test Results"])

@router.post("/analyze", response_model=TestAnalysisResponse)
async def analyze_test_output(req: TestAnalysisRequest):
    """
    Parses test runner output, extracts failed assertions, and provides diagnostic remedies.
    """
    # Redact secrets
    redacted = redaction_service.redact(req.test_output)
    clean_output = redacted.clean_text

    result = test_analyzer_service.analyze(clean_output, req.framework)
    analysis_id = f"test-{uuid.uuid4().hex[:10]}"
    now_str = datetime.now(timezone.utc).isoformat()

    resp = TestAnalysisResponse(
        id=analysis_id,
        framework=result["framework"],
        total_tests=result["total_tests"],
        passed=result["passed"],
        failed=result["failed"],
        skipped=result["skipped"],
        failed_tests=result["failed_tests"],
        root_cause_summary=result["root_cause_summary"],
        next_steps=result["next_steps"],
        remedy_patch=result["remedy_patch"],
        secrets_redacted_count=redacted.secrets_detected,
        provider="deterministic_fallback",
        model_id="test-rule-analyzer",
        is_fallback=True,
        created_at=now_str
    )

    await save_analysis(
        analysis_id=analysis_id,
        analysis_type="test_result",
        title=f"{result['framework'].upper()} Test Suite: {result['failed']} Failed / {result['total_tests']} Total",
        summary=result["root_cause_summary"][:200],
        raw_input=clean_output[:4000],
        structured_output=resp.model_dump(),
        provider="deterministic_fallback",
        model_id="test-rule-analyzer",
        secrets_redacted_count=redacted.secrets_detected
    )

    return resp

@router.get("/samples")
async def get_sample_test_outputs() -> List[Dict[str, str]]:
    """
    Returns pre-packaged sample test outputs for testing.
    """
    samples_dir = Path(__file__).resolve().parent.parent.parent.parent / "sample-data" / "tests"
    samples = []
    if samples_dir.exists():
        for f in samples_dir.glob("*.txt"):
            try:
                samples.append({
                    "id": f.stem,
                    "filename": f.name,
                    "content": f.read_text(encoding="utf-8")
                })
            except Exception:
                continue
    return samples
