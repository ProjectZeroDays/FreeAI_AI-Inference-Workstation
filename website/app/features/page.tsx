import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

const features = [
  {
    category: 'Router',
    icon: '⬡',
    items: [
      'Keyword classifier with confidence score',
      'Fallback chain across roster',
      'Degenerate output detection',
      'LRU response cache (X-Cache: HIT/MISS)',
      'Per-client rate limiting (429)',
      'Optional X-API-Key auth',
      '/metrics endpoint',
    ],
  },
  {
    category: 'Agent API',
    icon: '◉',
    items: [
      'project / refactor / debug / analyze endpoints',
      'Profiles: strict, balanced, creative, verbose, minimal',
      'Session memory (20 turns x 100 sessions)',
      'Error envelopes',
      'Call counters',
    ],
  },
  {
    category: 'Workflow Engine',
    icon: '⟁',
    items: [
      'Registry-based pipelines',
      'Sequential + parallel steps',
      '3-attempt retry per step',
      'Missing-dependency validation',
      'JSONL audit log',
      'Export/import definitions',
      '4 shipped templates',
    ],
  },
  {
    category: 'Autonomous SDLC',
    icon: '⟿',
    items: [
      '7-phase lifecycle: plan→code→test→fix→review→doc→package',
      'Real verification: compileall, pytest, node --check',
      'Sandboxed workspaces',
      'Artifact tarball download',
      'Run cancellation',
      'Concurrency cap',
    ],
  },
  {
    category: 'Security',
    icon: '◈',
    items: [
      'Aikido integration',
      'Pentest agents',
      'Auto-patching',
      '33 security skills (14 Red, 12 Blue, 7 Purple)',
      'API key rotation (10 keys per provider)',
      'Semgrep, Bandit, Safety, Trivy',
    ],
  },
  {
    category: 'GPU Inference',
    icon: '⬢',
    items: [
      'llama.cpp (:9001) — GGUF CUDA',
      'vLLM (:9002) — high throughput',
      'FreeToken (:9100) — edge MoE 290B+',
      'Hot model hot-swap (/admin/model-switch)',
      'MTP speculative decoding',
      'Parallel hot models (per-GPU CUDA_VISIBLE_DEVICES)',
    ],
  },
  {
    category: 'Dashboard',
    icon: '◫',
    items: [
      'GPU stats with Chart.js history',
      'Alerts panel (services, thermal, util)',
      'Service UP/DOWN badges',
      'Settings panel with presets',
      'Model shelf (registry vs disk)',
      'SSE live updates',
    ],
  },
  {
    category: 'Optimizer',
    icon: '⚡',
    items: [
      'performance/balanced/eco power modes',
      'Hysteresis + 10-min cooldown',
      'GPU power cap + clock lock',
      'nvidia-persistenced enablement',
    ],
  },
  {
    category: 'Desktop',
    icon: '🖥',
    items: [
      'XFCE + TigerVNC',
      'noVNC (:6080)',
      'Remote access via browser',
    ],
  },
  {
    category: 'Integration',
    icon: '⊞',
    items: [
      'SendGrid, Gmail, Proton (email)',
      'Twilio (SMS)',
      'Telegram, WhatsApp, Signal',
      '40+ MCP servers',
      'Salad GPU marketplace',
    ],
  },
]

export default function Features() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            174 <span className="gradient-text">Features</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Everything you need for a production-grade AI inference workstation.
          </p>
        </div>

        <div className="space-y-8">
          {features.map((category) => (
            <div key={category.category} className="page-card">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl leading-none">{category.icon}</span>
                <h2 className="text-lg font-semibold text-white">{category.category}</h2>
                <span className="ml-auto page-badge page-badge-blue text-xs">{category.items.length}</span>
              </div>
              <ul className="space-y-2">
                {category.items.map((item) => (
                  <li key={item} className="flex items-start gap-3 text-slate-300 text-sm">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
