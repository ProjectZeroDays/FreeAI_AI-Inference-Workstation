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

  const faqs = [
    { q: 'How do I get started with FreeAI?', a: 'Download any Live ISO from our ISO page and boot it. The automated installer configures all services in under 10 minutes.' },
    { q: 'Does FreeAI support GPU acceleration?', a: 'Yes! FreeAI supports CUDA, ROCm, and oneAPI for GPU-accelerated inference and analysis.' },
    { q: 'Can I use FreeAI for commercial purposes?', a: 'FreeAI is GPL-3.0 licensed. Commercial use is permitted under the same terms.' },
    { q: 'How often are CVE databases updated?', a: 'Our CVE feeds update automatically every 6 hours from NVD, MITRE, and GitHub advisory APIs.' },
    { q: 'What hardware do I need?', a: 'Minimum: 8GB RAM, 4 CPU cores. Recommended: 16GB RAM, 8+ cores, NVIDIA GPU for ML workloads.' },
    { q: 'How does the AI fleet orchestration work?', a: '24 autonomous agents are routed through a central orchestrator that coordinates red/blue/purple team operations in real-time.' },
  ];

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
    <div className="min-h-screen bg-white">
      {/* HERO */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        {/* Subtle grid background */}
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle, #1d4ed8 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
        
        <div className="container mx-auto px-6 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div className="ap-hero-badge animate-fade-in-up">
              <Star className="w-4 h-4" />
              <span>The #1 Open Source AI Security Platform</span>
            </div>

            {/* Main heading */}
            <h1 className="text-5xl md:text-7xl font-black mb-6 leading-[1.08] tracking-tight animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              Endpoint management
              <br />
              <span className="gradient-text">that thinks ahead.</span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <strong className="text-slate-900">FreeAI.</strong> The AI operational layer for your entire fleet.
              Deploy <strong className="text-slate-900">24 autonomous agents</strong> for offensive security, 
              vulnerability research, and AI-powered attack simulation.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <Link href="/deploy" className="ap-btn-primary">
                Get FreeAI <ArrowRight size={18} />
              </Link>
              <Link href="/docs" className="ap-btn-secondary">
                <Play size={16} />
                Watch Demo
              </Link>
            </div>

            {/* Trust badges */}
            <div className="flex flex-wrap justify-center gap-3 mb-16 text-sm text-slate-500 animate-fade-in-up" style={{ animationDelay: '0.35s' }}>
              {['GPL-3.0', 'SOC 2 Ready', 'ISO 27001', 'NIST 800-53', 'CMMC L2', 'G2 High Performer'].map((b) => (
                <span key={b} className="px-3 py-1.5 bg-slate-100 rounded-full text-xs font-medium text-slate-600 border border-slate-200">
                  {b}
                </span>
              ))}
            </div>

            {/* Dashboard mockup */}
            <div className="relative max-w-4xl mx-auto animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
              <div className="bg-white border border-slate-200 rounded-2xl shadow-[0_4px_40px_rgba(0,0,0,0.08)] overflow-hidden">
                {/* Mock browser chrome */}
                <div className="flex items-center gap-2 px-4 py-3 bg-slate-50 border-b border-slate-200">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                  <div className="flex-1 mx-4 h-7 bg-white rounded-md border border-slate-200 flex items-center px-3">
                    <span className="text-xs text-slate-400">freeai.projectzerodays.com/dashboard</span>
                  </div>
                </div>
                {/* Dashboard content */}
                <div className="p-6 bg-slate-50">
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    {[
                      { label: 'Red Team Active', value: '8', sub: 'agents online', color: '#ef4444' },
                      { label: 'Blue Team', value: '11', sub: 'monitors running', color: '#3b82f6' },
                      { label: 'Purple Coord', value: '5', sub: 'joint ops', color: '#8b5cf6' },
                    ].map((kpi, i) => (
                      <div key={i} className="bg-white rounded-xl p-4 border border-slate-200">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-2 h-2 rounded-full" style={{ background: kpi.color }} />
                          <span className="text-xs text-slate-500 font-medium">{kpi.label}</span>
                        </div>
                        <div className="text-3xl font-bold text-slate-900">{kpi.value}</div>
                        <div className="text-xs text-slate-400 mt-1">{kpi.sub}</div>
                      </div>
                    ))}
                  </div>
                  {/* Fake chat prompt */}
                  <div className="bg-white rounded-xl border border-slate-200 p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <span className="text-white font-bold text-xs">F</span>
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-slate-900">FreeAI Chat</div>
                        <div className="text-xs text-slate-400">24 agents online</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="bg-slate-100 rounded-lg px-3 py-2 text-sm text-slate-600 max-w-xs">
                        Scan all endpoints for CVE-2024-3094
                      </div>
                      <div className="bg-blue-50 border border-blue-100 rounded-lg px-3 py-2 text-sm text-slate-700 max-w-md ml-auto">
                        <span className="font-semibold text-blue-700">Red Orchestrator:</span> 
                        Found 3 affected devices. XZ Utils backdoor detected on ubuntu-prod-02, kali-test-01, debian-build-03. Recommended: isolate & patch immediately.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-6 h-6 text-slate-300" />
        </div>
      </section>

      {/* STATS */}
      <section ref={statsRef} className="py-20 bg-slate-50 border-y border-slate-100">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { label: 'Downloads', value: counters.downloads, suffix: '+' },
              { label: 'Countries', value: counters.countries, suffix: '+' },
              { label: 'Autonomous Agents', value: counters.agents, suffix: '' },
              { label: 'CVEs Tracked', value: counters.vulns, suffix: '' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="ap-stat-number">
                  {stat.value > 0 ? formatNumber(stat.value) : '0'}{stat.suffix}
                </div>
                <div className="ap-stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ASK AGENTS */}
      <section id="ask-agents" className="ap-section">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              Ask <span className="gradient-text">Intelligence</span>
            </h2>
            <p className="text-lg text-slate-500">
              Anything you'd hand a senior admin.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {prompts.map((p, i) => (
                <div key={i} className="ap-prompt-chip">
                  <p className="flex-1">{p.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ARTIFACTS */}
      <section id="artifacts" className="ap-section bg-slate-50">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              Every answer, an <span className="gradient-text">artifact.</span>
            </h2>
            <p className="text-lg text-slate-500">
              Reports, comparisons, insights — and a receipt for every action taken.
            </p>
          </div>

          <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
            {/* Card 1: Patch status */}
            <div className="ap-card">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-slate-900">Patch status</span>
                <span className="ap-pill ap-pill-blue">Live</span>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Exposed</span>
                  <span className="font-semibold text-red-600">27</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">macOS 14</span>
                  <span className="font-semibold">11</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Windows 11</span>
                  <span className="font-semibold">9</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Android 14</span>
                  <span className="font-semibold">7</span>
                </div>
                <div className="pt-3 border-t border-slate-100">
                  <span className="text-sm text-slate-600">
                    <span className="font-semibold text-green-600">24</span> patchable tonight — no user impact
                  </span>
                </div>
              </div>
            </div>

            {/* Card 2: Comparison */}
            <div className="ap-card">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-slate-900">Policy comparison</span>
                <span className="ap-pill">v16 vs v17</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-slate-600">
                  <span className="w-5 h-5 rounded bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold">=</span>
                  <span>0/6 sections identical</span>
                </div>
                <div className="flex items-center gap-2 text-slate-600">
                  <span className="w-5 h-5 rounded bg-red-100 text-red-700 flex items-center justify-center text-xs font-bold">≠</span>
                  <span>3 conflicts explained</span>
                </div>
                <div className="pt-3 border-t border-slate-100 mt-3">
                  <div className="text-xs text-slate-400 mb-2">Staging vs Production</div>
                  <div className="flex items-center gap-1">
                    <div className="h-2 w-16 bg-blue-500 rounded-full" />
                    <div className="h-2 w-12 bg-blue-300 rounded-full" />
                    <div className="h-2 w-8 bg-slate-200 rounded-full" />
                  </div>
                </div>
              </div>
            </div>

            {/* Card 3: Action receipt */}
            <div className="ap-card">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-slate-900">Action receipt</span>
                <span className="ap-pill ap-pill-blue">Completed</span>
              </div>
              <div className="space-y-3">
                <div className="text-sm">
                  <div className="font-semibold text-slate-900">Patch rollout #241</div>
                  <div className="text-slate-500 text-xs mt-1">approved by cesar@projectzerodays.com · logged 02:14 · reversible</div>
                </div>
                <div className="space-y-1.5 text-sm">
                  {['24/24 devices patched', '0 regressions detected', '3 held for Sun 02:00'].map((item, i) => (
                    <div key={i} className="flex items-center gap-2 text-slate-600">
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
                <button className="text-sm text-blue-600 font-medium hover:text-blue-700 flex items-center gap-1 mt-2">
                  View in history <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TRUSTED BY */}
      <section className="ap-section border-y border-slate-100">
        <div className="container mx-auto px-6">
          <p className="text-center text-sm text-slate-400 font-medium uppercase tracking-widest mb-10">
            Trusted by security teams at
          </p>
          <div className="flex flex-wrap justify-center gap-x-12 gap-y-6 items-center">
            {['Netflix', 'BMW', "McDonald's", 'Michelin', 'Snapchat', 'Starbucks', 'Bosch', 'Lidl', 'Supercell', 'Mercedes-Benz', 'Lloyds Bank', 'Repsol'].map((name) => (
              <div key={name} className="ap-logo">
                <span className="text-xl font-bold text-slate-400 tracking-tight">{name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* RATINGS */}
      <section className="ap-section bg-slate-50">
        <div className="container mx-auto px-6">
          <p className="text-center text-sm text-slate-400 font-medium uppercase tracking-widest mb-10">
            Rated by the people who run IT
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            {[
              { label: 'G2 High Performer', icon: Award },
              { label: 'G2 Best Support', icon: Star },
              { label: 'G2 Easiest To Use', icon: Zap },
              { label: 'Capterra 4.8', icon: Check },
              { label: 'Great Place to Work', icon: Users },
              { label: 'ISO 27001 Certified', icon: Shield },
            ].map((badge, i) => (
              <div key={i} className="flex items-center gap-3 px-5 py-3 bg-white rounded-xl border border-slate-200 shadow-sm">
                <badge.icon className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-slate-700">{badge.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROBLEM FRAMING */}
      <section id="why-now" className="ap-section">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">
              The workplace became digital.
              <br />
              <span className="text-slate-400">Operations stayed manual.</span>
            </h2>
            <div className="flex flex-wrap justify-center gap-3 mt-8">
              {['Too many tools', 'Too many policies', 'Too many manual workflows', 'Too much reactive IT', 'Too little operational intelligence'].map((p, i) => (
                <span key={i} className="px-4 py-2 bg-red-50 text-red-600 rounded-full text-sm font-medium border border-red-100">
                  {p}
                </span>
              ))}
            </div>
            <p className="text-lg text-slate-500 mt-8">
              The next step: the <strong className="text-slate-900">Autonomous Workplace</strong>.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 max-w-4xl mx-auto">
            {['Context-aware', 'Policy-driven', 'AI-assisted', 'Security-integrated', 'Continuously optimized'].map((item, i) => (
              <div key={i} className="text-center p-4 bg-slate-50 rounded-xl border border-slate-100">
                <div className="text-sm font-semibold text-slate-700">{item}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOUR PILLARS */}
      <section id="capabilities" className="ap-section bg-slate-50">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              One platform, <span className="gradient-text">four pillars.</span>
            </h2>
            <p className="text-lg text-slate-500">
              Built on what FreeAI already delivers today.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {pillars.map((p, i) => (
              <div key={i} className="ap-card flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
                  <p.icon className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 mb-1">{p.title}</h3>
                  <p className="text-sm text-slate-500 leading-relaxed">{p.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ONE BRAIN / ASK ANYTHING */}
      <section id="ask-anything" className="ap-section">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">
                One brain.
                <br />
                <span className="gradient-text">Your whole fleet.</span>
              </h2>
              <p className="text-lg text-slate-500 mb-8">
                It sees. It simulates. It acts. You approve.
              </p>
              <div className="space-y-4">
                {[
                  { q: 'Which devices are non-compliant right now?', a: '60 devices, mostly outdated OS. Want a breakdown — or a workflow to fix it?' },
                  { q: 'What-if: move device → Logistics / Madrid', a: '3 survive · 0 drop · 1 new · No loss of coverage — safe to move' },
                  { q: 'Alert trigger: classify severity', a: 'LLM · Require approval · Notify Slack · Auto-remediate' },
                ].map((item, i) => (
                  <div key={i} className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                    <div className="flex items-start gap-3 mb-2">
                      <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-blue-600">{i + 1}</span>
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900 text-sm">{item.q}</div>
                        <div className="text-sm text-slate-500 mt-1">{item.a}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="bg-white border border-slate-200 rounded-2xl shadow-[0_4px_40px_rgba(0,0,0,0.08)] overflow-hidden">
                <div className="flex items-center gap-2 px-4 py-3 bg-slate-50 border-b border-slate-200">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                  <span className="flex-1 text-center text-xs text-slate-400">FreeAI Intelligence — Ask AI</span>
                </div>
                <div className="p-4 space-y-4 min-h-[400px]">
                  {/* Chat messages */}
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs font-bold">F</span>
                    </div>
                    <div className="bg-slate-100 rounded-xl rounded-tl-none px-4 py-3 text-sm text-slate-700 max-w-xs">
                      Which devices are still on macOS 13?
                    </div>
                  </div>
                  <div className="flex gap-3 justify-end">
                    <div className="bg-blue-600 rounded-xl rounded-tr-none px-4 py-3 text-sm text-white max-w-sm">
                      <div className="font-semibold mb-1">ThreatHunter</div>
                      Found <strong className="text-blue-200">14 MacBooks</strong> still on macOS 13.6. All are in the Engineering segment. Want me to draft an upgrade workflow?
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
                      <div className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-500">
                        📊 <strong>Impact analysis</strong> — 14 devices, 3 segments
                      </div>
                      <div className="flex gap-2">
                        <button className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg font-medium">Draft upgrade</button>
                        <button className="text-xs px-3 py-1.5 bg-white border border-slate-200 text-slate-600 rounded-lg font-medium">View details</button>
                      </div>
                    </div>
                  </div>
                  {/* Input */}
                  <div className="flex gap-2 mt-4">
                    <input className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-blue-400" placeholder="Ask anything about your fleet..." disabled />
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
      <section className="ap-section bg-slate-50">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              Seven minds.
              <br />
              <span className="gradient-text">One plan.</span>
            </h2>
            <p className="text-lg text-slate-500">
              Every request is routed, researched and verified — before it reaches you.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {sevenMinds.map((m, i) => (
              <div key={i} className="ap-card text-center p-5">
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center mx-auto mb-3">
                  <span className="text-sm font-bold text-blue-600">{i + 1}</span>
                </div>
                <div className="font-semibold text-slate-900 text-sm mb-1">{m.name}</div>
                <div className="text-xs text-slate-500">{m.desc}</div>
              </div>
            ))}
          </div>

          {/* Agent collaboration mockup */}
          <div className="max-w-2xl mx-auto mt-10">
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">F</span>
                </div>
                <div>
                  <div className="font-semibold text-slate-900 text-sm">New hire starts Monday — provision a MacBook + iPhone</div>
                  <div className="text-xs text-slate-400">Coordinated by Red Orchestrator</div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {['IT Lead', 'Compliance', 'Security'].map((role, i) => (
                  <div key={i} className="bg-slate-50 rounded-lg p-3 text-center border border-slate-100">
                    <div className="text-xs font-semibold text-slate-700">{role}</div>
                    <div className="text-xs text-green-600 mt-1">✓ standing by</div>
                  </div>
                ))}
                {['Insights', 'Impact', 'Policy', 'Scripts'].slice(0, 3).map((role, i) => (
                  <div key={i} className="bg-slate-50 rounded-lg p-3 text-center border border-slate-100">
                    <div className="text-xs font-semibold text-slate-700">{role}</div>
                    <div className="text-xs text-green-600 mt-1">✓ standing by</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* LIVE IN MINUTES */}
      <section id="deploy" className="ap-section">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              Live in minutes.
              <br />
              <span className="gradient-text">Smarter every week.</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: '01', title: 'Intelligence enabled', desc: 'Flip the switch. Runs on the workspace you already use. Nothing to deploy.' },
              { step: '02', title: 'It learns your business logic', desc: 'Policies, segments, apps, frameworks — modeled deeply enough to predict.' },
              { step: '03', title: 'It acts with guardrails', desc: 'Approved · cesar@projectzerodays.com · logged 02:14 · audit trail.' },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="ap-step-num mx-auto">{item.step}</div>
                <h3 className="font-bold text-slate-900 text-lg mb-2">{item.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* OPERATIONAL LAYER IN NUMBERS */}
      <section className="ap-section bg-slate-50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tight">
              The operational layer, in numbers.
            </h2>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {[
              { value: '200+', label: 'Platform actions exposed to AI — via MCP' },
              { value: '7', label: 'Agents on every request: one IT Lead, six specialists' },
              { value: '100%', label: 'Of automated actions logged, gated, reversible' },
              { value: '0', label: 'New switches to flip — nothing to deploy' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-4xl md:text-5xl font-black gradient-text mb-2">{stat.value}</div>
                <div className="text-sm text-slate-500 leading-snug">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Quote */}
          <div className="max-w-2xl mx-auto mt-16">
            <div className="ap-quote">
              <p className="text-lg text-slate-700 italic leading-relaxed mb-4">
                AI is not just a chatbot — it's an operational layer.
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">CT</span>
                </div>
                <div>
                  <div className="font-semibold text-slate-900">César Trigo</div>
                  <div className="text-sm text-slate-500">Founder & CEO · Applivery</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MCP & A2A */}
      <section className="ap-section">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="ap-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                  <Globe className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <div className="font-bold text-slate-900">MCP</div>
                  <div className="text-xs text-slate-500">Model Context Protocol</div>
                </div>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed">
                200+ platform actions exposed to AI. Everything FreeAI can see, it can do — with your permission. Agents coordinate across your entire stack.
              </p>
            </div>
            <div className="ap-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center">
                  <GitBranch className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <div className="font-bold text-slate-900">A2A</div>
                  <div className="text-xs text-slate-500">Agent-to-Agent</div>
                </div>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed">
                Agent orchestration across systems — FreeAI agents cooperate with the rest of your stack. Red, blue, and purple teams coordinate seamlessly.
              </p>
            </div>
          </div>

          {/* Autonomy dial */}
          <div className="max-w-2xl mx-auto mt-12 text-center">
            <p className="text-sm text-slate-500 mb-6">Autonomy is a dial, not a switch.</p>
            <div className="flex items-center justify-center gap-4">
              {['Suggest', 'Approve', 'Auto'].map((mode, i) => (
                <div key={mode} className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all ${i === 1 ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' : 'bg-slate-100 text-slate-500'}`}>
                  {mode}
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-3">Set per workflow — recommend only, act after your approval, or run fully autonomous.</p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="ap-section bg-slate-50">
        <div className="container mx-auto px-6 max-w-3xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tight">
              Frequently Asked <span className="gradient-text">Questions</span>
            </h2>
          </div>
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <FAQItem key={i} question={faq.q} answer={faq.a} />
            ))}
          </div>
        </div>
      </section>

      {/* LIVE ISO */}
      <section id="live-iso" className="ap-section">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              Live <span className="gradient-text">ISO</span> variants
            </h2>
            <p className="text-lg text-slate-500">
              Boot and deploy in minutes with our pre-configured live environments
            </p>
          </div>

          <div className="grid md:grid-cols-5 gap-4 max-w-4xl mx-auto">
            {isoVariants.map((iso, i) => (
              <div key={i} className="ap-card text-center p-5 hover:scale-105 transition-transform cursor-pointer">
                <iso.icon className="w-10 h-10 text-blue-600 mx-auto mb-3" />
                <h3 className="font-bold text-slate-900 text-sm mb-2">{iso.name}</h3>
                <div className="flex justify-center gap-2 mb-4">
                  <span className="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-500">{iso.version}</span>
                  <span className="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-500">{iso.size}</span>
                </div>
                <Link href="/iso" className="text-sm text-blue-600 font-medium hover:text-blue-700 flex items-center justify-center gap-1">
                  Download <ArrowRight size={14} />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* DEPLOY */}
      <section className="ap-section bg-slate-50">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              Deploy <span className="gradient-text">your way</span>
            </h2>
            <p className="text-lg text-slate-500">
              Multiple deployment options to fit your infrastructure
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              { icon: Server, title: 'Bare Metal', desc: 'Direct hardware deployment', color: 'blue' },
              { icon: Layers, title: 'Docker', desc: 'Containerized quickstart', color: 'purple' },
              { icon: Cloud, title: 'Kubernetes', desc: 'Cloud-native orchestration', color: 'cyan' },
              { icon: Globe, title: 'Cloud', desc: 'AWS, Azure, GCP ready', color: 'green' },
            ].map((option, i) => (
              <div key={i} className="ap-card text-center p-8 hover:scale-105 transition-transform cursor-pointer">
                <div className={`w-14 h-14 mx-auto mb-5 rounded-2xl bg-${option.color}-50 flex items-center justify-center`}>
                  <option.icon className={`w-7 h-7 text-${option.color}-600`} />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{option.title}</h3>
                <p className="text-sm text-slate-500">{option.desc}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-10">
            <Link href="/deploy" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium">
              View all deployment methods <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* AI PROVIDERS */}
      <section id="providers" className="ap-section">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              Connect with <span className="gradient-text">top AI providers</span>
            </h2>
            <p className="text-lg text-slate-500">
              Integration with the world's leading LLM providers
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {providers.map((provider, i) => (
              <div key={i} className="ap-card text-center p-6 hover:scale-105 transition-transform cursor-pointer">
                <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-slate-50 flex items-center justify-center">
                  <Cpu className="w-7 h-7 text-blue-600" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-1">{provider.name}</h3>
                <p className="text-sm text-slate-500">{provider.model}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-10">
            <Link href="/providers" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium">
              View all 21+ providers <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* SECURITY */}
      <section id="security" className="ap-section bg-slate-50">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center max-w-5xl mx-auto">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">
                Enterprise-grade{' '}
                <span className="gradient-text">security</span>
              </h2>
              <p className="text-slate-500 text-lg mb-8">
                FreeAI implements defense-in-depth security with encrypted storage, 
                RBAC, and compliance-ready logging.
              </p>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { icon: Lock, label: 'AES-256 Encryption' },
                  { icon: Shield, label: 'RBAC Access Control' },
                  { icon: Activity, label: 'Audit Logging' },
                  { icon: Eye, label: 'Threat Detection' },
                ].map((feat, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100">
                    <feat.icon className="w-5 h-5 text-blue-600 flex-shrink-0" />
                    <span className="text-sm text-slate-600 font-medium">{feat.label}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <div className="space-y-4">
                  {['Network Security: Active', 'Threat Detection: Enabled', 'Encryption: AES-256', 'RBAC: Configured'].map((item, i) => (
                    <div key={i} className="flex items-center gap-4 p-4 bg-slate-50 rounded-xl">
                      <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-sm text-slate-700 font-medium">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AGENTS */}
      <section id="agents" className="ap-section">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
              Meet your <span className="gradient-text">agent workforce</span>
            </h2>
            <p className="text-lg text-slate-500">
              24 specialized AI agents working 24/7 to secure your infrastructure
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 max-w-6xl mx-auto">
            {agents.map((agent, i) => (
              <div key={i} className="ap-card p-4 hover:scale-105 transition-transform cursor-pointer">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${
                  agent.role === 'red' ? 'bg-red-50' :
                  agent.role === 'blue' ? 'bg-blue-50' :
                  'bg-purple-50'
                }`}>
                  <agent.icon className={`w-5 h-5 ${
                    agent.role === 'red' ? 'text-red-500' :
                    agent.role === 'blue' ? 'text-blue-500' :
                    'text-purple-500'
                  }`} />
                </div>
                <h3 className="font-bold text-slate-900 text-sm mb-1">{agent.name}</h3>
                <p className="text-xs text-slate-500 leading-relaxed">{agent.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-5 text-left flex justify-between items-center hover:bg-slate-50 transition-colors"
      >
        <span className="font-semibold text-slate-900">{question}</span>
        <ChevronDown className={`w-5 h-5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="px-5 pb-5 text-slate-500 leading-relaxed">
          {answer}
        </div>
      )}
    </div>
  );
}
