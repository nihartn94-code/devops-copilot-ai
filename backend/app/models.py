from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class RedactionResult(BaseModel):
    clean_text: str
    secrets_detected: int = 0
    redactions: List[str] = Field(default_factory=list)

class ObservedEvidence(BaseModel):
    error_type: str = "UnknownError"
    primary_error_message: str
    failed_command_or_file: Optional[str] = None
    line_number: Optional[int] = None
    exit_code: Optional[int] = None
    context_snippet: str
    extracted_tokens: List[str] = Field(default_factory=list)

class AnalysisHypothesis(BaseModel):
    likely_root_cause: str
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.9)
    explanation: str
    prioritized_debugging_steps: List[str] = Field(default_factory=list)
    recommended_fix_code: Optional[str] = None
    recommended_fix_description: Optional[str] = None

class BuildLogAnalysisRequest(BaseModel):
    log_content: str = Field(..., min_length=5, description="Raw text of the build log")
    build_tool: Optional[str] = Field(default=None, description="Optional tool hint: docker, npm, maven, gradle, python")

class BuildLogAnalysisResponse(BaseModel):
    id: str
    tool_detected: str
    secrets_redacted_count: int = 0
    observed_evidence: ObservedEvidence
    ai_hypothesis: AnalysisHypothesis
    provider: str
    model_id: str
    is_fallback: bool
    created_at: str

class RepoInspectionRequest(BaseModel):
    repo_path: str = Field(..., description="Target authorized repository directory")

class RepoInspectionResponse(BaseModel):
    id: str
    repo_path: str
    languages_detected: List[str] = Field(default_factory=list)
    frameworks_detected: List[str] = Field(default_factory=list)
    config_files_found: List[str] = Field(default_factory=list)
    git_status: Dict[str, Any] = Field(default_factory=dict)
    potential_issues: List[Dict[str, str]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    secrets_redacted_count: int = 0
    provider: str
    model_id: str
    is_fallback: bool
    created_at: str

class FailedTestDetail(BaseModel):
    test_name: str
    file_path: Optional[str] = None
    failure_message: str
    stack_trace: str
    assertion_type: Optional[str] = None

class TestAnalysisRequest(BaseModel):
    test_output: str = Field(..., min_length=5, description="Raw test runner output")
    framework: Optional[str] = Field(default=None, description="Optional framework hint: pytest, jest, junit")

class TestAnalysisResponse(BaseModel):
    id: str
    framework: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    failed_tests: List[FailedTestDetail] = Field(default_factory=list)
    root_cause_summary: str
    next_steps: List[str] = Field(default_factory=list)
    remedy_patch: Optional[str] = None
    secrets_redacted_count: int = 0
    provider: str
    model_id: str
    is_fallback: bool
    created_at: str

class DocSearchResult(BaseModel):
    title: str
    source_file: str
    source_url: Optional[str] = None
    relevance_score: float
    excerpt: str

class DocSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Technical question or topic")
    max_results: Optional[int] = Field(default=3, ge=1, le=10)

class DocSearchResponse(BaseModel):
    query: str
    results: List[DocSearchResult] = Field(default_factory=list)
    ai_answer: str
    provider: str
    model_id: str
    is_fallback: bool
    created_at: str

class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="Unique conversational thread identifier")
    message: str = Field(..., min_length=1, description="User prompt or question")
    analysis_id: Optional[str] = Field(default=None, description="Optional reference to previous analysis")

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    analysis_id: Optional[str] = None
    role: str
    content: str
    provider: str
    model_id: str
    is_fallback: bool
    created_at: str

class DashboardStatsResponse(BaseModel):
    total_analyses: int
    total_build_logs: int
    total_tests: int
    total_repos: int
    total_docs: int
    total_secrets_redacted: int
    recent_analyses: List[Dict[str, Any]]
