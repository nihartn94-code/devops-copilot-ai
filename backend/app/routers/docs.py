import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import APIRouter
from backend.app.database import save_analysis
from backend.app.models import DocSearchRequest, DocSearchResponse
from backend.app.services.doc_service import doc_service

router = APIRouter(prefix="/api/docs", tags=["Documentation Assistant"])

@router.post("/search", response_model=DocSearchResponse)
async def search_documentation(req: DocSearchRequest):
    """
    Searches curated developer documentation and provides grounded answers with source links.
    """
    results, ai_answer = doc_service.search(req.query, max_results=req.max_results or 3)
    analysis_id = f"doc-{uuid.uuid4().hex[:10]}"
    now_str = datetime.now(timezone.utc).isoformat()

    resp = DocSearchResponse(
        query=req.query,
        results=results,
        ai_answer=ai_answer,
        provider="curated_documentation_index",
        model_id="doc-keyword-ranker",
        is_fallback=False,
        created_at=now_str
    )

    # Persist in SQLite
    await save_analysis(
        analysis_id=analysis_id,
        analysis_type="doc_search",
        title=f"Doc Search: {req.query[:40]}",
        summary=ai_answer[:200],
        raw_input=req.query,
        structured_output=resp.model_dump(),
        provider="curated_documentation_index",
        model_id="doc-keyword-ranker",
        secrets_redacted_count=0
    )

    return resp

@router.get("/list")
async def list_documentation_topics() -> List[Dict[str, str]]:
    """
    Lists available indexed documentation topics and external sources.
    """
    unique_files: Dict[str, Dict[str, str]] = {}
    for item in doc_service.docs:
        fn = item["file_name"]
        if fn not in unique_files:
            unique_files[fn] = {
                "file_name": fn,
                "title": item["title"].split(" › ")[0],
                "source_url": item["source_url"] or ""
            }
    return list(unique_files.values())
