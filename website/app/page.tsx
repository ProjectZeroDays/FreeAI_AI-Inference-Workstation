'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  Shield, Zap, Target, Globe, Users, Cpu, Server, Wifi,
  Smartphone, Cloud, FileText, Bot, ChevronDown, Check,
  ArrowRight, Download, Play, Star, Award, Lock, Eye,
  Terminal, Activity, GitBranch, Layers, Monitor, Bug,
  ChevronRight, Clock, BarChart3, UserCheck, RefreshCw,
  AlertTriangle, Mic, ArrowUpRight
} from 'lucide-react';

const FAQ_DATA = [
  { q: 'How do I get started with FreeAI?', a: 'Download any Live ISO from our ISO page and boot it. The automated installer configures all services in under 10 minutes.' },
  { q: 'Does FreeAI support GPU acceleration?', a: 'Yes! FreeAI supports CUDA, ROCm, and oneAPI for GPU-accelerated inference and analysis.' },
  { q: 'Can I use FreeAI for commercial purposes?', a: 'FreeAI is GPL-3.0 licensed. Commercial use is permitted under the same terms.' },
  { q: 'How often are CVE databases updated?', a: 'Our CVE feeds update automatically every 6 hours from NVD, MITRE, and GitHub advisory APIs.' },
  { q: 'What hardware do I need?', a: 'Minimum: 8GB RAM, 4 CPU cores. Recommended: 16GB RAM, 8+ cores, NVIDIA GPU for ML workloads.' },
  { q: 'How does the AI fleet orchestration work?', a: '24 autonomous agents are routed through a central orchestrator that coordinates red/blue/purple team operations in real-time.' },
];

