import Link from 'next/link'
import { ArrowRight, Download, BookOpen, Cpu, Shield, Zap, Code, Terminal, Globe, Server, Wifi, Lock, ChevronRight, Play, CheckCircle, AlertCircle, Clock } from 'lucide-react'
import { motion } from 'framer-motion'

const stats = [
  { value: '174', label: 'Features' },
  { value: '55+', label: 'Skills' },
  { value: '24', label: 'Agents' },
  { value: '40+', label: 'MCPs' },
  { value: '21+', label: 'Providers' },
]

const askPrompts = [
  'Generate deployment plan for Ubuntu + NVIDIA GPU',
  'Show current GPU utilization across all nodes',
  'Draft CI/CD pipeline for microservice X',
  'Scan repo for security issues and CVEs',
  'Compare bare metal vs Docker performance',
  'List all running models and their VRAM usage',
]

const askPromptsSecondary = [
  'Schedule model downloads outside peak hours',
  'Export compliance report for SOC 2 audit',
  'Which models are outdated on GPU clusters?',
  'Move workloads to cloud fallback provider',
  'Summarize last nights autonomous SDLC runs',
  'What broke after the CUDA toolkit update?',
]

const artifactCards = [
  {
    pill: 'Security report',
    title: 'CVE-2026-4102 — Fleet exposure',
    meta: '6 agents consulted · just now',
    metric: '27 exposed, 24 patchable',
    row: '24 patchable tonight · no user impact',
    action: 'Create patch rollout',
    type: 'exposure',
  },
  {
    pill: 'Policy compare',
    title: 'Bare Metal vs Docker vs K8s',
    meta: 'v1.2.0 · v1.2.0 · v1.2.0',
    metric: '0/4 sections identical · 3 conflicts',
    row: 'GPU passthrough only on bare metal',
    action: 'Open comparison',
    actionAlt: 'Apply fix',
    type: 'compare',
  },
  {
    pill: 'Anomaly',
    title: 'GPU utilization spike — Node 3',
    meta: 'today · 09:14 UTC',
    metric: '+38% load in 20 min · 4x baseline',
    row: 'Flagged and contained',
    action: 'Investigate',
    actionAlt: 'Alert rule',
    type: 'anomaly',
  },
  {
    pill: 'Action receipt',
    title: 'Patch rollout #241 — completed',
    meta: 'approved by admin · logged 02:14 · reversible',
    checks: ['24/24 devices patched', '0 regressions detected', '3 held for Sun 02:00'],
    action: 'View in history',
    type: 'receipt',
  },
]

const pillars = [
  {
    icon: <Cpu className="w-6 h-6" />,
    title: 'Hardware & GPU Intelligence',
    description: 'Every device state understood in context — posture, compliance, location, history, and GPU utilization.',
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: 'SDLC Automation',
    description: 'Apps deployed, updated and retired by policy — 7-phase autonomous lifecycle with real compilation tests.',
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: 'Security by Operation',
    description: 'Security embedded in daily operations — Aikido integration, pentest agents, auto-patching, not bolted on.',
  },
  {
    icon: <Globe className="w-6 h-6" />,
    title: 'Developer Experience',
    description: 'IT that feels invisible — VSCode extension, desktop clients, browser automation, MCP tools.',
  },
]

const qaItems = [
  { q: 'Which models are non-compliant right now?', a: '60 devices, mostly outdated drivers. Want a breakdown — or a workflow to fix it?' },
  { q: 'Show GPU utilization across all nodes', a: 'Node 1: 87% · Node 2: 23% · Node 3: 94% (spike detected) · Node 4: 45%' },
  { q: 'What-if: move workload to Salad GPU marketplace', a: 'Estimated cost: $1.20/hr · Latency: +45ms · 3 instances available now' },
]

const deployMethods = [
  { name: 'Bare Metal', command: 'sudo ./hardware/install-stack.sh', for: 'Production servers' },
  { name: 'Docker Compose', command: 'docker compose --profile allinone up -d', for: 'Any host with NVIDIA Docker' },
  { name: 'Kubernetes', command: 'kubectl apply -f k8s/', for: 'Cloud-native deployments' },
  { name: 'Live ISO', command: 'Boot freeaios-amd64.iso', for: 'No-install workstation' },
]

