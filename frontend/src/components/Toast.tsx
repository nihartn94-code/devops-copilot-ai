import React from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

interface ToastContainerProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col space-y-2 pointer-events-none">
      {toasts.map((toast) => {
        const isSuccess = toast.type === 'success';
        const isError = toast.type === 'error';
        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-center space-x-3 px-4 py-3 rounded-lg shadow-xl border backdrop-blur-md transition-all duration-200 ${
              isSuccess
                ? 'bg-slate-900/90 text-emerald-400 border-emerald-500/30'
                : isError
                ? 'bg-slate-900/90 text-rose-400 border-rose-500/30'
                : 'bg-slate-900/90 text-blue-400 border-blue-500/30'
            }`}
          >
            {isSuccess && <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />}
            {isError && <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />}
            {!isSuccess && !isError && <Info className="w-5 h-5 text-blue-400 shrink-0" />}
            <span className="text-sm font-medium text-slate-200">{toast.message}</span>
            <button
              onClick={() => onDismiss(toast.id)}
              className="text-slate-400 hover:text-white ml-2 p-1 rounded"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
