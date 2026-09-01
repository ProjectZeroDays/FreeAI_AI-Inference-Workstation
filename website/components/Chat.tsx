'use client';

import { useState, useEffect, useRef } from 'react';
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
        alert(`Thanks! We'll send your early-access invite to ${email}`);
        setEmail('');
        setSubmitted(false);
      }, 800);
    }
  };

  return (
    <>
      {/* Floating launcher button */}
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

      {/* Lead box panel */}
      {isOpen && (
        <div
          ref={panelRef}
          className="fixed bottom-24 right-6 z-50 w-full max-w-sm bg-white border border-slate-200 rounded-2xl shadow-2xl shadow-slate-900/20 overflow-hidden animate-slide-up"
          role="dialog"
          aria-label="Chat with FreeAI"
          style={{ fontFamily: "'Inter', system-ui, sans-serif" }}
        >
          {/* Lead box container */}
          <div className="lead-box" style={{ background: 'white' }}>
            {/* Header */}
            <header className="lead-head" style={{ padding: '16px 20px', borderBottom: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div className="lead-head-top" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span className="lead-orb" aria-hidden="true" style={{ width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1d4ed8' }}>
                    <svg width="17" height="15.88" viewBox="0 0 197 184" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '20px', height: '18.66px' }}>
                      <path fillRule="evenodd" clipRule="evenodd" d="M88.2715 10.0268L176 184L87.9999 162.759L0 184L88.2446 10.0268L88.2579 10L88.2715 10.0268Z" fill="currentColor"></path>
                      <path d="M164 25C164 25 165.821 41.9948 172.913 49.087C180.005 56.1792 197 58 197 58C197 58 180.005 59.8208 172.913 66.913C165.821 74.0052 164 91 164 91C164 91 162.179 74.0052 155.087 66.913C147.995 59.8208 131 58 131 58C131 58 147.995 56.1792 155.087 49.087C162.179 41.9948 164 25 164 25Z" fill="currentColor"></path>
                      <path d="M143 4C143 4 144.048 13.7849 148.132 17.8683C152.215 21.9517 162 23 162 23C162 23 152.215 24.0483 148.132 28.1317C144.048 32.2151 143 42 143 42C143 42 141.952 32.2151 137.868 28.1317C133.785 24.0483 124 23 124 23C124 23 133.785 21.9517 137.868 17.8683C141.952 13.7849 143 4 143 4Z" fill="currentColor"></path>
                      <path d="M178 0C178 0 178.662 6.17992 181.241 8.75891C183.82 11.3379 190 12 190 12C190 12 183.82 12.6621 181.241 15.2411C178.662 17.8201 178 24 178 24C178 24 177.338 17.8201 174.759 15.2411C172.18 12.6621 166 12 166 12C166 12 172.18 11.3379 174.759 8.75891C177.338 6.17992 178 0 178 0Z" fill="currentColor"></path>
                    </svg>
                  </span>
                  <div className="lead-id">
                    <h3 id="lead-title" className="lead-title" style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#0f172a', lineHeight: 1.2 }}>
                      FreeAI Intelligence
                    </h3>
                    <p className="lead-status" style={{ margin: '2px 0 0', fontSize: '12px', color: '#16a34a', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span style={{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', background: '#22c55e' }} />
                      Online
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  className="lead-close"
                  aria-label="Close"
                  onClick={() => setIsOpen(false)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', color: '#64748b', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'color 0.15s, background 0.15s' }}
                  onMouseEnter={e => { e.currentTarget.style.color = '#0f172a'; e.currentTarget.style.background = '#f1f5f9'; }}
                  onMouseLeave={e => { e.currentTarget.style.color = '#64748b'; e.currentTarget.style.background = 'none'; }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="m14.5 9.5l-5 5m0-5l5 5"></path>
                  </svg>
                </button>
              </div>
              {/* Tabs */}
              <div className="lead-tabs" role="tablist" aria-label="What do you need?" style={{ display: 'flex', gap: '4px' }}>
                <button
                  type="button"
                  role="tab"
                  className={`lead-tab ${activeTab === 'early-access' ? 'lead-tab--active' : ''}`}
                  aria-selected={activeTab === 'early-access'}
                  onClick={() => setActiveTab('early-access')}
                  style={{
                    flex: 1,
                    padding: '8px 12px',
                    fontSize: '13px',
                    fontWeight: activeTab === 'early-access' ? 600 : 500,
                    color: activeTab === 'early-access' ? '#1d4ed8' : '#64748b',
                    background: activeTab === 'early-access' ? '#eff6ff' : 'transparent',
                    border: 'none',
                    borderRadius: activeTab === 'early-access' ? '8px 8px 0 0' : '8px',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                >
                  Early access
                </button>
                <button
                  type="button"
                  role="tab"
                  className={`lead-tab ${activeTab === 'specialist' ? 'lead-tab--active' : ''}`}
                  aria-selected={activeTab === 'specialist'}
                  onClick={() => setActiveTab('specialist')}
                  style={{
                    flex: 1,
                    padding: '8px 12px',
                    fontSize: '13px',
                    fontWeight: activeTab === 'specialist' ? 600 : 500,
                    color: activeTab === 'specialist' ? '#1d4ed8' : '#64748b',
                    background: activeTab === 'specialist' ? '#eff6ff' : 'transparent',
                    border: 'none',
                    borderRadius: activeTab === 'specialist' ? '8px 8px 0 0' : '8px',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                >
                  Talk to a specialist
                </button>
              </div>
            </header>

            {/* Chat content */}
            <div className="chat" aria-live="polite" style={{ padding: '16px 20px', minHeight: '160px', maxHeight: '240px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {activeTab === 'early-access' ? (
                <>
                  {/* Bot message 1 */}
                  <div className="msg msg--bot">
                    <span className="msg-orb" aria-hidden="true" style={{ flexShrink: 0, width: '20px', height: '18px', color: '#1d4ed8' }}>
                      <svg width="12" height="11.86" viewBox="0 0 176 174" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fillRule="evenodd" clipRule="evenodd" d="M88.2715 0.0267731L176 174L87.9999 152.759L0 174L88.2446 0.0267731L88.2579 0L88.2715 0.0267731Z" fill="currentColor"></path>
                      </svg>
                    </span>
                    <p className="msg-bubble" style={{ margin: 0, padding: '10px 14px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '13px', color: '#334155', lineHeight: 1.5 }}>
                      Hi — let&apos;s get you into this summer&apos;s Europe rollout. Three taps and your email, about 30 seconds.
                    </p>
                  </div>
                  {/* Bot message 2 */}
                  <div className="msg msg--bot">
                    <span className="msg-orb" aria-hidden="true" style={{ flexShrink: 0, width: '20px', height: '18px', color: '#1d4ed8' }}>
                      <svg width="12" height="11.86" viewBox="0 0 176 174" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fillRule="evenodd" clipRule="evenodd" d="M88.2715 0.0267731L176 174L87.9999 152.759L0 174L88.2446 0.0267731L88.2579 0L88.2715 0.0267731Z" fill="currentColor"></path>
                      </svg>
                    </span>
                    <p className="msg-bubble" style={{ margin: 0, padding: '10px 14px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '13px', color: '#334155', lineHeight: 1.5 }}>
                      First things first — where should we send your early-access invite?
                    </p>
                  </div>
                </>
              ) : (
                <div className="msg msg--bot">
                  <span className="msg-orb" aria-hidden="true" style={{ flexShrink: 0, width: '20px', height: '18px', color: '#1d4ed8' }}>
                    <svg width="12" height="11.86" viewBox="0 0 176 174" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path fillRule="evenodd" clipRule="evenodd" d="M88.2715 0.0267731L176 174L87.9999 152.759L0 174L88.2446 0.0267731L88.2579 0L88.2715 0.0267731Z" fill="currentColor"></path>
                    </svg>
                  </span>
                  <p className="msg-bubble" style={{ margin: 0, padding: '10px 14px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '13px', color: '#334155', lineHeight: 1.5 }}>
                    I&apos;d be happy to connect you with a specialist. What&apos;s your name and company?
                  </p>
                </div>
              )}
            </div>

            {/* Input tray */}
            <div className="tray" style={{ padding: '12px 20px 16px', borderTop: '1px solid #e2e8f0', background: '#f8fafc' }}>
              {!submitted ? (
                <form className="composer composer--compact" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      data-v-1e24ae2f=""
                      type={activeTab === 'early-access' ? 'email' : 'text'}
                      required
                      autoComplete="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder={activeTab === 'early-access' ? 'you@company.com' : 'Your name & company'}
                      aria-label="Work email"
                      style={{
                        flex: 1,
                        padding: '10px 14px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#334155',
                        background: 'white',
                        outline: 'none',
                        transition: 'border-color 0.15s',
                      }}
                      onFocus={e => e.currentTarget.style.borderColor = '#93c5fd'}
                      onBlur={e => e.currentTarget.style.borderColor = '#e2e8f0'}
                    />
                    <button
                      type="submit"
                      className="composer-send"
                      aria-label="Send"
                      style={{
                        width: '40px',
                        height: '40px',
                        background: '#1d4ed8',
                        border: 'none',
                        borderRadius: '8px',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'background 0.15s',
                        flexShrink: 0,
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = '#1e40af'}
                      onMouseLeave={e => e.currentTarget.style.background = '#1d4ed8'}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 19V5M5 12l7-7 7 7"></path>
                      </svg>
                    </button>
                  </div>
                  <p className="composer-note" style={{ margin: 0, fontSize: '11px', color: '#94a3b8', lineHeight: 1.4 }}>
                    {activeTab === 'early-access'
                      ? 'Only to contact you about your invite'
                      : 'A specialist will reach out within 24 hours'}
                  </p>
                </form>
              ) : (
                <div style={{ padding: '12px 0', textAlign: 'center' }}>
                  <p style={{ margin: 0, fontSize: '14px', color: '#16a34a', fontWeight: 500 }}>
                    ✓ Thanks! We&apos;ll be in touch shortly.
                  </p>
                </div>
              )}
            </div>

            {/* Fine print */}
            <p className="lead-fine" style={{ padding: '10px 20px 14px', fontSize: '11px', color: '#94a3b8', lineHeight: 1.5, display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: '1px' }}>
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                <path d="m9 12 2 2 4-4"></path>
              </svg>
              <span>
                FreeAI will use your details only to answer this request.{' '}
                <a href="/legal/privacy" className="lead-privacy" target="_blank" rel="noopener noreferrer" style={{ color: '#1d4ed8', textDecoration: 'underline' }}>
                  Privacy Policy
                </a>
              </span>
            </p>
          </div>
        </div>
      )}
    </>
  );
}
