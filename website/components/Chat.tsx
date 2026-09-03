'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { X } from 'lucide-react';

export default function Chat() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('early-access');
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
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
      setSubmitted(true);
      setTimeout(() => {
        setEmail('');
        setSubmitted(false);
      }, 2000);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white shadow-xl shadow-blue-500/30 flex items-center justify-center transition-all hover:scale-110"
        aria-label="Chat with FreeAI"
        title="Chat with FreeAI"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </button>

      {isOpen && (
        <div
          ref={panelRef}
          className="fixed bottom-24 right-6 z-50 w-full max-w-sm bg-slate-900 border border-white/10 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden"
          role="dialog"
          aria-label="Chat with FreeAI"
        >
          <header className="px-5 py-4 border-b border-white/10">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">F</span>
                </div>
                <div>
                  <h3 className="text-white font-semibold text-sm">FreeAI Intelligence</h3>
                  <p className="text-green-400 text-xs flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                    Online
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                aria-label="Close chat"
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X size={18} />
              </button>
            </div>
            <div className="flex gap-1 bg-slate-800 rounded-lg p-1" role="tablist">
              {(['early-access', 'specialist'] as const).map((tab) => (
                <button
                  key={tab}
                  role="tab"
                  aria-selected={activeTab === tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    activeTab === tab
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab === 'early-access' ? 'Early access' : 'Talk to specialist'}
                </button>
              ))}
            </div>
          </header>

          <div className="px-5 py-4 min-h-[140px] max-h-[200px] overflow-y-auto space-y-3" aria-live="polite">
            {activeTab === 'early-access' ? (
              <>
                <div className="flex gap-2">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xs font-bold">F</span>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-300 max-w-xs">
                    Want early access to the FreeAI inference stack? Drop your email and we&apos;ll notify you.
                  </div>
                </div>
              </>
            ) : (
              <div className="flex gap-2">
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-xs font-bold">F</span>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-300 max-w-xs">
                  I&apos;d be happy to connect you with a specialist. What&apos;s your name and company?
                </div>
              </div>
            )}
          </div>

          <div className="px-5 py-4 border-t border-white/10 bg-black/20">
            {!submitted ? (
              <form onSubmit={handleSubmit} className="space-y-2">
                <div className="flex gap-2">
                  <input
                    type={activeTab === 'early-access' ? 'email' : 'text'}
                    required
                    autoComplete={activeTab === 'early-access' ? 'email' : 'off'}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={activeTab === 'early-access' ? 'you@company.com' : 'Your name & company'}
                    aria-label={activeTab === 'early-access' ? 'Work email' : 'Name and company'}
                    className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                  />
                  <button
                    type="submit"
                    aria-label="Send"
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors flex-shrink-0"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 19V5M5 12l7-7 7 7"></path>
                    </svg>
                  </button>
                </div>
                <p className="text-xs text-slate-500">
                  {activeTab === 'early-access'
                    ? 'Only to contact you about your invite'
                    : 'A specialist will reach out within 24 hours'}
                </p>
              </form>
            ) : (
              <p className="text-sm text-green-400 text-center py-2">
                ✓ Thanks! We&apos;ll be in touch shortly.
              </p>
            )}
          </div>

          <div className="px-5 py-3 border-t border-white/5">
            <p className="text-xs text-slate-500 leading-relaxed">
              FreeAI will use your details only to answer this request.{' '}
              <Link href="/legal/privacy" className="text-blue-400 hover:text-blue-300 underline">
                Privacy Policy
              </Link>
            </p>
          </div>
        </div>
      )}
    </>
  );
}
