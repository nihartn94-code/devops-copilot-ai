import {
  BuildLogResponse,
  ChatMessage,
  DashboardStats,
  DocSearchResponse,
  HealthStatus,
  RepoInspectionResponse,
  SampleItem,
  TestAnalysisResponse
} from '../types/api';

const API_BASE = '/api';

export const api = {
  async getHealth(): Promise<HealthStatus> {
    const res = await fetch('/health');
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    if (!res.ok) throw new Error('Failed to load dashboard metrics');
    return res.json();
  },

  async analyzeBuildLog(logContent: string, buildTool?: string): Promise<BuildLogResponse> {
    const res = await fetch(`${API_BASE}/build-logs/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ log_content: logContent, build_tool: buildTool || null }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(err.detail || 'Build log analysis failed');
    }
    return res.json();
  },

  async uploadBuildLogFile(file: File): Promise<BuildLogResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/build-logs/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'File upload failed');
    }
    return res.json();
  },

  async getSampleLogs(): Promise<SampleItem[]> {
    const res = await fetch(`${API_BASE}/build-logs/samples`);
    if (!res.ok) return [];
    return res.json();
  },

  async inspectRepo(repoPath: string): Promise<RepoInspectionResponse> {
    const res = await fetch(`${API_BASE}/repo/inspect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_path: repoPath }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Inspection failed' }));
      throw new Error(err.detail || 'Repository inspection failed');
    }
    return res.json();
  },

  async getSampleRepoPath(): Promise<{ sample_repo_path: string; exists: boolean }> {
    const res = await fetch(`${API_BASE}/repo/sample-path`);
    if (!res.ok) throw new Error('Failed to get sample repo path');
    return res.json();
  },

  async analyzeTestResults(testOutput: string, framework?: string): Promise<TestAnalysisResponse> {
    const res = await fetch(`${API_BASE}/test-results/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ test_output: testOutput, framework: framework || null }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Test analysis failed' }));
      throw new Error(err.detail || 'Test result analysis failed');
    }
    return res.json();
  },

  async getSampleTests(): Promise<SampleItem[]> {
    const res = await fetch(`${API_BASE}/test-results/samples`);
    if (!res.ok) return [];
    return res.json();
  },

  async searchDocs(query: string, maxResults: number = 3): Promise<DocSearchResponse> {
    const res = await fetch(`${API_BASE}/docs/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, max_results: maxResults }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Search failed' }));
      throw new Error(err.detail || 'Doc search failed');
    }
    return res.json();
  },

  async sendChatMessage(sessionId: string, message: string, analysisId?: string): Promise<ChatMessage> {
    const res = await fetch(`${API_BASE}/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message, analysis_id: analysisId || null }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Chat error' }));
      throw new Error(err.detail || 'Failed to send chat message');
    }
    return res.json();
  },

  async getChatHistory(sessionId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${API_BASE}/chat/history/${sessionId}`);
    if (!res.ok) return [];
    return res.json();
  },

  async getHistory(limit: number = 50, type?: string): Promise<any[]> {
    const url = type ? `${API_BASE}/history?limit=${limit}&type=${type}` : `${API_BASE}/history?limit=${limit}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to load history');
    return res.json();
  },

  async getAnalysisDetail(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/history/${id}`);
    if (!res.ok) throw new Error('Analysis not found');
    return res.json();
  },

  async deleteAnalysis(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete analysis');
  },

  getMarkdownExportUrl(id: string): string {
    return `${API_BASE}/history/${id}/export-markdown`;
  }
};
