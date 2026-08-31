import Link from 'next/link'
import { Github, ArrowRight } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-slate-900 border-t border-slate-800 mt-0">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Column 1: Brand + CTA */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <span className="font-bold text-lg text-white">FreeAI</span>
            </div>
            <p className="text-slate-400 text-sm max-w-xs mb-4">
              Unified AI inference workstation. Manage, secure, and automate every model — automatically.
            </p>
            <Link
              href="/deploy"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Get FreeAI <ArrowRight size={16} />
            </Link>
            <div className="flex flex-wrap gap-2 mt-4">
              {['SOC 2', 'ISO 27001', 'NIST 800-53', 'CMMC L2'].map((badge) => (
                <span key={badge} className="px-2 py-1 rounded bg-slate-800 text-xs text-slate-500 border border-slate-700">
                  {badge}
                </span>
              ))}
            </div>
          </div>

          {/* Column 2: Product */}
          <div>
            <h3 className="font-semibold text-white mb-4">Product</h3>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><Link href="/#ask-agents" className="hover:text-white transition-colors">Ask Agents</Link></li>
              <li><Link href="/#artifacts" className="hover:text-white transition-colors">Artifacts</Link></li>
              <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
              <li><Link href="/providers" className="hover:text-white transition-colors">Integrations</Link></li>
              <li><Link href="/deploy" className="hover:text-white transition-colors">Deploy</Link></li>
              <li><Link href="/iso" className="hover:text-white transition-colors">Live ISO</Link></li>
            </ul>
          </div>

          {/* Column 3: Resources */}
          <div>
            <h3 className="font-semibold text-white mb-4">Resources</h3>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><Link href="/deploy" className="hover:text-white transition-colors">Deploy Guide</Link></li>
              <li>
                <a href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation"
                   className="hover:text-white transition-colors flex items-center gap-1"
                   target="_blank" rel="noopener noreferrer">
                  <Github size={14} /> GitHub
                </a>
              </li>
              <li>
                <a href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/discussions"
                   className="hover:text-white transition-colors"
                   target="_blank" rel="noopener noreferrer">Forum</a>
              </li>
              <li><Link href="/docs" className="hover:text-white transition-colors">About</Link></li>
              <li><Link href="/legal/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>

          {/* Column 4: Legal */}
          <div>
            <h3 className="font-semibold text-white mb-4">Legal</h3>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><Link href="/legal/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
              <li><Link href="/legal/terms" className="hover:text-white transition-colors">Terms</Link></li>
              <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
              <li><Link href="/security#compliance" className="hover:text-white transition-colors">Compliance</Link></li>
              <li><Link href="/legal/careers" className="hover:text-white transition-colors">Careers</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-slate-500 text-sm">
            ©2026 FreeAI — Unified AI Workstation — GPL-3.0 License
          </p>
          <p className="text-slate-500 text-sm">
            AI is not just a chatbot — it's an operational layer.
          </p>
        </div>
      </div>
    </footer>
  )
}
