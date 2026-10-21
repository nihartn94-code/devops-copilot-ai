import React, { useEffect, useState } from 'react';
import {
  History,
  FileText,
  Download,
  Trash2,
  RefreshCw,
  Eye,
  X,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  Terminal,
  FolderGit2,
  BookOpen
} from 'lucide-react';
import { api } from '../services/api';

interface HistoryViewProps {
  showToast: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ showToast }) => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [activeModalData, setActiveModalData] = useState<any | null>(null);

  const loadHistory = async (typeFilter?: string) => {
    setLoading(true);
    try {
      const type = (typeFilter || selectedType) === 'all' ? undefined : (typeFilter || selectedType);
      const data = await api.getHistory(50, type);
      setItems(data);
    } catch (err: any) {
      showToast(err.message || 'Failed to load history', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [selectedType]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this analysis report?')) return;
    try {
      await api.deleteAnalysis(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
      showToast('Analysis deleted', 'success');
      if (activeModalData?.id === id) setActiveModalData(null);
    } catch (err: any) {
      showToast(err.message || 'Delete failed', 'error');
    }
  };

  const handleOpenDetail = async (id: string) => {
    try {
      const detail = await api.getAnalysisDetail(id);
      setActiveModalData(detail);
    } catch (err: any) {
      showToast('Failed to load analysis details', 'error');
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'build_log':
        return <Terminal className="w-4 h-4 text-blue-400" />;
      case 'repo_inspection':
        return <FolderGit2 className="w-4 h-4 text-emerald-400" />;
      case 'test_result':
        return <CheckCircle2 className="w-4 h-4 text-purple-400" />;
      case 'doc_search':
        return <BookOpen className="w-4 h-4 text-cyan-400" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
            <History className="w-6 h-6 text-blue-400" />
            <span>Analysis History & Saved Reports</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Persisted in local SQLite database. Reopen, review, or export reports for CI/CD attachment.
          </p>
        </div>

        <button
          onClick={() => loadHistory()}
          className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2">
        {['all', 'build_log', 'repo_inspection', 'test_result', 'doc_search'].map((t) => (
          <button
            key={t}
            onClick={() => setSelectedType(t)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition ${
              selectedType === t
                ? 'bg-blue-600 text-white shadow'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            {t.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* History List */}
      <div className="space-y-3">
        {loading ? (
          <div className="py-16 text-center text-slate-500 text-sm">Loading past analyses...</div>
        ) : items.length === 0 ? (
          <div className="py-16 text-center text-slate-500 text-sm border border-dashed border-slate-800 rounded-xl">
            No saved analyses match the current filter.
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              onClick={() => handleOpenDetail(item.id)}
              className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-800/40 hover:border-slate-700 transition cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="flex items-start space-x-3.5 min-w-0">
                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 shrink-0 mt-0.5">
                  {getTypeIcon(item.analysis_type)}
                </div>
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-semibold text-white truncate">{item.title}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {item.analysis_type.replace('_', ' ')}
                    </span>
                    {item.secrets_redacted_count > 0 && (
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                        {item.secrets_redacted_count} secret(s) redacted
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 truncate max-w-2xl">{item.summary}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3 shrink-0 self-end sm:self-center">
                <span className="text-xs text-slate-500 font-mono">
                  {new Date(item.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                </span>
                <a
                  href={api.getMarkdownExportUrl(item.id)}
                  download
                  onClick={(e) => e.stopPropagation()}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-cyan-400 transition"
                  title="Download Markdown Report"
                >
                  <Download className="w-4 h-4" />
                </a>
                <button
                  onClick={(e) => handleDelete(item.id, e)}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-rose-400 transition"
                  title="Delete record"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal Detail Viewer */}
      {activeModalData && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white">{activeModalData.title}</h3>
                <span className="text-xs text-slate-400 font-mono">ID: {activeModalData.id}</span>
              </div>
              <div className="flex items-center space-x-2">
                <a
                  href={api.getMarkdownExportUrl(activeModalData.id)}
                  download
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download .md</span>
                </a>
                <button
                  onClick={() => setActiveModalData(null)}
                  className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto space-y-4">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Summary
                </span>
                <p className="text-xs text-slate-200 leading-relaxed p-3 rounded-lg bg-slate-950 border border-slate-800">
                  {activeModalData.summary}
                </p>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Structured Output Payload (JSON)
                </span>
                <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-cyan-300 overflow-x-auto max-h-96 leading-relaxed">
                  {JSON.stringify(activeModalData.structured_output, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