export default function Home() {
  const [counters, setCounters] = useState({ downloads: 0, agents: 0, countries: 0, vulns: 0 });
  const statsRef = useRef<HTMLDivElement>(null);
  const [statsVisible, setStatsVisible] = useState(false);

  useEffect(() => {
    const checkStats = () => {
      if (statsRef.current) {
        const rect = statsRef.current.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.8 && !statsVisible) {
          setStatsVisible(true);
          animateCounters();
        }
      }
    };
    window.addEventListener('scroll', checkStats);
    return () => window.removeEventListener('scroll', checkStats);
  }, [statsVisible]);

  // Scroll-triggered reveal for all sections
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -60px 0px' }
    );
    document.querySelectorAll('.scroll-reveal').forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const animateCounters = () => {
    const targets = { downloads: 671000, agents: 24, countries: 50, vulns: 21 };
    const duration = 2000;
    const steps = 60;
    const interval = duration / steps;
    let step = 0;
    const timer = setInterval(() => {
      step++;
      const progress = Math.min(step / steps, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCounters({
        downloads: Math.floor(targets.downloads * eased),
        agents: Math.floor(targets.agents * eased),
        countries: Math.floor(targets.countries * eased),
        vulns: Math.floor(targets.vulns * eased)
      });
      if (step >= steps) clearInterval(timer);
    }, interval);
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(0) + 'K';
    return num.toString();
  };

  const prompts = [
    { text: "Who's still on macOS 13?", icon: Monitor },
    { text: "Lock every device in the Paris office", icon: Lock },
    { text: "Why did enrollment spike this morning?", icon: Activity },
    { text: "Draft a rollout plan for Chrome 126", icon: RefreshCw },
    { text: "Which kiosks are offline right now?", icon: Eye },
    { text: "Compare staging vs production policies", icon: GitBranch },
    { text: "Schedule reboots outside shift hours", icon: Clock },
    { text: "Export a compliance report for the audit", icon: FileText },
    { text: "Which apps are out of date on exec laptops?", icon: Smartphone },
    { text: "Move Store #24 to the Madrid segment", icon: Globe },
    { text: "Summarize last night's patch run", icon: BarChart3 },
    { text: "What broke after the macOS 15.6 update?", icon: AlertTriangle },
  ];

  const agents = [
    { name: 'Red Orchestrator', role: 'red', icon: Target, desc: 'Autonomous red team coordination' },
    { name: 'PhishingSimulator', role: 'red', icon: Eye, desc: 'Enterprise phishing simulations' },
    { name: 'CredsHarvester', role: 'red', icon: Bot, desc: 'Credential harvesting operations' },
    { name: 'LlmAdversarial', role: 'red', icon: Terminal, desc: 'LLM prompt injection attacks' },
    { name: 'WifiRogue', role: 'red', icon: Wifi, desc: 'WiFi deauth & rogue AP attacks' },
    { name: 'ExploitDev', role: 'red', icon: Shield, desc: 'Custom exploit development' },
    { name: 'ZeroClickFinder', role: 'red', icon: Zap, desc: 'Zero-click vulnerability hunting' },
    { name: 'VulnAssessor', role: 'red', icon: Activity, desc: 'Vulnerability assessment engine' },
    { name: 'NetworkScanner', role: 'red', icon: Globe, desc: 'Full network reconnaissance' },
    { name: 'SocialEngineer', role: 'red', icon: Users, desc: 'Social engineering campaigns' },
    { name: 'WebAppScanner', role: 'red', icon: Cloud, desc: 'Web application pentesting' },
    { name: 'WifiJamming', role: 'red', icon: Wifi, desc: 'Wireless jamming operations' },
    { name: 'Blue Orchestrator', role: 'blue', icon: Shield, desc: 'Defensive operations coordination' },
    { name: 'ThreatHunter', role: 'blue', icon: Eye, desc: 'Proactive threat hunting' },
    { name: 'IocAnalyzer', role: 'blue', icon: Activity, desc: 'IOC pattern analysis' },
    { name: 'MalwareAnalyzer', role: 'blue', icon: Bug, desc: 'Malware behavior analysis' },
    { name: 'ForensicAnalyst', role: 'blue', icon: FileText, desc: 'Digital forensics investigations' },
    { name: 'IncidentResponder', role: 'blue', icon: Zap, desc: 'Automated incident response' },
    { name: 'NetworkDefender', role: 'blue', icon: Globe, desc: 'Network defense operations' },
    { name: 'LogAnalyzer', role: 'blue', icon: Terminal, desc: 'SIEM log correlation' },
    { name: 'DeceptionEngine', role: 'blue', icon: Eye, desc: 'Honeypot & canary deployment' },
    { name: 'Purple Orchestrator', role: 'purple', icon: GitBranch, desc: 'Purple team collaboration' },
    { name: 'AttackSimulation', role: 'purple', icon: Target, desc: 'ATT&CK-based simulations' },
    { name: 'RemediationBot', role: 'purple', icon: Zap, desc: 'Auto-remediation workflows' },
  ];

  const pillars = [
    { icon: Eye, title: 'Device Intelligence', desc: 'Every device state understood in context — posture, compliance, location, history.' },
    { icon: RefreshCw, title: 'Application Automation', desc: 'Apps deployed, updated and retired by policy, across every operating system.' },
    { icon: Shield, title: 'Security by Operation', desc: 'Security embedded in daily operations — not bolted on afterwards.' },
    { icon: Users, title: 'Employee Experience', desc: 'IT that feels invisible to the people it serves.' },
  ];

  const isoVariants = [
    { name: 'Ubuntu 24.04 XFCE', icon: Monitor, version: 'v24.04', size: '2.4 GB' },
    { name: 'Kali Linux Rolling', icon: Shield, version: '2024.3', size: '3.1 GB' },
    { name: 'Debian 12', icon: Server, version: '12.6', size: '2.8 GB' },
    { name: 'NixOS Minimum', icon: Layers, version: '24.05', size: '1.2 GB' },
    { name: 'Alpine Linux', icon: Activity, version: '3.20', size: '0.8 GB' },
  ];

  const faqs = FAQ_DATA;

  const providers = [
    { name: 'Meta', model: 'Llama 3.1' },
    { name: 'OpenAI', model: 'GPT-4o' },
    { name: 'Anthropic', model: 'Claude 3.5' },
    { name: 'Google', model: 'Gemini 1.5' },
    { name: 'Mistral', model: 'Mistral Large' },
    { name: 'Cohere', model: 'Command R+' },
  ];

  const sevenMinds = [
    { name: 'Onboarding', desc: 'New hire provisioned Monday' },
    { name: 'App Rollout', desc: 'Batch deploy to segments' },
    { name: 'Field Services', desc: 'Remote field device management' },
    { name: 'CVE Response', desc: 'Rapid vulnerability mitigation' },
    { name: 'Offboarding', desc: 'Secure device retirement' },
    { name: 'Compliance', desc: 'Audit-ready reporting' },
    { name: 'Patch Ops', desc: 'Scheduled patch campaigns' },
  ];

  return (
    <div className="min-h-screen bg-[#020617]">
      {/* HERO */}
      <section className="relative pt-32 pb-20 overflow-hidden bg-[#0a0f1e]">
        <div className="absolute inset-0 opacity-[0.06]" style={{ backgroundImage: 'radial-gradient(circle, #60a5fa 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-500/10 rounded-full blur-3xl" />

        <div className="container mx-auto px-6 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <div className="ap-hero-badge-dark animate-fade-in-up">
              <Star className="w-4 h-4" />
              <span>The #1 Open Source AI Security Platform</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-black mb-6 leading-[1.08] tracking-tight animate-fade-in-up text-white" style={{ animationDelay: '0.1s' }}>
              Your own AI
              <br />
              <span className="gradient-text">inference stack.</span>
            </h1>

            <p className="text-xl md:text-2xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <strong className="text-white">FreeAI.</strong> Self-hosted GPU inference with 24 autonomous agents, multi-model routing, and full security tooling — deploy anywhere.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <Link href="/deploy" className="ap-btn-primary">
                Get FreeAI <ArrowRight size={18} />
              </Link>
              <Link href="/docs" className="ap-btn-secondary-dark">
                <Play size={16} />
                Watch Demo
              </Link>
            </div>

            {/* One-click install */}
            <div className="max-w-xl mx-auto mb-16 animate-fade-in-up" style={{ animationDelay: '0.35s' }}>
              <button
                onClick={() => {
                  navigator.clipboard.writeText('docker compose --profile allinone up -d');
                }}
                className="w-full flex items-center gap-3 px-4 py-3 bg-[#0f172a] border border-white/10 rounded-xl hover:border-blue-500/50 transition-colors group text-left"
                aria-label="Copy install command"
              >
                <code className="flex-1 text-sm text-slate-300 font-mono">docker compose --profile allinone up -d</code>
                <span className="text-xs text-slate-500 group-hover:text-blue-400 transition-colors flex items-center gap-1">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  Copy
                </span>
              </button>
            </div>

            <div className="flex flex-wrap justify-center gap-3 mb-16 text-sm animate-fade-in-up" style={{ animationDelay: '0.35s' }}>
              {['GPL-3.0', 'Self-hosted', '24+ Providers', 'Multi-GPU', 'Live ISO', 'Docker & K8s'].map((b) => (
                <span key={b} className="px-3 py-1.5 bg-[#0f172a]/80 rounded-full text-xs font-medium text-slate-300 border border-white/10">
                  {b}
                </span>
              ))}
            </div>

            <div className="relative max-w-4xl mx-auto animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
              {/* Animated gradient border glow */}
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-blue-500/30 rounded-3xl blur opacity-50 animate-pulse-glow" />
              <div className="relative bg-[#0f172a] border border-slate-700 rounded-2xl shadow-[0_4px_40px_rgba(0,0,0,0.4)] overflow-hidden">
                <div className="flex items-center gap-2 px-4 py-3 bg-[#0a0f1e] border-b border-slate-700">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                  <div className="flex-1 mx-4 h-7 bg-[#0f172a] rounded-md border border-slate-700 flex items-center px-3">
                    <span className="text-xs text-slate-500">freeai.projectzerodays.com/dashboard</span>
                  </div>
                </div>
                <div className="p-6 bg-[#0a0f1e]/50">
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    {[
                      { label: 'Models Loaded', value: '8', sub: 'active in router', color: '#3b82f6' },
                      { label: 'GPU Utilization', value: '87%', sub: 'RTX 4090', color: '#22c55e' },
                      { label: 'Agents Online', value: '24', sub: 'red/blue/purple', color: '#a78bfa' },
                    ].map((kpi, i) => (
                      <div key={i} className="bg-[#0f172a] rounded-xl p-4 border border-slate-700">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-2 h-2 rounded-full" style={{ background: kpi.color }} />
                          <span className="text-xs text-slate-400 font-medium">{kpi.label}</span>
                        </div>
                        <div className="text-3xl font-bold text-white">{kpi.value}</div>
                        <div className="text-xs text-slate-500 mt-1">{kpi.sub}</div>
                      </div>
                    ))}
                  </div>
                  <div className="bg-[#0f172a] rounded-xl border border-slate-700 p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <span className="text-white font-bold text-xs">F</span>
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-white">FreeAI Chat</div>
                        <div className="text-xs text-slate-500">24 agents online</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="bg-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300 max-w-xs">
                        Scan all endpoints for CVE-2024-3094
                      </div>
                      <div className="bg-blue-900/30 border border-blue-800 rounded-lg px-3 py-2 text-sm text-slate-300 max-w-md ml-auto">
                        <span className="font-semibold text-blue-400">Red Orchestrator:</span>
                        Found 3 affected devices. XZ Utils backdoor detected on ubuntu-prod-02, kali-test-01, debian-build-03. Recommended: isolate & patch immediately.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-6 h-6 text-slate-600" />
        </div>
      </section>

      {/* STATS */}
      <section ref={statsRef} className="py-20 bg-[#0a0f1e] border-y border-slate-700 scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { label: 'Downloads', value: counters.downloads, suffix: '+' },
              { label: 'Countries', value: counters.countries, suffix: '+' },
              { label: 'Autonomous Agents', value: counters.agents, suffix: '' },
              { label: 'CVEs Tracked', value: counters.vulns, suffix: '' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="ap-stat-number">{stat.value > 0 ? formatNumber(stat.value) : '0'}{stat.suffix}</div>
                <div className="ap-stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ASK AGENTS */}
      <section id="ask-agents" className="ap-section scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Ask <span className="gradient-text">Intelligence</span>
            </h2>
            <p className="text-lg text-slate-400">Anything you'd hand a senior admin.</p>
          </div>
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {prompts.map((p, i) => (
                <div key={i} className="ap-prompt-chip-dark">
                  <p className="flex-1">{p.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ARTIFACTS */}
      <section id="artifacts" className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Every answer, an <span className="gradient-text">artifact.</span>
            </h2>
            <p className="text-lg text-slate-400">Reports, comparisons, insights — and a receipt for every action taken.</p>
          </div>
          <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
            <div className="ap-card-dark">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-white">Patch status</span>
                <span className="ap-pill ap-pill-blue">Live</span>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm"><span className="text-slate-400">Exposed</span><span className="font-semibold text-red-400">27</span></div>
                <div className="flex justify-between text-sm"><span className="text-slate-400">macOS 14</span><span className="font-semibold text-white">11</span></div>
                <div className="flex justify-between text-sm"><span className="text-slate-400">Windows 11</span><span className="font-semibold text-white">9</span></div>
                <div className="flex justify-between text-sm"><span className="text-slate-400">Android 14</span><span className="font-semibold text-white">7</span></div>
                <div className="pt-3 border-t border-slate-700">
                  <span className="text-sm text-slate-400"><span className="font-semibold text-green-400">24</span> patchable tonight — no user impact</span>
                </div>
              </div>
            </div>
            <div className="ap-card-dark">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-white">Policy comparison</span>
                <span className="ap-pill">v16 vs v17</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-slate-400">
                  <span className="w-5 h-5 rounded bg-green-900/40 text-green-400 flex items-center justify-center text-xs font-bold">=</span>
                  <span>0/6 sections identical</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <span className="w-5 h-5 rounded bg-red-900/40 text-red-400 flex items-center justify-center text-xs font-bold">≠</span>
                  <span>3 conflicts explained</span>
                </div>
                <div className="pt-3 border-t border-slate-700 mt-3">
                  <div className="text-xs text-slate-500 mb-2">Staging vs Production</div>
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-16 bg-blue-500 rounded-full" />
                    <div className="h-2 w-12 bg-blue-400 rounded-full" />
                    <div className="h-2 w-8 bg-slate-600 rounded-full" />
                  </div>
                </div>
              </div>
            </div>
            <div className="ap-card-dark">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-white">Action receipt</span>
                <span className="ap-pill ap-pill-blue">Completed</span>
              </div>
              <div className="space-y-3">
                <div className="text-sm">
                  <div className="font-semibold text-white">Patch rollout #241</div>
                  <div className="text-slate-500 text-xs mt-1">approved by admin@org.local · logged 02:14 · reversible</div>
                </div>
                <div className="space-y-1.5 text-sm">
                  {['24/24 devices patched', '0 regressions detected', '3 held for Sun 02:00'].map((item, i) => (
                    <div key={i} className="flex items-center gap-2 text-slate-400">
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
                <button className="text-sm text-blue-400 font-medium hover:text-blue-300 flex items-center gap-1 mt-2">
                  View in history <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TRUSTED BY */}
      <section className="ap-section border-y border-white/10 scroll-reveal">
        <div className="container mx-auto px-6">
          <p className="text-center text-sm text-slate-500 font-medium uppercase tracking-widest mb-10">Built for security researchers, developers &amp; operators</p>
          <div className="flex flex-wrap justify-center gap-x-12 gap-y-6 items-center">
            {['Red Team', 'Blue Team', 'Bug Bounty Hunters', 'Pentesters', 'ML Engineers', 'Sysadmins'].map((name) => (
              <div key={name} className="ap-logo-dark"><span className="text-xl font-bold text-slate-500 tracking-tight">{name}</span></div>
            ))}
          </div>
        </div>
      </section>

      {/* RATINGS */}
      <section className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6">
          <p className="text-center text-sm text-slate-500 font-medium uppercase tracking-widest mb-10">Built with modern tooling</p>
          <div className="flex flex-wrap justify-center gap-4">
            {[
              { label: 'GPL-3.0 Open Source', icon: Shield },
              { label: '21+ AI Providers', icon: Globe },
              { label: 'CUDA & ROCm', icon: Cpu },
              { label: 'Docker & K8s', icon: Layers },
              { label: 'Self-hosted', icon: Server },
              { label: '1156+ Tests', icon: Check },
            ].map((badge, i) => (
              <div key={i} className="flex items-center gap-3 px-5 py-3 bg-[#0f172a] rounded-xl border border-white/10">
                <badge.icon className="w-5 h-5 text-blue-400" />
                <span className="text-sm font-medium text-slate-300">{badge.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROBLEM FRAMING */}
      <section id="why-now" className="ap-section scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight text-white">
              Running AI models is expensive.
              <br /><span className="text-slate-500">Running them securely is harder.</span>
            </h2>
            <div className="flex flex-wrap justify-center gap-3 mt-8">
              {['Cloud API costs add up', 'Data leaves your control', 'No fallback when APIs fail', 'Hard to verify outputs', 'Multi-model coordination is manual'].map((p, i) => (
                <span key={i} className="px-4 py-2 bg-red-900/30 text-red-400 rounded-full text-sm font-medium border border-red-800/50">{p}</span>
              ))}
            </div>
            <p className="text-lg text-slate-400 mt-8">
              The solution: <strong className="text-white">FreeAI</strong> — a self-hosted inference stack that routes, verifies, and secures every request.
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 max-w-4xl mx-auto">
            {['Multi-model routing', 'Automatic fallback', 'Real-time verification', 'Zero data leakage', 'Full audit trails'].map((item, i) => (
              <div key={i} className="text-center p-4 bg-[#0f172a] rounded-xl border border-white/10">
                <div className="text-sm font-semibold text-slate-300">{item}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOUR PILLARS */}
      <section id="capabilities" className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              One stack, <span className="gradient-text">four pillars.</span>
            </h2>
            <p className="text-lg text-slate-400">Everything you need for production AI inference.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {[
              { icon: Cpu, title: 'Model Router', desc: 'Classifies prompts, routes to the best backend, falls back automatically, caches repeats, blocks repetition loops.' },
              { icon: Bot, title: 'Autonomous Agents', desc: 'Plan → code → verify with real compilers → fix → review → document → package. 7-phase SDLC with session memory.' },
              { icon: Shield, title: 'Security Suite', desc: '33 security skills across Red, Blue, and Purple teams. Aikido integration, pentest agents, auto-patching.' },
              { icon: Layers, title: 'Deploy Anywhere', desc: 'Bare metal, Docker Compose, Kubernetes, Vast.ai, or Live ISO. Same code, any environment.' },
            ].map((p, i) => (
              <div key={i} className="ap-card-dark flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-900/40 flex items-center justify-center flex-shrink-0">
                  <p.icon className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-bold text-white mb-1">{p.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{p.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ONE BRAIN / ASK ANYTHING */}
      <section id="ask-anything" className="ap-section scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight text-white">
                Ask anything.<br /><span className="gradient-text">Get verified answers.</span>
              </h2>
              <p className="text-lg text-slate-400 mb-8">Every response is routed through classification, fallback chains, and real verification.</p>
              <div className="space-y-4">
                {[
                  { q: 'Route this prompt to the best model', a: 'Classified as full_project (0.94 confidence) → routed to qwen3.6-12b. Cache HIT in 12ms.' },
                  { q: 'Fallback chain when GPU is busy', a: 'Local 9B → Venice uncensored → OpenRouter → Agnes AI. Each with retry logic and timeout.' },
                  { q: 'Verify output quality', a: 'Degenerate output detection catches repetition loops. Real compiler/tests in SDLC sandboxes.' },
                ].map((item, i) => (
                  <div key={i} className="bg-[#0f172a] rounded-xl p-4 border border-slate-700">
                    <div className="flex items-start gap-3 mb-2">
                      <div className="w-6 h-6 rounded-full bg-blue-900/60 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-blue-400">{i + 1}</span>
                      </div>
                      <div>
                        <div className="font-semibold text-white text-sm">{item.q}</div>
                        <div className="text-sm text-slate-400 mt-1">{item.a}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="bg-[#0f172a] border border-slate-700 rounded-2xl shadow-[0_4px_40px_rgba(0,0,0,0.4)] overflow-hidden">
                <div className="flex items-center gap-2 px-4 py-3 bg-[#0a0f1e] border-b border-slate-700">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
              <span className="flex-1 text-center text-xs text-slate-500">FreeAI Router — Model Routing</span>
                </div>
                <div className="p-4 space-y-4 min-h-[400px]">
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs font-bold">F</span>
                    </div>
                  <div className="bg-[#1e293b] rounded-xl rounded-tl-none px-4 py-3 text-sm text-slate-300 max-w-xs">
                    Route "design a rate limiter" to best available backend
                  </div>
                  </div>
                  <div className="flex gap-3 justify-end">
                    <div className="bg-blue-600 rounded-xl rounded-tr-none px-4 py-3 text-sm text-white max-w-sm">
                      <div className="font-semibold mb-1">qwen3.6-12b (local)</div>
                      Routed via confidence 0.94 · 342ms · Cache MISS · <strong className="text-blue-200">Response ready</strong>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs font-bold">F</span>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs font-bold">F</span>
                    </div>
                    <div className="space-y-2">
                      <div className="bg-[#1e293b] rounded-lg px-3 py-2 text-xs text-slate-400">
                        📊 <strong className="text-slate-300">Verification</strong> — compile passed, tests green
                      </div>
                      <div className="flex gap-2">
                        <button className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg font-medium">Draft upgrade</button>
                        <button className="text-xs px-3 py-1.5 bg-slate-700 border border-slate-600 text-slate-300 rounded-lg font-medium">View details</button>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <input className="flex-1 px-4 py-2.5 bg-[#1e293b] border border-white/10 rounded-xl text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:border-blue-500" placeholder="Ask FreeAI anything..." disabled />
                    <button className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white">
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SEVEN MINDS */}
      <section className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              24 minds.<br /><span className="gradient-text">One workflow.</span>
            </h2>
            <p className="text-lg text-slate-400">Every prompt is classified, routed, verified, and documented — autonomously.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {[
              { name: 'Classify', desc: 'Task type + confidence' },
              { name: 'Route', desc: 'Best backend selection' },
              { name: 'Verify', desc: 'Compiler + test gates' },
              { name: 'Fallback', desc: 'Automatic chain recovery' },
              { name: 'Cache', desc: 'LRU response store' },
              { name: 'Rate Limit', desc: 'Per-client token bucket' },
              { name: 'Log', desc: 'Full audit trail' },
              { name: 'Package', desc: 'Artifact tarball output' },
            ].map((m, i) => (
              <div key={i} className="ap-card-dark text-center p-5">
                <div className="w-10 h-10 rounded-xl bg-blue-900/40 flex items-center justify-center mx-auto mb-3">
                  <span className="text-sm font-bold text-blue-400">{i + 1}</span>
                </div>
                <div className="font-semibold text-white text-sm mb-1">{m.name}</div>
                <div className="text-xs text-slate-400">{m.desc}</div>
              </div>
            ))}
          </div>
          <div className="max-w-2xl mx-auto mt-10">
            <div className="bg-[#1e293b] border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">F</span>
                </div>
                <div>
                  <div className="font-semibold text-white text-sm">Autonomous SDLC Pipeline</div>
                  <div className="text-xs text-slate-500">7-phase lifecycle · real verification · auto-package</div>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-2">
                {['Plan', 'Code', 'Verify', 'Package'].map((stage, i) => (
                  <div key={i} className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                    <div className="text-xs font-semibold text-slate-300">{stage}</div>
                    <div className="text-xs text-green-400 mt-1">✓ done</div>
                  </div>
                ))}
                <div className="bg-blue-500/20 rounded-lg p-3 text-center border border-blue-500/30">
                  <div className="text-xs font-semibold text-blue-300">Running</div>
                  <div className="text-xs text-blue-400 mt-1">● testing</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* LIVE IN MINUTES */}
      <section id="deploy" className="ap-section scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Live in minutes.<br /><span className="gradient-text">Smarter every week.</span>
            </h2>
          </div>
           <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
             {[
               { step: '01', title: 'Clone & configure', desc: 'git clone, set your API keys, go. No cloud account needed.' },
               { step: '02', title: 'Model router classifies', desc: 'Every prompt is scored, routed, cached, and rate-limited automatically.' },
               { step: '03', title: 'Agents verify & ship', desc: 'Real compilers, real tests, real artifacts — in sandboxed workspaces.' },
             ].map((item, i) => (
               <div key={i} className="text-center">
                 <div className="ap-step-num mx-auto">{item.step}</div>
                 <h3 className="font-bold text-white text-lg mb-2">{item.title}</h3>
                 <p className="text-sm text-slate-400 leading-relaxed">{item.desc}</p>
               </div>
             ))}
           </div>
        </div>
      </section>

      {/* OPERATIONAL LAYER IN NUMBERS */}
      <section className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tight text-white">Built for production.</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {[
              { value: '21+', label: 'AI providers routed' },
              { value: '24', label: 'Autonomous agents' },
              { value: '33', label: 'Security skills' },
              { value: '1156+', label: 'Tests passing' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-4xl md:text-5xl font-black gradient-text mb-2">{stat.value}</div>
                <div className="text-sm text-slate-400 leading-snug">{stat.label}</div>
              </div>
            ))}
          </div>
          <div className="max-w-2xl mx-auto mt-16">
            <div className="ap-quote-dark">
              <p className="text-lg text-slate-300 italic leading-relaxed mb-4">
                FreeAI is the only stack that unifies model routing, autonomous SDLC, GPU inference, and security tooling in one self-hosted package.
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">PZ</span>
                </div>
                <div>
                  <div className="font-semibold text-white">ProjectZeroDays</div>
                  <div className="text-sm text-slate-400">Open Source · GPL-3.0</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MCP & A2A */}
      <section className="ap-section scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="ap-card-dark">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-blue-900/40 flex items-center justify-center">
                  <Globe className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <div className="font-bold text-white">MCP</div>
                  <div className="text-xs text-slate-400">Model Context Protocol</div>
                </div>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                200+ platform actions exposed to AI. Everything FreeAI can see, it can do — with your permission.
              </p>
            </div>
            <div className="ap-card-dark">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-purple-900/40 flex items-center justify-center">
                  <GitBranch className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <div className="font-bold text-white">A2A</div>
                  <div className="text-xs text-slate-400">Agent-to-Agent</div>
                </div>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                Agent orchestration across systems — FreeAI agents cooperate with the rest of your stack.
              </p>
            </div>
          </div>
          <div className="max-w-2xl mx-auto mt-12 text-center">
            <p className="text-sm text-slate-400 mb-6">Autonomy is a dial, not a switch.</p>
            <div className="flex items-center justify-center gap-4">
              {['Suggest', 'Approve', 'Auto'].map((mode, i) => (
                <div key={mode} className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all ${i === 1 ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50' : 'bg-[#0f172a] text-slate-400 border border-white/10'}`}>
                  {mode}
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500 mt-3">Set per workflow — recommend only, act after your approval, or run fully autonomous.</p>
          </div>
        </div>
      </section>

      {/* PRICING */}
      <section id="pricing" className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Free forever.<br /><span className="gradient-text">Pay only for your hardware.</span>
            </h2>
            <p className="text-lg text-slate-400">GPL-3.0 licensed. No subscriptions, no cloud lock-in, no hidden fees.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
            <div className="ap-card-dark flex flex-col">
              <div className="mb-6">
                <div className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-2">Self-Hosted</div>
                <div className="flex items-baseline gap-1">
                  <span className="text-5xl font-black text-white">$0</span>
                  <span className="text-slate-400 text-sm">/forever</span>
                </div>
                <p className="text-sm text-slate-400 mt-2">GPL-3.0 · unlimited agents · all features</p>
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                {['24 autonomous agents', 'All security skills (14 Red, 12 Blue, 7 Purple)', '21+ AI providers', 'Live ISO variants', 'GPU inference (llama.cpp, vLLM)', 'Full API access', 'Community support'].map((feat) => (
                  <li key={feat} className="flex items-center gap-2 text-sm text-slate-300">
                    <Check className="w-4 h-4 text-green-400 flex-shrink-0" />{feat}
                  </li>
                ))}
              </ul>
              <Link href="/deploy" className="w-full text-center px-6 py-3 rounded-xl border-2 border-blue-500 text-blue-400 font-semibold hover:bg-blue-500 hover:text-white transition-all">
                Deploy Now
              </Link>
            </div>
            <div className="ap-card-dark flex flex-col">
              <div className="mb-6">
                <div className="text-sm font-semibold text-purple-400 uppercase tracking-wider mb-2">Enterprise Support</div>
                <div className="flex items-baseline gap-1">
                  <span className="text-5xl font-black text-white">Custom</span>
                </div>
                <p className="text-sm text-slate-400 mt-2">Priority support · SLA · custom integrations</p>
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                {['Everything in Self-Hosted', '99.9% uptime SLA', 'Priority email & chat support', 'Custom integrations', 'Dedicated account manager', 'Compliance reporting', 'Training & onboarding'].map((feat) => (
                  <li key={feat} className="flex items-center gap-2 text-sm text-slate-300">
                    <Check className="w-4 h-4 text-purple-400 flex-shrink-0" />{feat}
                  </li>
                ))}
              </ul>
              <Link href="/legal/contact" className="w-full text-center px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold transition-all">
                Contact Sales
              </Link>
            </div>
          </div>
          <p className="text-center text-sm text-slate-500 mt-8">No credit card required. All source code is public on GitHub.</p>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6 max-w-3xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tight text-white">
              Frequently Asked <span className="gradient-text">Questions</span>
            </h2>
          </div>
          <div className="space-y-3">
            {FAQ_DATA.map((faq, i) => (
              <FAQItem key={i} question={faq.q} answer={faq.a} />
            ))}
          </div>
        </div>
      </section>

      {/* LIVE ISO */}
      <section id="live-iso" className="ap-section scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Live <span className="gradient-text">ISO</span> variants
            </h2>
            <p className="text-lg text-slate-400">Boot and deploy in minutes with our pre-configured live environments</p>
          </div>
          <div className="grid md:grid-cols-5 gap-4 max-w-4xl mx-auto">
            {isoVariants.map((iso, i) => (
              <div key={i} className="ap-card-dark text-center p-5 hover:scale-105 transition-transform cursor-pointer">
                <iso.icon className="w-10 h-10 text-blue-400 mx-auto mb-3" />
                <h3 className="font-bold text-white text-sm mb-2">{iso.name}</h3>
                <div className="flex justify-center gap-2 mb-4">
                  <span className="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-400">{iso.version}</span>
                  <span className="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-400">{iso.size}</span>
                </div>
                <Link href="/iso" className="text-sm text-blue-400 font-medium hover:text-blue-300 flex items-center justify-center gap-1">
                  Download <ArrowRight size={14} />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* DEPLOY */}
      <section className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Deploy <span className="gradient-text">your way</span>
            </h2>
            <p className="text-lg text-slate-400">Multiple deployment options to fit your infrastructure</p>
          </div>
          <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              { icon: Server, title: 'Bare Metal', desc: 'Direct hardware deployment', color: 'blue' },
              { icon: Layers, title: 'Docker', desc: 'Containerized quickstart', color: 'purple' },
              { icon: Cloud, title: 'Kubernetes', desc: 'Cloud-native orchestration', color: 'cyan' },
              { icon: Globe, title: 'Cloud', desc: 'AWS, Azure, GCP ready', color: 'green' },
            ].map((option, i) => (
              <div key={i} className="ap-card-dark text-center p-8 hover:scale-105 transition-transform cursor-pointer">
                <div className={`w-14 h-14 mx-auto mb-5 rounded-2xl bg-${option.color}-900/40 flex items-center justify-center`}>
                  <option.icon className={`w-7 h-7 text-${option.color}-400`} />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{option.title}</h3>
                <p className="text-sm text-slate-400">{option.desc}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-10">
            <Link href="/deploy" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium">
              View all deployment methods <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* AI PROVIDERS */}
      <section id="providers" className="ap-section scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Connect with <span className="gradient-text">top AI providers</span>
            </h2>
            <p className="text-lg text-slate-400">Integration with the world's leading LLM providers</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {providers.map((provider, i) => (
              <div key={i} className="ap-card-dark text-center p-6 hover:scale-105 transition-transform cursor-pointer">
                <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-[#0f172a] flex items-center justify-center">
                  <Cpu className="w-7 h-7 text-blue-400" />
                </div>
                <h3 className="text-lg font-bold text-white mb-1">{provider.name}</h3>
                <p className="text-sm text-slate-400">{provider.model}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-10">
            <Link href="/providers" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium">
              View all 21+ providers <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* SECURITY */}
      <section id="security" className="ap-section bg-[#0a0f1e] scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center max-w-5xl mx-auto">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight text-white">
                Security-first{' '}
                <span className="gradient-text">by design</span>
              </h2>
              <p className="text-slate-400 text-lg mb-8">
                Router & model servers are LAN-only by default. UFW opens only ports 22/8030/8050. Autonomous sandboxes reject traversal, absolute paths, and oversized files.
              </p>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { icon: Lock, label: 'AES-256 Encryption' },
                  { icon: Shield, label: 'RBAC Access Control' },
                  { icon: Activity, label: 'Audit Logging' },
                  { icon: Eye, label: 'Threat Detection' },
                ].map((feat, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-[#0f172a] rounded-xl border border-slate-700">
                    <feat.icon className="w-5 h-5 text-blue-400 flex-shrink-0" />
                    <span className="text-sm text-slate-300 font-medium">{feat.label}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="bg-[#0f172a] border border-slate-700 rounded-2xl p-6">
                <div className="space-y-4">
                  {['Network Security: Active', 'Threat Detection: Enabled', 'Encryption: AES-256', 'RBAC: Configured'].map((item, i) => (
                    <div key={i} className="flex items-center gap-4 p-4 bg-slate-700/50 rounded-xl border border-slate-600">
                      <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse" />
                      <span className="text-sm text-slate-300 font-medium">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AGENTS */}
      <section id="agents" className="ap-section scroll-reveal">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight text-white">
              Meet your <span className="gradient-text">agent workforce</span>
            </h2>
            <p className="text-lg text-slate-400">24 specialized AI agents for red team, blue team, and purple team operations.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 max-w-6xl mx-auto">
            {agents.map((agent, i) => (
              <div key={i} className="ap-card-dark p-4 hover:scale-105 transition-transform cursor-pointer">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${
                  agent.role === 'red' ? 'bg-red-900/40' :
                  agent.role === 'blue' ? 'bg-blue-900/40' :
                  'bg-purple-900/40'
                }`}>
                  <agent.icon className={`w-5 h-5 ${
                    agent.role === 'red' ? 'text-red-400' :
                    agent.role === 'blue' ? 'text-blue-400' :
                    'text-purple-400'
                  }`} />
                </div>
                <h3 className="font-bold text-white text-sm mb-1">{agent.name}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{agent.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER — handled by layout.tsx Footer component */}
    </div>
  );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="bg-[#1e293b] border border-white/10 rounded-xl overflow-hidden hover:border-white/20 transition-colors">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-5 text-left flex justify-between items-center hover:bg-white/5 transition-colors"
        aria-expanded={isOpen}
      >
        <span className="font-semibold text-white">{question}</span>
        <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform flex-shrink-0 ml-4 ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="px-5 pb-5 text-slate-400 leading-relaxed">
          {answer}
        </div>
      )}
    </div>
  );
}
