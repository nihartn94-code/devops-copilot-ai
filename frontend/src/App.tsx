import React, { useEffect, useState } from 'react';
import { NavTab, Sidebar } from './components/Sidebar';
import { ToastContainer, ToastMessage } from './components/Toast';
import { DashboardView } from './views/DashboardView';
import { BuildLogView } from './views/BuildLogView';
import { RepoInspectorView } from './views/RepoInspectorView';
import { TestAnalyzerView } from './views/TestAnalyzerView';
import { DocAssistantView } from './views/DocAssistantView';
import { ChatAssistantView } from './views/ChatAssistantView';
import { HistoryView } from './views/HistoryView';
import { api } from './services/api';
import { HealthStatus } from './types/api';

export function App() {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [chatContext, setChatContext] = useState<{ analysisId?: string; prompt?: string }>({});

  useEffect(() => {
    api.getHealth()
      .then(setHealth)
      .catch((err) => {
        console.warn('Backend health check error:', err);
      });
  }, []);

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleDismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleStartChatWithContext = (analysisId: string, initialPrompt: string) => {
    setChatContext({ analysisId, prompt: initialPrompt });
    setCurrentTab('chat');
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Collapsible/Fixed Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={(tab) => {
          setCurrentTab(tab);
        }}
        health={health}
      />

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto bg-slate-950">
        {currentTab === 'dashboard' && (
          <DashboardView onNavigate={setCurrentTab} health={health} />
        )}
        {currentTab === 'build-logs' && (
          <BuildLogView
            onStartChatWithContext={handleStartChatWithContext}
            showToast={showToast}
          />
        )}
        {currentTab === 'repo-inspector' && (
          <RepoInspectorView showToast={showToast} />
        )}
        {currentTab === 'test-analyzer' && (
          <TestAnalyzerView showToast={showToast} />
        )}
        {currentTab === 'docs' && (
          <DocAssistantView showToast={showToast} />
        )}
        {currentTab === 'chat' && (
          <ChatAssistantView
            initialAnalysisId={chatContext.analysisId}
            initialPrompt={chatContext.prompt}
            health={health}
            showToast={showToast}
          />
        )}
        {currentTab === 'history' && (
          <HistoryView showToast={showToast} />
        )}
      </main>

      {/* Toast Notification Container */}
      <ToastContainer toasts={toasts} onDismiss={handleDismissToast} />
    </div>
  );
}

export default App;
