import Link from 'next/link'
import { ArrowLeft, BookOpen, FileText, Terminal, Shield, Cpu, Zap } from 'lucide-react'

const docCategories = [
  {
    title: 'Getting Started',
    icon: <Terminal className="w-5 h-5" />,
    docs: [
      { title: 'Installation', href: '#installation' },
      { title: 'Quick Start', href: '#quick-start' },
      { title: 'System Requirements', href: '#requirements' },
      { title: 'macOS Setup', href: '#macos' },
      { title: 'Windows Setup', href: '#windows' },
    ],
  },
  {
    title: 'Core Concepts',
    icon: <BookOpen className="w-5 h-5" />,
    docs: [
      { title: 'Model Router', href: '#router' },
      { title: 'Agent System', href: '#agents' },
      { title: 'Workflow Engine', href: '#workflow' },
      { title: 'GPU Inference', href: '#gpu' },
    ],
  },
  {
    title: 'Security',
    icon: <Shield className="w-5 h-5" />,
    docs: [
      { title: 'Security Overview', href: '#security-overview' },
      { title: 'Red Team Agents', href: '#red-team' },
      { title: 'Blue Team Agents', href: '#blue-team' },
      { title: 'Purple Team', href: '#purple-team' },
    ],
  },
  {
    title: 'Deployment',
    icon: <Cpu className="w-5 h-5" />,
    docs: [
      { title: 'Bare Metal', href: '#bare-metal' },
      { title: 'Docker Compose', href: '#docker' },
      { title: 'Kubernetes', href: '#kubernetes' },
      { title: 'Cloud Providers', href: '#cloud' },
      { title: 'Live ISO', href: '#iso' },
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
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            <span className="gradient-text">Documentation</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Complete guide to FreeAI — from installation to advanced configurations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {docCategories.map((category) => (
            <div key={category.title} className="p-6 rounded-xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
                  {category.icon}
                </div>
                <h2 className="text-lg font-semibold text-white">{category.title}</h2>
              </div>
              <ul className="space-y-2">
                {category.docs.map((doc) => (
                  <li key={doc.title}>
                    <Link href={doc.href} className="text-gray-400 hover:text-white text-sm transition-colors">
                      {doc.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 p-6 rounded-xl bg-primary/10 border border-primary/30">
          <h2 className="text-xl font-semibold text-white mb-3">Quick Links</h2>
          <div className="flex flex-wrap gap-4">
            <Link href="/deploy" className="px-4 py-2 rounded-lg bg-primary text-white text-sm hover:bg-primary-hover transition-colors">
              Deploy Guide
            </Link>
            <Link href="/features" className="px-4 py-2 rounded-lg bg-white/10 text-white text-sm hover:bg-white/20 transition-colors">
              Features
            </Link>
            <Link href="/api" className="px-4 py-2 rounded-lg bg-white/10 text-white text-sm hover:bg-white/20 transition-colors">
              API Reference
            </Link>
            <Link href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation" target="_blank" className="px-4 py-2 rounded-lg bg-white/10 text-white text-sm hover:bg-white/20 transition-colors">
              GitHub
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
