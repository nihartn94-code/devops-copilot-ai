import React, { useEffect, useRef, useState } from 'react';
import {
  Bot,
  User,
  Send,
  Sparkles,
  RotateCcw,
  ShieldCheck,
  Link2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { ChatMessage, HealthStatus } from '../types/api';

interface ChatAssistantViewProps {
  initialAnalysisId?: string;
  initialPrompt?: string;
  health: HealthStatus | null;
  showToast: (msg: string, type?: 'success' | 'error' | 'info') => void;
}

export const ChatAssistantView: React.FC<ChatAssistantViewProps> = ({
  initialAnalysisId,
  initialPrompt,
  health,
  showToast
}) => {
  const [sessionId, setSessionId] = useState<string>(() => 'session-' + Math.random().toString(36).substring(2, 9));
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>(initialPrompt || '');
  const [loading, setLoading] = useState<boolean>(false);
  const [analysisId, setAnalysisId] = useState<string | undefined>(initialAnalysisId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userText = input;
    setInput('');
    setLoading(true);

    // Optimistic user message
    const tempUserMsg: ChatMessage = {
      id: 'temp-' + Date.now(),
      session_id: sessionId,
      analysis_id: analysisId,
      role: 'user',
      content: userText,
      provider: 'user',
      model_id: 'input',
      is_fallback: false,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const resp = await api.sendChatMessage(sessionId, userText, analysisId);
      setMessages((prev) => [...prev.filter((m) => m.id !== tempUserMsg.id), tempUserMsg, resp]);
    } catch (err: any) {
      showToast(err.message || 'Failed to send message', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleResetSession = () => {
    const newSession = 'session-' + Math.random().toString(36).substring(2, 9);
    setSessionId(newSession);
    setMessages([]);
    setAnalysisId(undefined);
    showToast('New debugging conversation started', 'info');
  };

  return (
    <div className="p-8 max-w-5xl mx-auto h-[calc(100vh-2rem)] flex flex-col space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 shrink-0">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
            <Bot className="w-6 h-6 text-blue-400" />
            <span>AI Debugging Assistant</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Interactive multi-turn technical troubleshooting with secret redaction.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {analysisId && (
            <span className="inline-flex items-center text-xs px-2.5 py-1 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
              <Link2 className="w-3.5 h-3.5 mr-1" />
              <span>Linked to: {analysisId}</span>
            </span>
          )}
          <button
            onClick={handleResetSession}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Chat</span>
          </button>
        </div>
      </div>

      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 rounded-xl bg-slate-900/40 border border-slate-800">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500 space-y-3">
            <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-slate-400">
              <Sparkles className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="font-semibold text-white text-base">How can I assist your pipeline today?</h3>
            <p className="text-xs max-w-md text-slate-400 leading-relaxed">
              Ask follow-up questions about compiler errors, Docker multi-stage configurations, unit test assertion failures, or Bedrock architecture.
            </p>
          </div>
        ) : (
          messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id}
                className={`flex items-start space-x-3 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`max-w-2xl rounded-xl p-4 text-xs leading-relaxed space-y-2 ${
                    isUser
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-tl-none shadow-sm'
                  }`}
                >
                  <div className="whitespace-pre-wrap font-sans">{msg.content}</div>
                  {!isUser && (
                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                      <span>{msg.is_fallback ? 'Deterministic Fallback' : `Bedrock (${msg.model_id})`}</span>
                      <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  )}
                </div>
                {isUser && (
                  <div className="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })
        )}
        {loading && (
          <div className="flex items-center space-x-3 text-slate-400 text-xs p-3">
            <Bot className="w-5 h-5 text-blue-400 animate-spin" />
            <span>DevOps Copilot is reasoning...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Field */}
      <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center space-x-3 shrink-0">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a debugging question or request fix clarification..."
          className="flex-1 bg-transparent px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="inline-flex items-center justify-center p-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white shadow transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