const isoVariants = [
  { name: 'Ubuntu 24.04 XFCE', desc: 'Default desktop with full FreeAI stack pre-loaded', icon: '🐧' },
  { name: 'Kali Linux Rolling', desc: 'Full penetration-testing suite with networking preserved', icon: '🔴' },
  { name: 'Kodachi Linux', desc: 'Security-focused — Kali hardened with extra privacy tools', icon: '🔐' },
  { name: 'Debian 12', desc: 'Stable base with XFCE desktop and FreeAI tools', icon: '🦩' },
  { name: 'NixOS Minimum', desc: 'Declarative, reproducible, secure by default', icon: '❄️' },
]

const osSupport = [
  { os: 'Linux (Ubuntu/Kali/NixOS)', steps: 'git clone → sudo ./hardware/install-stack.sh → bash models/auto-download-models.sh', method: 'Bare Metal' },
  { os: 'macOS (Intel / Apple Silicon)', steps: 'brew install docker → docker compose --profile allinone up -d', method: 'Docker / Colima' },
  { os: 'Windows 10/11', steps: 'Install WSL2 → wsl --install -d Ubuntu → docker compose --profile allinone up -d', method: 'WSL2 + Docker' },
]

const complianceBadges = ['SOC 2 Type II', 'ISO 27001', 'NIST 800-53', 'CMMC L2/L3', 'FedRAMP Ready', 'DOD IL4']

const features = [
  {
    icon: <Zap className="w-6 h-6" />,
    title: 'Model Router',
    description: 'Classifies prompts, routes to best backend, automatic fallback chains, LRU cache, 21+ providers.',
  },
  {
    icon: <Code className="w-6 h-6" />,
    title: 'Autonomous Agents',
    description: '7-phase SDLC: plan → code → verify → fix → review → document → package. Real compilation tests.',
  },
  {
    icon: <Cpu className="w-6 h-6" />,
    title: 'GPU Inference',
    description: 'llama.cpp (:9001), vLLM (:9002), FreeToken (:9100) — local GGUF serving with 21+ bridges.',
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: 'Security',
    description: 'Aikido integration, pentest agents, auto-patching, 33 security skills (14 Red, 12 Blue, 7 Purple).',
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: 'Workflow Engine',
    description: 'Visual pipeline designer with validation, templates, audit logs, export/import.',
  },
  {
    icon: <BookOpen className="w-6 h-6" />,
    title: 'Live ISO',
    description: 'Bootable FreeAIOS — Ubuntu/Kodachi/Kali/NixOS with install, live, and rescue modes.',
  },
]

