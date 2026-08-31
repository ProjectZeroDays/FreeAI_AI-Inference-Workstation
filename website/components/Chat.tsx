'use client';

import { useState, useRef, useEffect } from 'react';
import { X, Send } from 'lucide-react';

export default function Chat() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('early-access');
  const [email, setEmail] = useState('');
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      alert(`Thanks! We'll send your early-access invite to ${email}`);
      setEmail('');
    }
  };

  return (
    <>
      {/* Floating launcher button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-12 h-12 rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow-lg flex items-center justify-center transition-all hover:scale-105"
        aria-label="Chat with FreeAI"
        title="Chat with FreeAI"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div
          ref={panelRef}
          className="fixed bottom-20 right-6 z-50 w-full max-w-sm bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden animate-slide-up"
          role="dialog"
          aria-label="Chat with FreeAI"
        >
          {/* Header */}
          <div className="px-4 py-3 border-b border-slate-100 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-xs">F</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-slate-900 text-sm">FreeAI Intelligence</div>
              <div className="flex items-center gap-1.5 text-xs text-green-600">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
                Online
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-7 h-7 rounded-lg border border-slate-200 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:border-slate-300 transition-colors"
              aria-label="Close"
            >
              <X size={14} />
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-slate-100">
            <button
              className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors ${
                activeTab === 'early-access'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
              onClick={() => setActiveTab('early-access')}
            >
              Early access
            </button>
            <button
              className={`flex-1 px-4 py-2.5 text-sm font-medium transition-colors ${
                activeTab === 'specialist'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
              onClick={() => setActiveTab('specialist')}
            >
              Talk to a specialist
            </button>
          </div>

          {/* Chat content */}
          <div className="px-4 py-4 min-h-[180px] max-h-[320px] overflow-y-auto">
            {activeTab === 'early-access' ? (
              <div className="space-y-3">
                <div className="flex gap-2.5">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xs font-bold">F</span>
                  </div>
                  <div className="bg-slate-100 rounded-xl rounded-tl-none px-3.5 py-2.5 text-sm text-slate-700 max-w-[85%]">
                    Hi — let&apos;s get you into this summer&apos;s rollout. Three taps and your email, about 30 seconds.
                  </div>
                </div>
                <div className="flex gap-2.5">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xs font-bold">F</span>
                  </div>
                  <div className="bg-slate-100 rounded-xl rounded-tl-none px-3.5 py-2.5 text-sm text-slate-700 max-w-[85%]">
                    First things first — where should we send your early-access invite?
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex gap-2.5">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xs font-bold">F</span>
                  </div>
                  <div className="bg-slate-100 rounded-xl rounded-tl-none px-3.5 py-2.5 text-sm text-slate-700 max-w-[85%]">
                    I&apos;d be happy to connect you with a specialist. What&apos;s your name and company?
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="px-4 py-3 border-t border-slate-100 bg-slate-50">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type={activeTab === 'early-access' ? 'email' : 'text'}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder={activeTab === 'early-access' ? 'you@company.com' : 'Your name & company'}
                className="flex-1 px-3.5 py-2 bg-white border border-slate-200 rounded-xl text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-blue-400"
                aria-label={activeTab === 'early-access' ? 'Work email' : 'Name and company'}
              />
              <button
                type="submit"
                className="w-9 h-9 bg-blue-600 hover:bg-blue-700 rounded-xl flex items-center justify-center text-white transition-colors"
                aria-label="Send"
              >
                <Send size={16} />
              </button>
            </form>
            <p className="text-[11px] text-slate-400 mt-2">
              {activeTab === 'early-access'
                ? 'Only to contact you about your invite'
                : 'A specialist will reach out within 24 hours'}
            </p>
          </div>

          {/* Privacy */}
          <div className="px-4 py-2.5 border-t border-slate-100 flex items-center gap-1.5">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-slate-400 flex-shrink-0">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            <span className="text-[11px] text-slate-400">
              FreeAI will use your details only to answer this request.{' '}
              <a href="/legal/privacy" className="text-blue-600 hover:underline">Privacy Policy</a>
            </span>
          </div>
        </div>
      )}
    </>
  );
}
