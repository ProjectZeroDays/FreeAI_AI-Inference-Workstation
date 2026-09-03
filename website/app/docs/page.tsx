import Link from 'next/link'
import { ArrowLeft, BookOpen, FileText, Terminal, Shield, Cpu, Zap } from 'lucide-react'

const docCategories = [
  {
    title: 'Getting Started',
    icon: <Terminal className="w-5 h-5" />,
    docs: [
      { title: 'Installation', href: '/deploy' },
      { title: 'Quick Start', href: '/#deploy' },
      { title: 'System Requirements', href: '/deploy#hardware' },
    ],
  },
  {
    title: 'Core Concepts',
    icon: <BookOpen className="w-5 h-5" />,
    docs: [
      { title: 'Model Router', href: '/features#router' },
      { title: 'Agent System', href: '/agents' },
      { title: 'Workflow Engine', href: '/features#workflow' },
      { title: 'GPU Inference', href: '/features#gpu' },
    ],
  },
  {
    title: 'Security',
    icon: <Shield className="w-5 h-5" />,
    docs: [
      { title: 'Security Overview', href: '/security' },
      { title: 'Red Team Agents', href: '/agents#red-team' },
      { title: 'Blue Team Agents', href: '/agents#blue-team' },
      { title: 'Purple Team', href: '/agents#purple-team' },
    ],
  },
  {
    title: 'Deployment',
    icon: <Cpu className="w-5 h-5" />,
    docs: [
      { title: 'Bare Metal', href: '/deploy#bare-metal' },
      { title: 'Docker Compose', href: '/deploy#docker' },
      { title: 'Kubernetes', href: '/deploy#kubernetes' },
      { title: 'Live ISO', href: '/iso' },
    ],
  },
  {
    title: 'API Reference',
    icon: <Zap className="w-5 h-5" />,
    docs: [
      { title: 'Router API', href: '/api#router' },
      { title: 'Agent API', href: '/api#agents' },
      { title: 'Workflow API', href: '/api#workflow' },
      { title: 'Dashboard API', href: '/api#dashboard' },
    ],
  },
]

export default function Docs() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            <span className="gradient-text">Documentation</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Complete guide to FreeAI — from installation to advanced configurations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {docCategories.map((category) => (
            <div key={category.title} className="page-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-blue-500/15 flex items-center justify-center text-blue-400">
                  {category.icon}
                </div>
                <h2 className="text-base font-semibold text-white">{category.title}</h2>
              </div>
              <ul className="space-y-2">
                {category.docs.map((doc) => (
                  <li key={doc.title}>
                    <Link href={doc.href} className="text-slate-400 hover:text-white text-sm transition-colors">
                      {doc.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="p-6 rounded-xl bg-blue-500/10 border border-blue-500/20">
          <h2 className="text-lg font-semibold text-white mb-3">Quick Links</h2>
          <div className="flex flex-wrap gap-3">
            <Link href="/deploy" className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors">
              Deploy Guide
            </Link>
            <Link href="/features" className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm transition-colors">
              Features
            </Link>
            <Link href="/api" className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm transition-colors">
              API Reference
            </Link>
            <Link href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation" target="_blank" rel="noopener noreferrer" className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm transition-colors">
              GitHub
            </Link>
            <Link href="/api" className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-white text-sm transition-colors border border-white/10">
              API Reference
            </Link>
            <a href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation" target="_blank" rel="noopener noreferrer" className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/15 text-white text-sm transition-colors border border-white/10">
              GitHub
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
