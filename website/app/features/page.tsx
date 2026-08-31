import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { motion } from 'framer-motion'

const features = [
  {
    category: 'Router',
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
    items: [
      'performance/balanced/eco power modes',
      'Hysteresis + 10-min cooldown',
      'GPU power cap + clock lock',
      'nvidia-persistenced enablement',
    ],
  },
  {
    category: 'Desktop',
    items: [
      'XFCE + TigerVNC',
      'noVNC (:6080)',
      'Remote access via browser',
    ],
  },
  {
    category: 'Integration',
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
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            174 <span className="gradient-text">Features</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Everything you need for a production-grade AI inference workstation.
          </p>
        </motion.div>

        <div className="space-y-12">
          {features.map((category, i) => (
            <motion.div
              key={category.category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="p-6 rounded-xl bg-white/5 border border-white/10"
            >
              <h2 className="text-xl font-semibold text-white mb-4">{category.category}</h2>
              <ul className="space-y-2">
                {category.items.map((item, j) => (
                  <li key={j} className="flex items-start gap-3 text-gray-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
