export interface ObservedEvidence {
  error_type: string;
  primary_error_message: string;
  failed_command_or_file?: string | null;
  line_number?: number | null;
  exit_code?: number | null;
  context_snippet: string;
  extracted_tokens: string[];
}

export interface AnalysisHypothesis {
  likely_root_cause: string;
  confidence_score: number;
  explanation: string;
  prioritized_debugging_steps: string[];
  recommended_fix_code?: string | null;
  recommended_fix_description?: string | null;
}

export interface BuildLogResponse {
  id: string;
  tool_detected: string;
  secrets_redacted_count: number;
  observed_evidence: ObservedEvidence;
  ai_hypothesis: AnalysisHypothesis;
  provider: string;
  model_id: string;
  is_fallback: boolean;
  created_at: string;
}

export interface GitStatus {
  is_git_repo: boolean;
  branch?: string;
  is_clean?: boolean;
  modified_files?: string[];
  untracked_files?: string[];
  recent_commits?: string[];
  message?: string;
  error?: string;
}

export interface RepoIssue {
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
}

export interface RepoInspectionResponse {
  id: string;
  repo_path: string;
  languages_detected: string[];
  frameworks_detected: string[];
  config_files_found: string[];
  git_status: GitStatus;
  potential_issues: RepoIssue[];
  recommendations: string[];
  secrets_redacted_count: number;
  provider: string;
  model_id: string;
  is_fallback: boolean;
  created_at: string;
}

export interface FailedTestDetail {
  test_name: string;
  file_path?: string | null;
  failure_message: string;
  stack_trace: string;
  assertion_type?: string | null;
}

export interface TestAnalysisResponse {
  id: string;
  framework: string;
  total_tests: number;
  passed: number;
  failed: number;
  skipped: number;
  failed_tests: FailedTestDetail[];
  root_cause_summary: string;
  next_steps: string[];
  remedy_patch?: string | null;
  secrets_redacted_count: number;
  provider: string;
  model_id: string;
  is_fallback: boolean;
  created_at: string;
}

export interface DocSearchResult {
  title: string;
  source_file: string;
  source_url?: string | null;
  relevance_score: number;
  excerpt: string;
}

export interface DocSearchResponse {
  query: string;
  results: DocSearchResult[];
  ai_answer: string;
  provider: string;
  model_id: string;
  is_fallback: boolean;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  analysis_id?: string | null;
  role: 'user' | 'assistant';
  content: string;
  provider: string;
  model_id: string;
  is_fallback: boolean;
  created_at: string;
}

export interface DashboardStats {
  total_analyses: number;
  total_build_logs: number;
  total_tests: number;
  total_repos: number;
  total_docs: number;
  total_secrets_redacted: number;
  recent_analyses: Array<{
    id: string;
    created_at: string;
    analysis_type: string;
    title: string;
    summary: string;
    provider: string;
    model_id: string;
  }>;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  version: string;
  bedrock_mode: string;
  bedrock_model_id: string;
  aws_credentials_configured: boolean;
  mcp_server_target: string;
}

export interface SampleItem {
  id: string;
  filename: string;
  content: string;
}
