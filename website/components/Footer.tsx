import Link from 'next/link'
import { Github, Twitter } from 'lucide-react'

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
            <p className="text-gray-400 text-sm max-w-md">
              The AI workstation that thinks ahead. Local models, autonomous agents, 
              full SDLC automation — one self-hosted stack.
            </p>
            <div className="flex gap-2 mt-4">
              {['SOC 2', 'ISO 27001', 'NIST 800-53', 'CMMC L2'].map((badge) => (
                <span key={badge} className="px-2 py-1 rounded bg-white/5 text-xs text-gray-500 border border-white/5">
                  {badge}
                </span>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold text-white mb-4">Product</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
              <li><Link href="/agents" className="hover:text-white transition-colors">Agents</Link></li>
              <li><Link href="/deploy" className="hover:text-white transition-colors">Deploy</Link></li>
              <li><Link href="/api" className="hover:text-white transition-colors">API</Link></li>
              <li><Link href="/iso" className="hover:text-white transition-colors">Live ISO</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-white mb-4">Resources</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
              <li><Link href="/providers" className="hover:text-white transition-colors">Providers</Link></li>
              <li>
                <a href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation" 
                   className="hover:text-white transition-colors flex items-center gap-1"
                   target="_blank" rel="noopener noreferrer">
                  <Github size={14} /> GitHub
                </a>
              </li>
              <li>
                <a href="https://github.com/ProjectZeroDays" 
                   className="hover:text-white transition-colors flex items-center gap-1"
                   target="_blank" rel="noopener noreferrer">
                  <Twitter size={14} /> Twitter
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-white/10 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-500 text-sm">
            © 2026 FreeAI. MIT License.
          </p>
          <div className="flex items-center gap-6">
            <a href="https://github.com/ProjectZeroDays" className="text-gray-400 hover:text-white transition-colors">
              <Github size={20} />
            </a>
            <span className="text-gray-500 text-sm">Privacy · Terms · Security</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
