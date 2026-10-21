import React, { useEffect, useState } from 'react';
import {
  Terminal,
  Upload,
  Copy,
  Check,
  ShieldAlert,
  Sparkles,
  FileCode,
  AlertOctagon,
  ArrowRight,
  MessageSquare,
  ListOrdered
} from 'lucide-react';
import { api } from '../services/api';
import { BuildLogResponse, SampleItem } from '../types/api';

interface BuildLogViewProps {
  onStartChatWithContext?: (analysisId: string, initialPrompt: string) => void;
  showToast: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const BuildLogView: React.FC<BuildLogViewProps> = ({ onStartChatWithContext, showToast }) => {
  const [logInput, setLogInput] = useState<string>('');
  const [samples, setSamples] = useState<SampleItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<BuildLogResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'evidence' | 'hypothesis'>('evidence');
  const [copiedCode, setCopiedCode] = useState<boolean>(false);

  useEffect(() => {
    api.getSampleLogs().then(setSamples).catch(() => {});
  }, []);

  const handleAnalyze = async (contentToAnalyze?: string) => {
    const text = contentToAnalyze || logInput;
    if (!text.trim()) {
      showToast('Please paste a build log or select a sample first.', 'error');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const resp = await api.analyzeBuildLog(text);
      setResult(resp);
      showToast('Build log successfully parsed and diagnosed!', 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to analyze build log', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      showToast('File exceeds 5MB upload limit.', 'error');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const resp = await api.uploadBuildLogFile(file);
      setResult(resp);
      setLogInput(file.name + ' uploaded');
      showToast(`Analyzed ${file.name} successfully`, 'success');
    } catch (err: any) {
      showToast(err.message || 'File upload analysis failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    showToast('Code copied to clipboard', 'success');
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
          <Terminal className="w-6 h-6 text-blue-400" />
          <span>Build-Log Analyzer</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Detects errors and warnings, isolates relevant error lines, redacts credentials, and provides root cause analysis.
        </p>
      </div>

      {/* Input Section */}
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 space-y-4">
        {/* Sample pickers */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-medium mr-1">Load Safe Sample:</span>
          {samples.map((sample) => (
            <button
              key={sample.id}
              onClick={() => {
                setLogInput(sample.content);
                handleAnalyze(sample.content);
              }}
              className="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition"
            >
              {sample.filename.replace('.log', '')}
            </button>
          ))}
        </div>

        {/* Textarea */}
        <textarea
          value={logInput}
          onChange={(e) => setLogInput(e.target.value)}
          placeholder="Paste build terminal output, compiler errors, or Docker BuildKit logs here..."
          rows={7}
          className="w-full p-4 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition resize-y"
        />

        {/* Action buttons */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <label className="cursor-pointer inline-flex items-center space-x-2 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition">
            <Upload className="w-4 h-4 text-slate-400" />
            <span>Upload Log File (.log, .txt)</span>
            <input type="file" accept=".log,.txt" onChange={handleFileUpload} className="hidden" />
          </label>

          <button
            onClick={() => handleAnalyze()}
            disabled={loading || !logInput.trim()}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-semibold shadow-lg shadow-blue-600/30 transition"
          >
            <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Analyzing Log...' : 'Run Diagnostics'}</span>
          </button>
        </div>
      </div>

      {/* Secret Redaction Banner */}
      {result && result.secrets_redacted_count > 0 && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center space-x-3 text-amber-400">
          <ShieldAlert className="w-5 h-5 shrink-0" />
          <div className="text-xs">
            <span className="font-bold">Zero Secret Leakage Protection: </span>
            {result.secrets_redacted_count} sensitive credential(s) or API key(s) were automatically redacted before analysis.
          </div>
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          {/* Top metadata bar */}
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Detected Tool:</span>
              <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                {result.tool_detected.toUpperCase()}
              </span>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Exit Code:</span>
              <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                {result.observed_evidence.exit_code ?? 1}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400">Analysis Provider:</span>
              <span
                className={`text-xs px-2 py-0.5 rounded font-mono font-semibold ${
                  result.is_fallback
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}
              >
                {result.is_fallback ? 'Demo Rule Engine (Offline Fallback)' : `Bedrock (${result.model_id})`}
              </span>
            </div>
          </div>

          {/* Dual Panel: Evidence vs Hypothesis Tabs */}
          <div className="border border-slate-800 rounded-xl bg-slate-900/40 overflow-hidden shadow-sm">
            <div className="flex border-b border-slate-800 bg-slate-950/80">
              <button
                onClick={() => setActiveTab('evidence')}
                className={`px-6 py-3 text-xs font-semibold tracking-wider uppercase border-b-2 transition ${
                  activeTab === 'evidence'
                    ? 'border-blue-500 text-blue-400 bg-slate-900/40'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                1. Observed Evidence (Exact Logs)
              </button>
              <button
                onClick={() => setActiveTab('hypothesis')}
                className={`px-6 py-3 text-xs font-semibold tracking-wider uppercase border-b-2 transition ${
                  activeTab === 'hypothesis'
                    ? 'border-blue-500 text-blue-400 bg-slate-900/40'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                2. AI Root-Cause Hypothesis & Steps
              </button>
            </div>

            <div className="p-6">
              {activeTab === 'evidence' ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                      <div className="text-xs text-slate-400 font-medium">Error Classification</div>
                      <div className="text-sm font-semibold text-rose-400 mt-1">
                        {result.observed_evidence.error_type}
                      </div>
                    </div>
                    <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                      <div className="text-xs text-slate-400 font-medium">Failing Command or Target</div>
                      <div className="text-sm font-mono text-slate-200 mt-1 truncate">
                        {result.observed_evidence.failed_command_or_file || 'Subprocess Execution Step'}
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-slate-400 font-medium mb-2">Primary Error Message</div>
                    <div className="p-3.5 rounded-lg bg-slate-950 border border-rose-900/40 text-rose-300 font-mono text-xs">
                      {result.observed_evidence.primary_error_message}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs text-slate-400 font-medium mb-2">Surrounding Log Context Window</div>
                    <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 font-mono text-xs overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-80">
                      {result.observed_evidence.context_snippet}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Confidence rating */}
                  <div className="flex items-center justify-between p-3.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-xs text-slate-400">Diagnosis Confidence</div>
                    <div className="text-xs font-mono font-bold text-emerald-400">
                      {Math.round(result.ai_hypothesis.confidence_score * 100)}% Certainty
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                      Likely Root Cause
                    </h4>
                    <p className="text-sm text-slate-200 leading-relaxed p-4 rounded-lg bg-slate-950 border border-slate-800">
                      {result.ai_hypothesis.likely_root_cause}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                      Detailed Technical Explanation
                    </h4>
                    <div className="text-xs text-slate-300 leading-relaxed p-4 rounded-lg bg-slate-950 border border-slate-800 whitespace-pre-line font-sans">
                      {result.ai_hypothesis.explanation}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center space-x-1.5">
                      <ListOrdered className="w-4 h-4 text-blue-400" />
                      <span>Prioritized Debugging Steps</span>
                    </h4>
                    <div className="space-y-2">
                      {result.ai_hypothesis.prioritized_debugging_steps.map((step, idx) => (
                        <div
                          key={idx}
                          className="flex items-start space-x-3 p-3 rounded-lg bg-slate-950 border border-slate-800"
                        >
                          <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 text-xs font-bold flex items-center justify-center shrink-0">
                            {idx + 1}
                          </span>
                          <span className="text-xs text-slate-200 leading-relaxed">{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recommended Fix Section */}
          {result.ai_hypothesis.recommended_fix_code && (
            <div className="p-6 rounded-xl border border-blue-500/30 bg-blue-950/20 space-y-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center space-x-2">
                    <FileCode className="w-5 h-5 text-blue-400" />
                    <span>Recommended Fix</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    {result.ai_hypothesis.recommended_fix_description || 'Proposed code changes for manual developer verification.'}
                  </p>
                </div>
                <button
                  onClick={() => handleCopy(result.ai_hypothesis.recommended_fix_code!)}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition"
                >
                  {copiedCode ? <Check className="w-3.5 h-3.5 text-white" /> : <Copy className="w-3.5 h-3.5 text-white" />}
                  <span>{copiedCode ? 'Copied!' : 'Copy Fix'}</span>
                </button>
              </div>

              <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-cyan-300 font-mono text-xs overflow-x-auto leading-relaxed">
                {result.ai_hypothesis.recommended_fix_code}
              </pre>
            </div>
          )}

          {/* Chat follow-up action */}
          {onStartChatWithContext && (
            <div className="flex justify-end">
              <button
                onClick={() =>
                  onStartChatWithContext(
                    result.id,
                    `I analyzed the ${result.tool_detected} build error (${result.observed_evidence.error_type}). How can I debug this further?`
                  )
                }
                className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
              >
                <MessageSquare className="w-4 h-4 text-blue-400" />
                <span>Ask Follow-up in AI Debugging Chat</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
