import React, { useEffect, useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Copy,
  Check,
  Download,
  Sparkles,
  FileCode,
  Layers,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { SampleItem, TestAnalysisResponse } from '../types/api';

interface TestAnalyzerViewProps {
  showToast: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const TestAnalyzerView: React.FC<TestAnalyzerViewProps> = ({ showToast }) => {
  const [testInput, setTestInput] = useState<string>('');
  const [samples, setSamples] = useState<SampleItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<TestAnalysisResponse | null>(null);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);
  const [copiedPatch, setCopiedPatch] = useState<boolean>(false);

  useEffect(() => {
    api.getSampleTests().then(setSamples).catch(() => {});
  }, []);

  const handleAnalyze = async (override?: string) => {
    const text = override || testInput;
    if (!text.trim()) {
      showToast('Please paste test output or select a sample first.', 'error');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const resp = await api.analyzeTestResults(text);
      setResult(resp);
      showToast('Test results parsed and diagnosed!', 'success');
    } catch (err: any) {
      showToast(err.message || 'Analysis failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedPatch(true);
    showToast('Remedy patch copied to clipboard', 'success');
    setTimeout(() => setCopiedPatch(false), 2000);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
          <CheckCircle2 className="w-6 h-6 text-purple-400" />
          <span>Test-Result Analyzer</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Parses pytest, Jest, and JUnit outputs to isolate failing assertions, explain root causes, and propose non-destructive fixes.
        </p>
      </div>

      {/* Input Box */}
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-medium mr-1">Load Safe Sample:</span>
          {samples.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setTestInput(s.content);
                handleAnalyze(s.content);
              }}
              className="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition"
            >
              {s.filename.replace('.txt', '')}
            </button>
          ))}
        </div>

        <textarea
          value={testInput}
          onChange={(e) => setTestInput(e.target.value)}
          placeholder="Paste test runner terminal output (e.g. pytest, jest, vitest)..."
          rows={6}
          className="w-full p-4 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition resize-y"
        />

        <div className="flex justify-end">
          <button
            onClick={() => handleAnalyze()}
            disabled={loading || !testInput.trim()}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-semibold shadow-lg shadow-purple-600/30 transition"
          >
            <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Analyzing Suite...' : 'Analyze Test Results'}</span>
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary Stats Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40">
              <span className="text-xs text-slate-400 font-medium">Framework</span>
              <div className="text-lg font-mono font-bold text-white mt-1 uppercase">
                {result.framework}
              </div>
            </div>
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40">
              <span className="text-xs text-slate-400 font-medium">Total Tests</span>
              <div className="text-lg font-mono font-bold text-slate-200 mt-1">
                {result.total_tests}
              </div>
            </div>
            <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-950/10">
              <span className="text-xs text-emerald-400 font-medium">Passed</span>
              <div className="text-lg font-mono font-bold text-emerald-400 mt-1">
                {result.passed}
              </div>
            </div>
            <div className="p-4 rounded-xl border border-rose-500/20 bg-rose-950/10">
              <span className="text-xs text-rose-400 font-medium">Failed</span>
              <div className="text-lg font-mono font-bold text-rose-400 mt-1">
                {result.failed}
              </div>
            </div>
          </div>

          {/* Root Cause Summary */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-amber-400" />
              <span>Root Cause Diagnosis</span>
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed p-4 rounded-lg bg-slate-950 border border-slate-800">
              {result.root_cause_summary}
            </p>

            {/* Next Steps */}
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2">
                Suggested Next Steps
              </span>
              <div className="space-y-2">
                {result.next_steps.map((step, idx) => (
                  <div
                    key={idx}
                    className="flex items-start space-x-3 p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300"
                  >
                    <span className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 font-bold flex items-center justify-center shrink-0">
                      {idx + 1}
                    </span>
                    <span className="leading-relaxed">{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Failed Tests Breakdown */}
          {result.failed_tests.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <XCircle className="w-5 h-5 text-rose-400" />
                <span>Failed Tests ({result.failed_tests.length})</span>
              </h3>

              <div className="space-y-2.5">
                {result.failed_tests.map((test, idx) => {
                  const isExpanded = expandedIndex === idx;
                  return (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-800 bg-slate-900/40 overflow-hidden"
                    >
                      <button
                        onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                        className="w-full p-4 flex items-center justify-between text-left hover:bg-slate-800/40 transition"
                      >
                        <div className="flex items-center space-x-3 min-w-0 pr-4">
                          <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                          <div className="min-w-0">
                            <span className="text-sm font-semibold text-white font-mono truncate block">
                              {test.test_name}
                            </span>
                            {test.file_path && (
                              <span className="text-xs text-slate-400 font-mono mt-0.5 block">
                                {test.file_path}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-3 shrink-0">
                          {test.assertion_type && (
                            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                              {test.assertion_type}
                            </span>
                          )}
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-slate-400" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-slate-400" />
                          )}
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="p-4 border-t border-slate-800 bg-slate-950 space-y-3">
                          <div>
                            <span className="text-xs text-slate-400 font-medium block mb-1">Failure Message</span>
                            <pre className="p-3 rounded bg-slate-900 border border-slate-800 text-rose-300 font-mono text-xs overflow-x-auto whitespace-pre-wrap">
                              {test.failure_message}
                            </pre>
                          </div>
                          <div>
                            <span className="text-xs text-slate-400 font-medium block mb-1">Captured Stack Trace</span>
                            <pre className="p-3 rounded bg-slate-900 border border-slate-800 text-slate-400 font-mono text-xs overflow-x-auto whitespace-pre-wrap max-h-60">
                              {test.stack_trace}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Proposed Remedy Patch */}
          {result.remedy_patch && (
            <div className="p-6 rounded-xl border border-purple-500/30 bg-purple-950/20 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center space-x-2">
                    <FileCode className="w-5 h-5 text-purple-400" />
                    <span>Proposed Remedy Patch</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Review and verify before applying to your codebase.
                  </p>
                </div>
                <button
                  onClick={() => handleCopy(result.remedy_patch!)}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow transition"
                >
                  {copiedPatch ? <Check className="w-3.5 h-3.5 text-white" /> : <Copy className="w-3.5 h-3.5 text-white" />}
                  <span>{copiedPatch ? 'Copied!' : 'Copy Patch'}</span>
                </button>
              </div>

              <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-purple-300 font-mono text-xs overflow-x-auto leading-relaxed">
                {result.remedy_patch}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
