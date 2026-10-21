import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from backend.app.database import save_analysis
from backend.app.models import RepoInspectionRequest, RepoInspectionResponse
from backend.app.services.repo_service import repo_inspector

router = APIRouter(prefix="/api/repo", tags=["Repository Inspector"])

@router.post("/inspect", response_model=RepoInspectionResponse)
async def inspect_repository(req: RepoInspectionRequest):
    """
    Safely inspects an authorized local repository directory.
    Strictly read-only, checks against path traversal, and flags vulnerabilities.
    """
    try:
        resolved_path = repo_inspector.validate_and_resolve_path(req.repo_path)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    analysis_data = repo_inspector.inspect(resolved_path)
    analysis_id = f"repo-{uuid.uuid4().hex[:10]}"
    now_str = datetime.now(timezone.utc).isoformat()

    langs_summary = ", ".join(analysis_data["languages_detected"][:3]) or "Unknown"
    summary_msg = f"Detected stack: {langs_summary}. Git repo: {analysis_data['git_status'].get('is_git_repo', False)}"

    resp = RepoInspectionResponse(
        id=analysis_id,
        repo_path=str(resolved_path),
        languages_detected=analysis_data["languages_detected"],
        frameworks_detected=analysis_data["frameworks_detected"],
        config_files_found=analysis_data["config_files_found"],
        git_status=analysis_data["git_status"],
        potential_issues=analysis_data["potential_issues"],
        recommendations=analysis_data["recommendations"],
        secrets_redacted_count=0,
        provider="local_inspector",
        model_id="safe-git-parser",
        is_fallback=False,
        created_at=now_str
    )

    await save_analysis(
        analysis_id=analysis_id,
        analysis_type="repo_inspection",
        title=f"Repo: {resolved_path.name}",
        summary=summary_msg,
        raw_input=str(resolved_path),
        structured_output=resp.model_dump(),
        provider="local_inspector",
        model_id="safe-git-parser",
        secrets_redacted_count=0
    )

    return resp

@router.get("/sample-path")
async def get_sample_repo_path():
    """
    Returns the path of the bundled sample repository for instant demonstration.
    """
    sample_dir = Path(__file__).resolve().parent.parent.parent.parent / "sample-data" / "sample-repo"
    return {
        "sample_repo_path": str(sample_dir),
        "exists": sample_dir.exists()
    }