export default function Home() {
  return (
    <div className="min-h-screen bg-[#060a18] text-gray-100">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Background orbs */}
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-float" />
        <div className="absolute top-40 right-1/4 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-20 left-1/2 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }} />

        <div className="relative max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-gray-400 mb-6">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              v1.2.0 — Autonomous SDLC Agents & Aikido Security
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              The AI workstation<br />
              <span className="gradient-text">that thinks ahead.</span>
            </h1>

            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
              FreeAI unifies GPU-optimized model serving, autonomous SDLC agents, 
              security scanning, and builder tools — all in one self-hosted stack.
            </p>

            <div className="flex flex-wrap gap-3 justify-center mb-8">
              {complianceBadges.map((badge) => (
                <span key={badge} className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs text-gray-400">
                  {badge}
                </span>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/deploy"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold transition-all hover:scale-105"
              >
                <Download size={20} />
                Deploy FreeAI
              </Link>
              <Link
                href="/docs"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/5 hover:bg-white/10 text-white rounded-lg font-semibold transition-all border border-white/10"
              >
                <BookOpen size={20} />
                Read Docs
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="grid grid-cols-5 gap-8 mt-20 max-w-4xl mx-auto"
          >
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white">{stat.value}</div>
                <div className="text-sm text-gray-400 mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Ask FreeAI Agents Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ask FreeAI <span className="gradient-text">Agents</span>
            </h2>
            <p className="text-gray-400 text-lg">
              Anything you'd hand a senior DevOps engineer.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {askPrompts.map((prompt, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center gap-3 px-5 py-4 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 hover:bg-white/10 transition-all cursor-pointer group"
              >
                <Terminal className="w-4 h-4 text-blue-400 flex-shrink-0" />
                <span className="text-sm text-gray-300 group-hover:text-white transition-colors">{prompt}</span>
                <ChevronRight className="w-4 h-4 text-gray-500 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.div>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {askPromptsSecondary.map((prompt, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: (i + 6) * 0.05 }}
                className="flex items-center gap-3 px-5 py-4 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 hover:bg-white/10 transition-all cursor-pointer group"
              >
                <Play className="w-4 h-4 text-purple-400 flex-shrink-0" />
                <span className="text-sm text-gray-300 group-hover:text-white transition-colors">{prompt}</span>
                <ChevronRight className="w-4 h-4 text-gray-500 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Artifacts Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Every answer, an <span className="gradient-text">artifact.</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Reports, comparisons, insights — and a receipt for every action taken.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {artifactCards.map((card, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-6 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <span className="inline-block px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs font-medium mb-2">
                      {card.pill}
                    </span>
                    <h3 className="text-lg font-semibold text-white">{card.title}</h3>
                    <p className="text-xs text-gray-500 mt-1">{card.meta}</p>
                  </div>
                  {card.type === 'exposure' && (
                    <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                      <AlertCircle className="w-6 h-6 text-red-400" />
                    </div>
                  )}
                  {card.type === 'compare' && (
                    <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center">
                      <ChevronRight className="w-6 h-6 text-purple-400" />
                    </div>
                  )}
                  {card.type === 'anomaly' && (
                    <div className="w-12 h-12 rounded-full bg-yellow-500/10 flex items-center justify-center">
                      <AlertCircle className="w-6 h-6 text-yellow-400" />
                    </div>
                  )}
                  {card.type === 'receipt' && (
                    <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-green-400" />
                    </div>
                  )}
                </div>

                {card.metric && (
                  <div className="text-2xl font-bold text-white mb-1">{card.metric}</div>
                )}

                {card.row && (
                  <p className="text-sm text-gray-400 mb-4">{card.row}</p>
                )}

                {card.checks && (
                  <ul className="space-y-2 mb-4">
                    {card.checks.map((check, j) => (
                      <li key={j} className="flex items-center gap-2 text-sm text-gray-300">
                        <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                        {check}
                      </li>
                    ))}
                  </ul>
                )}

                <div className="flex gap-3 mt-4">
                  <button className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-sm font-medium transition-colors">
                    {card.action}
                  </button>
                  {card.actionAlt && (
                    <button className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 text-sm font-medium transition-colors border border-white/10">
                      {card.actionAlt}
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof / Trusted By */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white/5 border-y border-white/5">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-lg font-semibold text-gray-400 mb-8">Trusted by developers worldwide</h2>
            <div className="flex flex-wrap justify-center gap-8 items-center">
              {['GitHub', 'Vercel', 'DigitalOcean', 'Hetzner', 'RunPod', 'Salad'].map((name) => (
                <div key={name} className="px-6 py-3 rounded-lg bg-white/5 text-gray-500 font-medium text-sm">
                  {name}
                </div>
              ))}
            </div>
            <div className="flex justify-center gap-6 mt-8">
              {['⭐ 4.8/5 Capterra', '⭐ 4.9/5 G2', 'SOC 2 Certified'].map((badge) => (
                <span key={badge} className="text-sm text-gray-400">{badge}</span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Problem Framing */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
              The workplace became digital.<br />
              <span className="text-gray-500">Operations stayed manual.</span>
            </h2>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-16">
            {[
              'Too many tools',
              'Too many policies',
              'Too many manual workflows',
              'Too much reactive IT',
              'Too little operational intelligence',
            ].map((pain, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-4 rounded-xl bg-red-500/5 border border-red-500/10 text-center"
              >
                <span className="text-sm text-red-400">{pain}</span>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-8 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-white/10"
          >
            <h3 className="text-2xl font-bold text-white mb-6 text-center">
              The next step: the <span className="gradient-text">Autonomous Workplace</span>.
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {['Context-aware', 'Policy-driven', 'AI-assisted', 'Security-integrated', 'Developer-centric', 'Continuously optimized'].map((attr) => (
                <div key={attr} className="flex items-center gap-2 text-gray-300">
                  <CheckCircle className="w-5 h-5 text-blue-400 flex-shrink-0" />
                  <span>{attr}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Four Pillars */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              One platform, <span className="gradient-text">four pillars.</span>
            </h2>
            <p className="text-gray-400 text-lg">
              Built on what FreeAI already delivers today.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {pillars.map((pillar, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all"
              >
                <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center text-primary mb-4">
                  {pillar.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{pillar.title}</h3>
                <p className="text-gray-400">{pillar.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* One Brain - Interactive Q&A */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
              One brain. <span className="gradient-text">Your whole fleet.</span>
            </h2>
            <p className="text-gray-400 text-lg">
              It sees. It simulates. It acts. You approve.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left: Question list */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Ask anything about your fleet</h3>
              {qaItems.map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <span className="text-blue-400 text-xs font-bold">Q</span>
                    </div>
                    <p className="text-gray-300 text-sm">{item.q}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Right: AI Answer panel */}
            <div className="p-6 rounded-2xl bg-black/30 border border-white/10">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-sm text-gray-400">AI Response</span>
              </div>
              <div className="space-y-4">
                {qaItems.map((item, i) => (
                  <div key={i} className="pb-4 border-b border-white/5 last:border-0 last:pb-0">
                    <p className="text-xs text-gray-500 mb-1">Q: {item.q}</p>
                    <div className="flex items-start gap-2">
                      <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                        <span className="text-purple-400 text-xs">A</span>
                      </div>
                      <p className="text-gray-300 text-sm">{item.a}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Deep Features Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Everything you need. <span className="gradient-text">Nothing you don't.</span>
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="p-6 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all hover:bg-white/10"
              >
                <div className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center text-primary mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Live ISO Variants */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              FreeAIOS — <span className="gradient-text">Live ISO</span>
            </h2>
            <p className="text-gray-400 text-lg">
              Bootable workstations for any purpose. No install required.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {isoVariants.map((iso, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-6 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all"
              >
                <div className="text-3xl mb-3">{iso.icon}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{iso.name}</h3>
                <p className="text-gray-400 text-sm">{iso.desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-6 rounded-xl bg-white/5 border border-white/10"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Build Your Own ISO</h3>
            <pre className="bg-black/50 rounded-lg p-4 text-sm text-green-400 overflow-x-auto font-mono">
{`# Requirements
sudo apt-get install -y xorriso isolinux

# Build from Ubuntu ISO
UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso \\
./live/build-live.sh

# Optional: bake repo into ISO for offline install
REPO_TARBALL=../dist/freeai-v1.2.0.tar.gz \\
./live/build-live.sh`}
            </pre>
          </motion.div>
        </div>
      </section>

      {/* OS Support Matrix */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Works on <span className="gradient-text">any OS</span>
            </h2>
            <p className="text-gray-400 text-lg">
              Linux, macOS, and Windows — all supported.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {osSupport.map((os, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-6 rounded-xl bg-white/5 border border-white/10"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Server className="w-6 h-6 text-blue-400" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">{os.os}</h3>
                    <span className="text-xs text-gray-500">{os.method}</span>
                  </div>
                </div>
                <pre className="bg-black/50 rounded-lg p-3 text-xs text-green-400 overflow-x-auto font-mono">
                  {os.steps}
                </pre>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Diagram */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Architecture</h2>
          </motion.div>

          <motion.pre
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="bg-black/50 rounded-xl p-6 text-sm text-gray-300 overflow-x-auto font-mono"
          >
{`                    ┌───────────────────────────────────────────────────────┐
                    │              FreeAI Dashboard (:8030)                 │
                    │        Flask + Chart.js + SSE + Authentication        │
                    ├───────────────────────────┬────────────────┬──────────┤
                    │  Router  │ Agents    │ Workflow │      Autonomous     │
                    │  :8010   │ :8020     │  :8040   │       :8050         │
                    │          │           │          │                     │
                    │ classify │ plan→code │ chain    │   7-phase SDLC      │
                    │ fallback │ verify    │ validate │   real compilation  │
                    │ cache    │ fix       │ template │   auto-package      │
                    ├───────────────────────────┴────────────────┴──────────┤
                    │              MCP Registry (40+ servers)               │
                    │    Aikido · SendGrid · Twilio · Telegram · WhatsApp   │
                    ├───────────────────────────────────────────────────────┤
                    │                  GPU Inference Layer                  │
                    │ llama.cpp  (:9001) · vLLM (:9002) · FreeToken (:9100) │
                    └───────────────────────────────────────────────────────┘`}
          </motion.pre>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-12 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready for an autonomous workplace?
            </h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              Deploy FreeAI in minutes. Local models, autonomous agents, full SDLC automation — on your hardware, your rules.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/deploy"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary hover:bg-primary-hover text-white rounded-lg font-semibold transition-all hover:scale-105"
              >
                <Download size={20} />
                Open Deploy Guide
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/5 hover:bg-white/10 text-white rounded-lg font-semibold transition-all border border-white/10"
              >
                <Terminal size={20} />
                Launch Dashboard
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
