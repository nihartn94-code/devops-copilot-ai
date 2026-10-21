import React, { useEffect, useState } from 'react';
import {
  Terminal,
  FolderGit2,
  CheckCircle2,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  Server,
  Layers,
  BookOpen,
  RefreshCw,
  Clock
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardStats, HealthStatus } from '../types/api';
import { NavTab } from '../components/Sidebar';

interface DashboardViewProps {
  onNavigate: (tab: NavTab) => void;
  health: HealthStatus | null;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigate, health }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const metricCards = [
    {
      title: 'Total Analyses',
      value: stats?.total_analyses ?? 0,
      icon: Layers,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20'
    },
    {
      title: 'Build Failures Parsed',
      value: stats?.total_build_logs ?? 0,
      icon: Terminal,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20'
    },
    {
      title: 'Test Suites Diagnosed',
      value: stats?.total_tests ?? 0,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20'
    },
    {
      title: 'Secrets Auto-Redacted',
      value: stats?.total_secrets_redacted ?? 0,
      icon: ShieldCheck,
      color: 'text-rose-400',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/20'
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border border-slate-800 p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              <span>Amazon Bedrock & Model Context Protocol (Streamable HTTP)</span>
            </div>
            <h2 className="text-3xl font-extrabold text-white tracking-tight">
              DevOps Copilot AI Command Center
            </h2>
            <p className="text-slate-400 text-sm leading-relaxed">
              Diagnose cryptic CI/CD build failures, inspect local git repositories safely, analyze unit and integration test outputs,
              and receive actionable debugging recommendations with zero accidental secret leaks.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => onNavigate('build-logs')}
              className="inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold shadow-lg shadow-blue-600/30 transition duration-150"
            >
              <Terminal className="w-4 h-4" />
              <span>Analyze Build Log</span>
            </button>
            <button
              onClick={loadStats}
              className="inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700 transition duration-150"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh Stats</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {metricCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className={`p-5 rounded-xl border bg-slate-900/60 backdrop-blur-sm ${card.borderColor} flex items-center space-x-4 shadow-sm hover:border-slate-700 transition`}
            >
              <div className={`p-3 rounded-lg ${card.bgColor} ${card.color}`}>
                <Icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-medium text-slate-400">{card.title}</p>
                <p className="text-2xl font-bold text-white mt-1">
                  {loading ? '...' : card.value}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Launch Cards */}
      <div>
        <h3 className="text-lg font-bold text-white mb-4">Quick Developer Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div
            onClick={() => onNavigate('build-logs')}
            className="group cursor-pointer p-6 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-800/50 hover:border-blue-500/40 transition-all duration-200 shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-4 group-hover:scale-105 transition">
              <Terminal className="w-5 h-5" />
            </div>
            <h4 className="font-semibold text-white text-base group-hover:text-blue-400 transition">
              Build-Log Analyzer
            </h4>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Paste or upload Docker, npm, Maven, or Python logs. Automatically isolates errors, redacts secrets, and outlines root causes.
            </p>
            <div className="mt-4 flex items-center text-xs text-blue-400 font-semibold group-hover:translate-x-1 transition duration-150">
              <span>Start analysis</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          <div
            onClick={() => onNavigate('repo-inspector')}
            className="group cursor-pointer p-6 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-800/50 hover:border-emerald-500/40 transition-all duration-200 shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4 group-hover:scale-105 transition">
              <FolderGit2 className="w-5 h-5" />
            </div>
            <h4 className="font-semibold text-white text-base group-hover:text-emerald-400 transition">
              Safe Repository Inspector
            </h4>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Read-only inspection of authorized codebases. Detects frameworks, uncommitted git diffs, and flags security exposures.
            </p>
            <div className="mt-4 flex items-center text-xs text-emerald-400 font-semibold group-hover:translate-x-1 transition duration-150">
              <span>Inspect repository</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>

          <div
            onClick={() => onNavigate('test-analyzer')}
            className="group cursor-pointer p-6 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-800/50 hover:border-purple-500/40 transition-all duration-200 shadow-sm"
          >
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mb-4 group-hover:scale-105 transition">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <h4 className="font-semibold text-white text-base group-hover:text-purple-400 transition">
              Test-Result Analyzer
            </h4>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Ingest pytest or Jest terminal outputs. Isolates failed assertions, explains root causes, and proposes non-destructive code patches.
            </p>
            <div className="mt-4 flex items-center text-xs text-purple-400 font-semibold group-hover:translate-x-1 transition duration-150">
              <span>Analyze tests</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </div>
        </div>
      </div>

      {/* Architecture & Recent Activity Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* MCP & Cloud Telemetry */}
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
          <div className="flex items-center space-x-2 text-white font-semibold">
            <Server className="w-4 h-4 text-cyan-400" />
            <span>Architecture & MCP Status</span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
              <div className="text-slate-400 font-medium">Model Context Protocol Transport</div>
              <div className="text-cyan-400 font-mono mt-1">Streamable HTTP (2025-11-25)</div>
              <div className="text-slate-400 mt-0.5">Endpoint: http://127.0.0.1:8001/mcp</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
              <div className="text-slate-400 font-medium">Amazon Bedrock Converse Status</div>
              <div className="text-emerald-400 font-mono mt-1">
                {health?.aws_credentials_configured ? 'Active (Claude 3.5 Sonnet)' : 'Demo Fallback Mode'}
              </div>
              <div className="text-slate-400 mt-0.5">
                {health?.aws_credentials_configured
                  ? 'Authenticated via AWS SDK'
                  : 'Deterministic offline rule engine active'}
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80">
              <div className="text-slate-400 font-medium">Local SQLite Persistence</div>
              <div className="text-slate-300 font-mono mt-1">devops_copilot.db (Async)</div>
            </div>
          </div>
        </div>

        {/* Recent Analysis Feed */}
        <div className="lg:col-span-2 p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-white font-semibold">
              <Clock className="w-4 h-4 text-blue-400" />
              <span>Recent Analyses</span>
            </div>
            <button
              onClick={() => onNavigate('history')}
              className="text-xs text-blue-400 hover:text-blue-300 font-medium"
            >
              View all history →
            </button>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-500 text-sm">Loading activity feed...</div>
          ) : !stats?.recent_analyses || stats.recent_analyses.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-sm border border-dashed border-slate-800 rounded-lg">
              No analyses recorded yet. Click one of the quick actions above to begin!
            </div>
          ) : (
            <div className="space-y-2.5">
              {stats.recent_analyses.map((item) => (
                <div
                  key={item.id}
                  onClick={() => onNavigate('history')}
                  className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 flex items-center justify-between cursor-pointer transition"
                >
                  <div className="space-y-1 min-w-0 pr-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold text-white truncate">{item.title}</span>
                      <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                        {item.analysis_type.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 truncate">{item.summary}</p>
                  </div>
                  <span className="text-[11px] text-slate-400 shrink-0 font-mono">
                    {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
