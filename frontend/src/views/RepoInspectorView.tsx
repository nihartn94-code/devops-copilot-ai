import React, { useState } from 'react';
import {
  FolderGit2,
  ShieldCheck,
  GitBranch,
  FileCode2,
  AlertTriangle,
  Lightbulb,
  Search,
  Sparkles,
  GitCommit,
  CheckCircle,
  FileCheck
} from 'lucide-react';
import { api } from '../services/api';
import { RepoInspectionResponse } from '../types/api';

interface RepoInspectorViewProps {
  showToast: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const RepoInspectorView: React.FC<RepoInspectorViewProps> = ({ showToast }) => {
  const [repoPath, setRepoPath] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<RepoInspectionResponse | null>(null);

  const handleInspect = async (pathOverride?: string) => {
    const target = pathOverride || repoPath;
    if (!target.trim()) {
      showToast('Please enter or select a repository directory path.', 'error');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const resp = await api.inspectRepo(target);
      setResult(resp);
      showToast('Repository inspected safely!', 'success');
    } catch (err: any) {
      showToast(err.message || 'Inspection failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUseSampleRepo = async () => {
    try {
      const info = await api.getSampleRepoPath();
      setRepoPath(info.sample_repo_path);
      handleInspect(info.sample_repo_path);
    } catch (err: any) {
      showToast('Failed to load sample repository path', 'error');
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
          <FolderGit2 className="w-6 h-6 text-emerald-400" />
          <span>Safe Repository Inspector</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Inspects authorized project directories for language stacks, build configs, Git working-tree status, and security hygiene.
        </p>
      </div>

      {/* Safety Notice */}
      <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>
            <strong>Read-Only Guarantee:</strong> Never scans system directories, modifies source code, or executes AI-suggested commands automatically.
          </span>
        </div>
        <span className="font-mono text-[10px] text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
          Path-Traversal Protected
        </span>
      </div>

      {/* Path Input Box */}
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="Enter absolute directory path (e.g. C:\workspace\my-project)..."
              className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition"
            />
          </div>
          <button
            onClick={handleUseSampleRepo}
            className="px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition shrink-0"
          >
            Use Bundled Sample Repo
          </button>
          <button
            onClick={() => handleInspect()}
            disabled={loading || !repoPath.trim()}
            className="inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30 transition shrink-0"
          >
            <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Inspecting...' : 'Inspect Repo'}</span>
          </button>
        </div>
      </div>

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          {/* Top Stack Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Languages Detected
              </span>
              <div className="flex flex-wrap gap-1.5">
                {result.languages_detected.length > 0 ? (
                  result.languages_detected.map((lang, i) => (
                    <span
                      key={i}
                      className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                    >
                      {lang}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500">None detected</span>
                )}
              </div>
            </div>

            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Frameworks & Tools
              </span>
              <div className="flex flex-wrap gap-1.5">
                {result.frameworks_detected.length > 0 ? (
                  result.frameworks_detected.map((fw, i) => (
                    <span
                      key={i}
                      className="text-xs font-mono px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30"
                    >
                      {fw}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500">None identified</span>
                )}
              </div>
            </div>

            <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Configuration Files
              </span>
              <div className="flex flex-wrap gap-1.5">
                {result.config_files_found.length > 0 ? (
                  result.config_files_found.map((cfg, i) => (
                    <span
                      key={i}
                      className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700"
                    >
                      {cfg}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500">None found</span>
                )}
              </div>
            </div>
          </div>

          {/* Git Status Card */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <GitBranch className="w-5 h-5 text-blue-400" />
                <span>Git Working Tree & History</span>
              </h3>
              <span
                className={`px-2.5 py-0.5 rounded text-xs font-mono font-semibold ${
                  result.git_status.is_clean
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}
              >
                {result.git_status.is_clean ? 'Clean Working Tree' : 'Uncommitted Changes Detected'}
              </span>
            </div>

            {result.git_status.is_git_repo ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-4 text-xs font-mono text-slate-300">
                  <span>Branch: <strong className="text-blue-400">{result.git_status.branch}</strong></span>
                </div>

                {/* Modified & untracked files */}
                {((result.git_status.modified_files && result.git_status.modified_files.length > 0) ||
                  (result.git_status.untracked_files && result.git_status.untracked_files.length > 0)) && (
                  <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2 text-xs font-mono">
                    {result.git_status.modified_files?.map((f, i) => (
                      <div key={i} className="flex items-center space-x-2 text-amber-400">
                        <span className="w-4 font-bold">M</span>
                        <span>{f}</span>
                      </div>
                    ))}
                    {result.git_status.untracked_files?.map((f, i) => (
                      <div key={i} className="flex items-center space-x-2 text-emerald-400">
                        <span className="w-4 font-bold">??</span>
                        <span>{f}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Recent Commits */}
                {result.git_status.recent_commits && result.git_status.recent_commits.length > 0 && (
                  <div>
                    <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider block mb-2">
                      Recent Commits
                    </span>
                    <div className="space-y-1.5">
                      {result.git_status.recent_commits.map((c, i) => (
                        <div
                          key={i}
                          className="flex items-center space-x-2 text-xs font-mono text-slate-300 p-2 rounded bg-slate-950 border border-slate-800/80"
                        >
                          <GitCommit className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                          <span>{c}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-xs text-slate-500">Not a Git repository.</div>
            )}
          </div>

          {/* Potential Issues & Security Hygiene */}
          {result.potential_issues.length > 0 && (
            <div className="p-6 rounded-xl border border-rose-500/30 bg-rose-950/10 space-y-4">
              <h3 className="text-base font-bold text-rose-300 flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-rose-400" />
                <span>Security Exposures & Issues Identified</span>
              </h3>
              <div className="space-y-2.5">
                {result.potential_issues.map((iss, i) => (
                  <div
                    key={i}
                    className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-start space-x-3 text-xs"
                  >
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono shrink-0 ${
                        iss.severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : iss.severity === 'HIGH'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}
                    >
                      {iss.severity}
                    </span>
                    <div>
                      <div className="font-semibold text-white">{iss.title}</div>
                      <div className="text-slate-400 mt-0.5">{iss.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Lightbulb className="w-5 h-5 text-amber-400" />
                <span>Recommendations for Repository Health</span>
              </h3>
              <div className="space-y-2">
                {result.recommendations.map((rec, i) => (
                  <div key={i} className="flex items-center space-x-2.5 text-xs text-slate-300">
                    <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{rec}</span>
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
