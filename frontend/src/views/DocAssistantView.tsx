import React, { useState } from 'react';
import {
  BookOpen,
  Search,
  ExternalLink,
  Sparkles,
  FileText,
  ShieldCheck,
  Tag
} from 'lucide-react';
import { api } from '../services/api';
import { DocSearchResponse } from '../types/api';

interface DocAssistantViewProps {
  showToast: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const DocAssistantView: React.FC<DocAssistantViewProps> = ({ showToast }) => {
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<DocSearchResponse | null>(null);

  const sampleQueries = [
    'How to fix missing Rust compiler during Docker build?',
    'Amazon Bedrock Converse API request structure',
    'FastAPI validation error handling and CORS',
    'Model Context Protocol Streamable HTTP specification',
  ];

  const handleSearch = async (override?: string) => {
    const q = override || query;
    if (!q.trim()) {
      showToast('Please enter a documentation query', 'error');
      return;
    }

    setLoading(true);
    setResponse(null);
    try {
      const resp = await api.searchDocs(q, 3);
      setResponse(resp);
      showToast('Documentation retrieved!', 'success');
    } catch (err: any) {
      showToast(err.message || 'Search failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
          <BookOpen className="w-6 h-6 text-cyan-400" />
          <span>Technical Documentation Assistant</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Searches grounded, curated developer documentation with verified sources. Never invents non-existent citations.
        </p>
      </div>

      {/* Query Box */}
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Ask a technical question (e.g. Bedrock Converse, Docker debugging, FastAPI)..."
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition"
            />
          </div>
          <button
            onClick={() => handleSearch()}
            disabled={loading || !query.trim()}
            className="inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-cyan-600/30 transition shrink-0"
          >
            <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Searching...' : 'Search Docs'}</span>
          </button>
        </div>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs text-slate-500 font-medium">Quick Prompts:</span>
          {sampleQueries.map((sq, i) => (
            <button
              key={i}
              onClick={() => {
                setQuery(sq);
                handleSearch(sq);
              }}
              className="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition"
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Results View */}
      {response && (
        <div className="space-y-6">
          {/* Grounded AI Answer */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                <span>Grounded Technical Guidance</span>
              </h3>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                Grounded on {response.results.length} Verified Document(s)
              </span>
            </div>

            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
              {response.ai_answer}
            </div>
          </div>

          {/* Sourced Citations */}
          {response.results.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <FileText className="w-5 h-5 text-blue-400" />
                <span>Verified Source Documents</span>
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {response.results.map((r, i) => (
                  <div
                    key={i}
                    className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 flex flex-col justify-between space-y-3"
                  >
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white truncate pr-2">{r.title}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 shrink-0">
                          {Math.round(r.relevance_score * 100)}% Match
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed line-clamp-4">
                        {r.excerpt}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                      <span className="text-slate-500 font-mono text-[11px] truncate">{r.source_file}</span>
                      {r.source_url && (
                        <a
                          href={r.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 font-medium shrink-0 ml-2"
                        >
                          <span>Official Docs</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
