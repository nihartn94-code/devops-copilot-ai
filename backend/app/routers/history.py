from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from backend.app.database import delete_analysis_by_id, get_analyses, get_analysis_by_id

router = APIRouter(prefix="/api/history", tags=["Reports & History"])

@router.get("")
async def list_history(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    type: Optional[str] = Query(default=None)
) -> List[Dict[str, Any]]:
    """
    Returns paginated list of past analyses.
    """
    return await get_analyses(limit=limit, offset=offset, analysis_type=type)

@router.get("/{analysis_id}")
async def get_analysis_detail(analysis_id: str) -> Dict[str, Any]:
    """
    Retrieves full details for a specific analysis record.
    """
    analysis = await get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    Deletes an analysis record.
    """
    deleted = await delete_analysis_by_id(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"status": "success", "deleted_id": analysis_id}

@router.get("/{analysis_id}/export-markdown")
async def export_markdown_report(analysis_id: str):
    """
    Formats the analysis as a structured markdown document for CI/CD reports.
    """
    analysis = await get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    title = analysis.get("title", "DevOps Copilot Analysis Report")
    atype = analysis.get("analysis_type", "General")
    created = analysis.get("created_at", "")
    provider = analysis.get("provider", "system")
    summary = analysis.get("summary", "")
    struct = analysis.get("structured_output", {})

    md_lines = [
        f"# {title}",
        f"**Analysis Type**: `{atype}`  ",
        f"**Generated**: `{created}`  ",
        f"**Engine**: `{provider}`  ",
        "",
        "## Summary",
        summary,
        "",
        "## Diagnostic Details",
    ]

    if atype == "build_log":
        evidence = struct.get("observed_evidence", {})
        hypo = struct.get("ai_hypothesis", {})
        md_lines.extend([
            f"- **Error Type**: `{evidence.get('error_type')}`",
            f"- **Failed Target**: `{evidence.get('failed_command_or_file')}`",
            f"- **Exit Code**: `{evidence.get('exit_code')}`",
            "",
            "### Observed Context Snippet",
            "```log",
            evidence.get("context_snippet", ""),
            "```",
            "",
            "### AI Root-Cause Hypothesis",
            hypo.get("explanation", ""),
            "",
            "### Prioritized Debugging Steps",
        ])
        for step in hypo.get("prioritized_debugging_steps", []):
            md_lines.append(f"1. {step}")
        if hypo.get("recommended_fix_code"):
            md_lines.extend([
                "",
                "### Recommended Fix Code",
                "```",
                hypo.get("recommended_fix_code", ""),
                "```"
            ])

    elif atype == "test_result":
        md_lines.extend([
            f"- **Framework**: `{struct.get('framework')}`",
            f"- **Total Tests**: {struct.get('total_tests')}",
            f"- **Passed**: {struct.get('passed')}",
            f"- **Failed**: {struct.get('failed')}",
            "",
            "### Failed Tests Breakdown",
        ])
        for ft in struct.get("failed_tests", []):
            md_lines.extend([
                f"#### ❌ {ft.get('test_name')}",
                f"- **Location**: `{ft.get('file_path')}`",
                f"- **Assertion Type**: `{ft.get('assertion_type')}`",
                "```",
                ft.get("failure_message", ""),
                "```"
            ])
        if struct.get("remedy_patch"):
            md_lines.extend([
                "",
                "### Proposed Remedy Patch",
                "```",
                struct.get("remedy_patch", ""),
                "```"
            ])

    md_content = "\n".join(md_lines)
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=devops-copilot-report-{analysis_id}.md"}
    )
