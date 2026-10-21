import React from 'react';
import {
  LayoutDashboard,
  Terminal,
  FolderGit2,
  CheckCircle2,
  BookOpen,
  Bot,
  History,
  Radio,
  ExternalLink,
  ShieldAlert
} from 'lucide-react';
import { HealthStatus } from '../types/api';

export type NavTab = 'dashboard' | 'build-logs' | 'repo-inspector' | 'test-analyzer' | 'docs' | 'chat' | 'history';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  health: HealthStatus | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, health }) => {
  const navItems = [
    { id: 'dashboard' as NavTab, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'build-logs' as NavTab, label: 'Build-Log Analyzer', icon: Terminal },
    { id: 'repo-inspector' as NavTab, label: 'Repo Inspector', icon: FolderGit2 },
    { id: 'test-analyzer' as NavTab, label: 'Test Analyzer', icon: CheckCircle2 },
    { id: 'docs' as NavTab, label: 'Doc Assistant', icon: BookOpen },
    { id: 'chat' as NavTab, label: 'AI Debugging Chat', icon: Bot },
    { id: 'history' as NavTab, label: 'History & Reports', icon: History },
  ];

  const isBedrockActive = health?.aws_credentials_configured && health?.bedrock_mode !== 'force_demo';

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white text-base tracking-tight leading-tight">DevOps Copilot</h1>
            <span className="text-xs font-mono text-cyan-400 font-semibold tracking-wide">ALEXA+ MCP READY</span>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 text-left ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Provider Status & Integration Badges */}
      <div className="p-4 border-t border-slate-800 space-y-3 bg-slate-950/60">
        {/* Bedrock status badge */}
        <div className="p-2.5 rounded-lg border border-slate-800/80 bg-slate-900/60">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-slate-400 font-medium">AI Provider</span>
            <span
              className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                isBedrockActive
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full mr-1 ${isBedrockActive ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              {isBedrockActive ? 'Bedrock Active' : 'Demo Fallback'}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 truncate font-mono">
            {isBedrockActive ? health?.bedrock_model_id : 'Deterministic Rule Engine'}
          </p>
        </div>

        {/* MCP Streamable HTTP status */}
        <div className="p-2.5 rounded-lg border border-slate-800/80 bg-slate-900/60">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-slate-400 font-medium">MCP Server</span>
            <span className="inline-flex items-center text-[10px] font-semibold text-cyan-400 bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-800/40">
              <Radio className="w-2.5 h-2.5 mr-1 text-cyan-400 animate-pulse" />
              Streamable HTTP
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-mono truncate">Port 8001 (/mcp)</p>
        </div>
      </div>
    </aside>
  );
};
