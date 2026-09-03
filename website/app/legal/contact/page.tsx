import Link from 'next/link'
import { ArrowLeft, Mail, Github } from 'lucide-react'

export default function LegalContact() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <h1 className="text-4xl font-bold text-white mb-4">Contact <span className="gradient-text">Us</span></h1>
        <p className="text-slate-400 text-lg mb-10">
          Have questions about FreeAI? We&apos;d love to hear from you.
        </p>

        <div className="space-y-6">
          <div className="page-card">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-blue-500/15 flex items-center justify-center text-blue-400">
                <Mail size={22} />
              </div>
              <div>
                <h3 className="text-white font-semibold">Email</h3>
                <a href="mailto:contact@projectzerodays.com" className="text-blue-400 hover:text-blue-300 text-sm">
                  contact@projectzerodays.com
                </a>
              </div>
            </div>
          </div>

          <div className="page-card">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-slate-700 flex items-center justify-center text-slate-300">
                <Github size={22} />
              </div>
              <div>
                <h3 className="text-white font-semibold">GitHub</h3>
                <p className="text-slate-400 text-sm">Open an issue or start a discussion</p>
                <a
                  href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/discussions"
                  target="_blank" rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 text-sm inline-flex items-center gap-1 mt-1"
                >
                  github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/discussions
                </a>
              </div>
            </div>
          </div>

          <div className="page-card">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-purple-500/15 flex items-center justify-center text-purple-400">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                  <circle cx="12" cy="10" r="3"></circle>
                </svg>
              </div>
              <div>
                <h3 className="text-white font-semibold">Community</h3>
                <p className="text-slate-400 text-sm">Join the discussion on our community channels</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 p-6 rounded-xl bg-blue-500/10 border border-blue-500/20">
          <h3 className="text-white font-semibold mb-2">Enterprise & Partnerships</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            For enterprise support inquiries, partnerships, or custom integrations, please email us directly.
          </p>
          <a href="mailto:enterprise@projectzerodays.com" className="text-blue-400 hover:text-blue-300 text-sm inline-flex items-center gap-1 mt-3">
            enterprise@projectzerodays.com <ArrowLeft className="rotate-180" size={14} />
          </a>
        </div>
      </div>
    </div>
  )
}
