import Link from 'next/link'
import { Github, Twitter, ArrowRight } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-[#060a18] border-t border-white/10 mt-0">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <span className="font-bold text-lg text-white">FreeAI</span>
            </div>
            <p className="text-gray-400 text-sm max-w-md mb-4">
              Unified AI inference workstation. Manage, secure, and automate every model — automatically.
            </p>
            <Link
              href="/deploy"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Get FreeAI <ArrowRight size={16} />
            </Link>
            <div className="flex gap-2 mt-4">
              {['SOC 2', 'ISO 27001', 'NIST 800-53', 'CMMC L2'].map((badge) => (
                <span key={badge} className="px-2 py-1 rounded bg-white/5 text-xs text-gray-500 border border-white/5">
                  {badge}
                </span>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-white mb-4">On This Page</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/" className="hover:text-white transition-colors">Why now</Link></li>
              <li><Link href="/features" className="hover:text-white transition-colors">Capabilities</Link></li>
              <li><Link href="/agents" className="hover:text-white transition-colors">Agents</Link></li>
              <li><Link href="/deploy" className="hover:text-white transition-colors">How it works</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-white mb-4">Community</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
              <li><Link href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/discussions" className="hover:text-white transition-colors">Forum</Link></li>
              <li><Link href="/docs" className="hover:text-white transition-colors">About</Link></li>
              <li><Link href="/legal/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-white mb-4">Legal</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/legal/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
              <li><Link href="/legal/terms" className="hover:text-white transition-colors">Terms</Link></li>
              <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-white/10 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-500 text-sm">
            ©2026 FreeAI — Unified AI Workstation — MIT License
          </p>
          <p className="text-gray-500 text-sm">
            AI is not just a chatbot — it's an operational layer.
          </p>
        </div>
      </div>
    </footer>
  )
}
