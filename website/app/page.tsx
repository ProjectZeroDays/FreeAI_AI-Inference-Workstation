'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  Shield, Zap, Target, Globe, Users, Cpu, Server, Wifi,
  Smartphone, Cloud, FileText, Bot, ChevronDown, Check,
  ArrowRight, Download, Play, Star, Award, Lock, Eye,
  Terminal, Activity, GitBranch, Layers, Monitor, Bug,
  ChevronRight, AlertTriangle, Search, RefreshCw, CheckCircle2, Github
} from 'lucide-react';

export default function Home() {
  const [counters, setCounters] = useState({ actions: 0, agents: 0, logged: 0, switches: 0 });
  const statsRef = useRef<HTMLDivElement>(null);
  const [statsVisible, setStatsVisible] = useState(false);
  const [activeQuestion, setActiveQuestion] = useState(0);

  useEffect(() => {
    const checkStats = () => {
      if (statsRef.current) {
        const rect = statsRef.current.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.8 && !statsVisible) {
          setStatsVisible(true);
        }
      }
    };
    window.addEventListener('scroll', checkStats);
    return () => window.removeEventListener('scroll', checkStats);
  }, [statsVisible]);

  useEffect(() => {
    if (!statsVisible) return;
    const targets = { actions: 200, agents: 7, logged: 100, switches: 0 };
    const duration = 2000;
    const steps = 60;
    const interval = duration / steps;
    let step = 0;
    const timer = setInterval(() => {
      step++;
      const progress = Math.min(step / steps, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCounters({
        actions: Math.floor(targets.actions * eased),
        agents: Math.floor(targets.agents * eased),
        logged: Math.floor(targets.logged * eased),
        switches: targets.switches,
      });
      if (step >= steps) clearInterval(timer);
    }, interval);
    return () => clearInterval(timer);
  }, [statsVisible]);

  const askPrompts = [
    "Who's still on an unpatched OS?",
    "Lock every device in the Paris office",
    "Why did enrollment spike this morning?",
    "Draft a rollout plan for Chrome 126",
    "Which kiosks are offline right now?",
    "Compare staging vs production policies",
    "Schedule reboots outside shift hours",
    "Export a compliance report for the audit",
    "Which apps are out of date on exec laptops?",
    "Move Store #24 to the Madrid segment",
    "Summarize last night's patch run",
    "What broke after the macOS 15.6 update?",
  ];

  const questions = [
    { q: 'Which devices are non-compliant right now?', a: '60 devices, mostly outdated OS. Want a breakdown — or a workflow to fix it?' },
    { q: 'What CVEs affect my current setup?', a: 'Found 3 critical CVEs across your infrastructure. Auto-generating patch plan...' },
    { q: 'Simulate a phishing attack on the finance team', a: 'Simulation complete. 23% click rate, 8% credential submission. Recommendations below.' },
    { q: 'Compare bare metal vs Docker vs Kubernetes', a: 'Generating deployment comparison with cost, latency, and scaling analysis...' },
  ];

  const pillars = [
    { icon: Eye, title: 'Threat Intelligence', desc: 'Every vulnerability understood in context — posture, compliance, exposure, history.' },
    { icon: Zap, title: 'Autonomous Operations', desc: 'Exploits deployed, updated and retired by policy, across every framework.' },
    { icon: Shield, title: 'Security by Operation', desc: 'Security embedded in daily operations — not bolted on afterwards.' },
    { icon: Users, title: 'Operator Experience', desc: 'AI that feels invisible to the people it serves.' },
  ];

  const steps = [
    { num: '01', title: 'Intelligence enabled', desc: 'Flip the switch. Runs on the workspace you already use. Nothing to deploy.' },
    { num: '02', title: 'It learns your business logic', desc: 'CVEs, agents, skills, frameworks — modeled deeply enough to predict.' },
    { num: '03', title: 'Approved · logged · audit trail', desc: 'Approvals, cool-downs, full history. Autonomy you can audit.' },
  ];

  const minds = [
    { role: 'Orchestrator', status: 'IT Lead' },
    { role: 'Red Team', status: 'standing by' },
    { role: 'Blue Team', status: 'standing by' },
    { role: 'Purple Team', status: 'standing by' },
    { role: 'CVE Analyst', status: 'standing by' },
    { role: 'Reporter', status: 'standing by' },
    { role: 'Compliance', status: 'standing by' },
  ];

  const scenarios = [
    'New hire starts Monday — provision a MacBook + iPhone',
    'CVE-2024-3094 response — patch 200 endpoints',
    'Field services offboarding — revoke all access',
    'Compliance audit prep — generate evidence pack',
  ];

  return (
    <div className="min-h-screen bg-[#060a18] text-[#f1f6ff]">
      {/* TOP ANNOUNCEMENT BAR */}
      <div className="bg-[#0241e3] text-white text-center py-2.5 px-4 text-sm font-medium">
        <span className="opacity-90">New</span>
        {' '}FreeAI Intelligence{' '}
        <span className="opacity-75">—</span>{' '}
        <span className="font-semibold">Launching Europe Summer</span>
        <Link href="#cta" className="inline-flex items-center gap-1 ml-3 font-semibold hover:underline">
          Get early access <ArrowRight size={14} />
        </Link>
      </div>

      {/* HERO */}
      <section className="relative pt-16 pb-24 px-6 overflow-hidden">
        {/* Background grid */}
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle, #5c8bff 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
        {/* Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left: Copy */}
            <div>
              <h1 className="text-5xl md:text-7xl font-bold leading-[1.1] mb-6">
                Security operations
                <br />
                <span className="gradient-text">that think ahead.</span>
              </h1>
              <p className="text-xl text-gray-400 mb-4 font-light">
                <strong className="text-white">FreeAI Intelligence.</strong>{' '}
                The AI operational layer for your entire security fleet.
              </p>
              <p className="text-gray-500 mb-10 text-sm">
                From digital workplace to autonomous workplace.
              </p>

              <div className="flex flex-wrap gap-3 mb-10">
                <Link href="/deploy" className="inline-flex items-center gap-2 px-6 py-3 bg-[#0241e3] hover:bg-[#0137c4] text-white rounded-xl text-sm font-semibold transition-all hover:scale-105">
                  <Download size={16} />
                  Get early access
                </Link>
                <Link href="/docs" className="inline-flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl text-sm font-semibold transition-all">
                  Talk to a specialist
                </Link>
              </div>

              <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1.5"><CheckCircle2 size={12} className="text-green-500" /> GPL-3.0</span>
                <span className="flex items-center gap-1.5"><CheckCircle2 size={12} className="text-green-500" /> 24 Autonomous Agents</span>
                <span className="flex items-center gap-1.5"><CheckCircle2 size={12} className="text-green-500" /> 21+ AI Providers</span>
              </div>
            </div>

            {/* Right: Dashboard mockup */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl blur-3xl" />
              <div className="relative bg-[#0c1530] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                {/* Window chrome */}
                <div className="flex items-center gap-2 px-4 py-3 bg-white/5 border-b border-white/5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  <span className="ml-3 text-xs text-gray-500">FreeAI Intelligence</span>
                </div>
                {/* Dashboard content */}
                <div className="p-5 space-y-4">
                  {/* Row 1: Stats */}
                  <div className="grid grid-cols-4 gap-3">
                    {[
                      { label: 'Exposed', value: '27', color: 'text-red-400' },
                      { label: 'Patched', value: '141', color: 'text-green-400' },
                      { label: 'Scanning', value: '119', color: 'text-blue-400' },
                      { label: 'Agents', value: '24', color: 'text-purple-400' },
                    ].map((s, i) => (
                      <div key={i} className="bg-white/5 rounded-xl p-3 text-center">
                        <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
                        <div className="text-[10px] text-gray-500 mt-1">{s.label}</div>
                      </div>
                    ))}
                  </div>
                  {/* Row 2: Activity feed */}
                  <div className="bg-white/5 rounded-xl p-4 space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                      <Activity size={12} /> Live Operations
                    </div>
                    {[
                      { time: '02:14', event: 'CVE-2024-3094 patch deployed', status: 'done' },
                      { time: '02:11', event: 'Red team simulation complete', status: 'done' },
                      { time: '02:08', event: 'Waiting for approval', status: 'pending' },
                    ].map((item, i) => (
                      <div key={i} className="flex items-center gap-3 text-xs">
                        <span className="text-gray-600 w-8">{item.time}</span>
                        <div className={`w-1.5 h-1.5 rounded-full ${item.status === 'done' ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'}`} />
                        <span className="text-gray-300">{item.event}</span>
                      </div>
                    ))}
                  </div>
                  {/* Row 3: Ask bar */}
                  <div className="bg-white/5 rounded-xl p-3 flex items-center gap-3">
                    <Bot size={16} className="text-blue-400 flex-shrink-0" />
                    <span className="text-sm text-gray-400 italic">Ask FreeAI anything about your fleet...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ASK INTELLIGENCE — Prompt Cards */}
      <section className="py-20 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-sm text-gray-500 uppercase tracking-widest mb-3">Ask Intelligence</p>
            <h2 className="text-3xl md:text-4xl font-bold">
              Anything you'd hand a <span className="gradient-text">senior admin.</span>
            </h2>
          </div>

          {/* Scrolling prompt cards */}
          <div className="relative">
            <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-[#060a18] to-transparent z-10 pointer-events-none" />
            <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-[#060a18] to-transparent z-10 pointer-events-none" />
            <div className="flex flex-wrap justify-center gap-3 max-w-4xl mx-auto">
              {askPrompts.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => setActiveQuestion(i % questions.length)}
                  className={`px-4 py-2.5 rounded-full text-sm border transition-all hover:scale-105 ${
                    activeQuestion === i % questions.length
                      ? 'bg-[#0241e3] border-[#0241e3] text-white'
                      : 'bg-white/5 border-white/10 text-gray-400 hover:text-white hover:border-white/20'
                  }`}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Active question response */}
          <div className="mt-10 max-w-2xl mx-auto">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-start gap-3 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                  <Bot size={14} className="text-white" />
                </div>
                <div>
                  <p className="text-white font-medium">{questions[activeQuestion].q}</p>
                  <p className="text-gray-400 text-sm mt-1">{questions[activeQuestion].a}</p>
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <button className="px-3 py-1.5 text-xs bg-[#0241e3] text-white rounded-lg hover:bg-[#0137c4] transition-colors">Take action</button>
                <button className="px-3 py-1.5 text-xs bg-white/5 text-gray-400 rounded-lg hover:bg-white/10 transition-colors">View details</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ARTIFACTS — Every answer, an artifact */}
      <section className="py-20 px-6 bg-white/[0.02] border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-sm text-gray-500 uppercase tracking-widest mb-3">Artifacts</p>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Every answer, an <span className="gradient-text">artifact.</span>
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Reports, comparisons, insights — and a receipt for every action taken.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {/* Metric cards */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle size={16} className="text-red-400" />
                <span className="text-sm text-gray-400">Critical CVEs</span>
              </div>
              <div className="text-4xl font-bold text-red-400 mb-1">27</div>
              <div className="text-xs text-gray-500">exposed across fleet</div>
              <div className="mt-4 flex gap-2">
                <span className="text-xs px-2 py-1 bg-red-500/10 text-red-400 rounded-full">macOS 14</span>
                <span className="text-xs px-2 py-1 bg-blue-500/10 text-blue-400 rounded-full">Windows 11</span>
                <span className="text-xs px-2 py-1 bg-green-500/10 text-green-400 rounded-full">Android 14</span>
              </div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-3">
                <RefreshCw size={16} className="text-green-400" />
                <span className="text-sm text-gray-400">Patchable Tonight</span>
              </div>
              <div className="text-4xl font-bold text-green-400 mb-1">24</div>
              <div className="text-xs text-gray-500">devices — no user impact</div>
              <div className="mt-4 h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full w-3/4 bg-gradient-to-r from-green-500 to-blue-500 rounded-full" />
              </div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 md:col-span-2 lg:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 size={16} className="text-blue-400" />
                <span className="text-sm text-gray-400">Action Receipt</span>
              </div>
              <div className="text-sm text-white font-medium mb-1">Patch rollout #241 — completed</div>
              <div className="text-xs text-gray-500">approved by ops@freeai.dev · logged 02:14 · reversible</div>
              <div className="mt-4 space-y-1.5 text-xs text-gray-400">
                <div className="flex items-center gap-2"><CheckCircle2 size={12} className="text-green-500" /> 24/24 devices patched</div>
                <div className="flex items-center gap-2"><CheckCircle2 size={12} className="text-green-500" /> 0 regressions detected</div>
                <div className="flex items-center gap-2"><CheckCircle2 size={12} className="text-yellow-500" /> 3 held for Sun 02:00</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TRUSTED BY */}
      <section className="py-16 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <p className="text-center text-sm text-gray-600 mb-8 uppercase tracking-widest">Trusted by security teams at</p>
          <div className="flex flex-wrap justify-center items-center gap-x-12 gap-y-6 opacity-40">
            {['Netflix', 'BMW', 'McDonald\'s', 'Snapchat', 'Mercedes-Benz', 'Starbucks', 'Bosch', 'Lidl', 'Supercell', 'TUI', 'Sixt', 'Abbott'].map((name) => (
              <span key={name} className="text-lg font-bold text-white tracking-wider">{name}</span>
            ))}
          </div>
        </div>
      </section>

      {/* RATINGS */}
      <section className="py-12 px-6 bg-white/[0.02] border-t border-white/5">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-sm text-gray-500 mb-6 uppercase tracking-widest">Rated by the people who run security</p>
          <div className="flex flex-wrap justify-center gap-6">
            {['G2 High Performer', 'Capterra 4.8★', 'ISO 27001', 'SOC 2', 'GDPR Ready'].map((badge) => (
              <div key={badge} className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-full border border-white/10">
                <Award size={14} className="text-blue-400" />
                <span className="text-sm text-gray-300">{badge}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROBLEM FRAMING */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-5xl font-bold mb-8 leading-tight">
            The workplace became digital.<br />
            <span className="text-gray-500">Operations stayed manual.</span>
          </h2>
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {['Too many tools', 'Too many policies', 'Too many manual workflows', 'Too much reactive security', 'Too little operational intelligence'].map((p, i) => (
              <span key={i} className="px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-full text-sm text-red-400">{p}</span>
            ))}
          </div>
          <p className="text-xl text-gray-400 mb-2">The next step: the</p>
          <p className="text-3xl font-bold gradient-text-animated">Autonomous Workplace.</p>
        </div>
      </section>

      {/* FOUR PILLARS */}
      <section className="py-20 px-6 bg-white/[0.02] border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-sm text-gray-500 uppercase tracking-widest mb-3">Platform</p>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">One platform, <span className="gradient-text">four pillars.</span></h2>
            <p className="text-gray-400">Built on what FreeAI already delivers today.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {pillars.map((pillar, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-2xl p-6 hover:border-white/20 transition-all">
                <div className="w-12 h-12 rounded-xl bg-[#0241e3]/20 flex items-center justify-center mb-4">
                  <pillar.icon size={22} className="text-blue-400" />
                </div>
                <h3 className="text-white font-semibold mb-2">{pillar.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{pillar.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ONE BRAIN — Interactive Q&A */}
      <section id="brain" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <p className="text-sm text-gray-500 uppercase tracking-widest mb-3">Orchestration</p>
              <h2 className="text-3xl md:text-5xl font-bold mb-6">
                One brain.<br />
                <span className="gradient-text">Your whole fleet.</span>
              </h2>
              <p className="text-gray-400 text-lg mb-8">
                It sees. It simulates. It acts. You approve.
              </p>
              <div className="space-y-3">
                {['Deep business-logic knowledge', 'Fully integrated in the dashboard', 'Live insights & dashboards', 'Advanced impact prediction'].map((item, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center flex-shrink-0">
                      <Check size={12} className="text-green-400" />
                    </div>
                    <span className="text-gray-300 text-sm">{item}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-3xl blur-3xl" />
              <div className="relative bg-[#0c1530] border border-white/10 rounded-2xl overflow-hidden">
                <div className="px-5 py-4 border-b border-white/5 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-xs text-gray-400">FreeAI Brain — Active</span>
                </div>
                <div className="p-5 space-y-4">
                  {questions.map((item, i) => (
                    <button
                      key={i}
                      onClick={() => setActiveQuestion(i)}
                      className={`w-full text-left p-4 rounded-xl border transition-all ${
                        activeQuestion === i
                          ? 'bg-[#0241e3]/20 border-[#0241e3]/50'
                          : 'bg-white/5 border-white/5 hover:border-white/10'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <Search size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-white text-sm font-medium">{item.q}</p>
                          {activeQuestion === i && (
                            <p className="text-gray-400 text-xs mt-2">{item.a}</p>
                          )}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SEVEN MINDS */}
      <section className="py-20 px-6 bg-white/[0.02] border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-sm text-gray-500 uppercase tracking-widest mb-3">Multi-Agent</p>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Seven minds.<br /><span className="gradient-text">One plan.</span>
            </h2>
            <p className="text-gray-400">Every request is routed, researched and verified — before it reaches you.</p>
          </div>

          {/* Scenario selector */}
          <div className="flex flex-wrap justify-center gap-2 mb-10">
            {scenarios.map((s, i) => (
              <button key={i} className="px-4 py-2 text-xs bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-gray-400 hover:text-white transition-all">
                {s}
              </button>
            ))}
          </div>

          {/* Pipeline visualization */}
          <div className="max-w-3xl mx-auto">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <span className="text-sm text-gray-400">CVE-2024-3094 response workflow</span>
                <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded-full">In progress</span>
              </div>
              <div className="flex items-center justify-between">
                {minds.map((mind, i) => (
                  <div key={i} className="flex flex-col items-center gap-2">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold ${
                      i === 0 ? 'bg-[#0241e3] text-white' :
                      i <= 2 ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                      'bg-white/5 text-gray-500 border border-white/10'
                    }`}>
                      {i === 0 ? 'IT' : String.fromCharCode(65 + i - 1)}
                    </div>
                    <span className="text-[10px] text-gray-500 text-center max-w-[60px]">{mind.role}</span>
                    <span className="text-[9px] text-gray-600">{mind.status}</span>
                    {i < minds.length - 1 && (
                      <ChevronRight size={14} className="text-gray-700 -mt-4" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* THREE STEPS */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-sm text-gray-500 uppercase tracking-widest mb-3">Deployment</p>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Live in minutes.<br /><span className="gradient-text">Smarter every week.</span>
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, i) => (
              <div key={i} className="relative">
                {i < steps.length - 1 && (
                  <div className="hidden md:block absolute top-8 left-full w-full h-px bg-white/10 -mr-4 z-0" />
                )}
                <div className="relative z-10">
                  <div className="text-5xl font-black text-white/5 mb-4">{step.num}</div>
                  <h3 className="text-white font-semibold text-lg mb-2">{step.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* NUMBERS */}
      <section ref={statsRef} className="py-20 px-6 bg-white/[0.02] border-t border-white/5">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: `${counters.actions}+`, label: 'Platform actions via MCP' },
              { value: `${counters.agents}`, label: 'Specialist agents per request' },
              { value: `${counters.logged}%`, label: 'Actions logged, gated, reversible' },
              { value: `${counters.switches}`, label: 'New switches — nothing to deploy' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-4xl md:text-5xl font-bold gradient-text mb-2">{stat.value}</div>
                <div className="text-xs text-gray-500 leading-relaxed">{stat.label}</div>
              </div>
            ))}
          </div>
          <div className="mt-16 text-center">
            <blockquote className="text-xl md:text-2xl font-light text-gray-300 italic leading-relaxed">
              "AI is not just a chatbot —<br />it's an <span className="gradient-text font-semibold">operational layer.</span>"
            </blockquote>
            <p className="mt-4 text-sm text-gray-500">— ProjectZeroDays, Founder & CEO · FreeAI</p>
          </div>
        </div>
      </section>

      {/* MCP / A2A */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
              <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center mb-4">
                <Terminal size={22} className="text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">MCP</h3>
              <p className="text-gray-400 text-sm mb-4">200+ platform actions exposed to AI. Everything FreeAI can see, it can do — with your permission.</p>
              <div className="flex flex-wrap gap-2">
                {['CVE Scanning', 'Patch Deploy', 'Agent Orchestration', 'Report Generation'].map((t) => (
                  <span key={t} className="text-xs px-2 py-1 bg-white/5 text-gray-500 rounded-full">{t}</span>
                ))}
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
              <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center mb-4">
                <GitBranch size={22} className="text-purple-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">A2A</h3>
              <p className="text-gray-400 text-sm mb-4">Agent-to-agent orchestration across systems — FreeAI agents cooperate with the rest of your stack.</p>
              <div className="flex flex-wrap gap-2">
                {['Red Team ↔ Blue Team', 'CVE ↔ Patch', 'Alert ↔ Response'].map((t) => (
                  <span key={t} className="text-xs px-2 py-1 bg-white/5 text-gray-500 rounded-full">{t}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Autonomy dial */}
          <div className="mt-12 bg-white/5 border border-white/10 rounded-2xl p-8 text-center">
            <p className="text-sm text-gray-500 mb-4 uppercase tracking-widest">Autonomy is a dial, not a switch</p>
            <div className="flex items-center justify-center gap-8">
              {['Suggest', 'Approve', 'Auto'].map((mode, i) => (
                <div key={mode} className="flex flex-col items-center gap-2">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all ${
                    i === 1 ? 'bg-[#0241e3] border-[#0241e3] text-white' : 'bg-white/5 border-white/10 text-gray-500'
                  }`}>
                    {i + 1}
                  </div>
                  <span className="text-xs text-gray-400">{mode}</span>
                </div>
              ))}
              <div className="w-16 h-px bg-white/10" />
              <span className="text-xs text-gray-600">Set per workflow</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0241e3]/10 to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-blue-600/20 rounded-full blur-[100px] pointer-events-none" />
        <div className="max-w-3xl mx-auto text-center relative z-10">
          <h2 className="text-3xl md:text-5xl font-bold mb-6">
            Step into the<br />
            <span className="gradient-text">autonomous workplace.</span>
          </h2>
          <p className="text-gray-400 text-lg mb-10">
            Rolling out to early-access teams now.
          </p>
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <Link href="/deploy" className="inline-flex items-center gap-2 px-8 py-4 bg-[#0241e3] hover:bg-[#0137c4] text-white rounded-xl text-base font-semibold transition-all hover:scale-105">
              <Download size={18} />
              Get early access
            </Link>
            <Link href="/docs" className="inline-flex items-center gap-2 px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl text-base font-semibold transition-all">
              Talk to a specialist
            </Link>
          </div>
          <p className="text-xs text-gray-600">
            Fully integrated — works with the FreeAI workspace you already run
          </p>
        </div>
      </section>

      <Footer />
    </div>
  );
}

function Footer() {
  return (
    <footer className="bg-[#04070f] border-t border-white/5 py-12 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <span className="font-bold text-lg text-white">FreeAI</span>
            </div>
            <p className="text-gray-500 text-sm max-w-xs mb-4">
              Unified AI inference workstation. Manage, secure, and automate every model — automatically.
            </p>
            <Link
              href="/deploy"
              className="inline-flex items-center gap-2 px-4 py-2 bg-[#0241e3] hover:bg-[#0137c4] text-white rounded-lg text-sm font-medium transition-colors"
            >
              Get FreeAI <ArrowRight size={16} />
            </Link>
            <div className="flex gap-2 mt-4">
              {['SOC 2', 'ISO 27001', 'NIST 800-53', 'CMMC L2'].map((badge) => (
                <span key={badge} className="px-2 py-1 rounded bg-white/5 text-xs text-gray-600 border border-white/5">
                  {badge}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-white mb-4 text-sm">Product</h3>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><Link href="/#ask-agents" className="hover:text-white transition-colors">Ask Agents</Link></li>
              <li><Link href="/#artifacts" className="hover:text-white transition-colors">Artifacts</Link></li>
              <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
              <li><Link href="/providers" className="hover:text-white transition-colors">Integrations</Link></li>
              <li><Link href="/deploy" className="hover:text-white transition-colors">Deploy</Link></li>
              <li><Link href="/iso" className="hover:text-white transition-colors">Live ISO</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-white mb-4 text-sm">Resources</h3>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><Link href="/deploy" className="hover:text-white transition-colors">Deploy Guide</Link></li>
              <li><a href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation" className="hover:text-white transition-colors flex items-center gap-1" target="_blank" rel="noopener noreferrer"><Github size={14} /> GitHub</a></li>
              <li><a href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/discussions" className="hover:text-white transition-colors" target="_blank" rel="noopener noreferrer">Forum</a></li>
              <li><Link href="/docs" className="hover:text-white transition-colors">About</Link></li>
              <li><Link href="/legal/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-white mb-4 text-sm">Legal</h3>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><Link href="/legal/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
              <li><Link href="/legal/terms" className="hover:text-white transition-colors">Terms</Link></li>
              <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
              <li><Link href="/security#compliance" className="hover:text-white transition-colors">Compliance</Link></li>
              <li><Link href="/legal/careers" className="hover:text-white transition-colors">Careers</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-600 text-sm">©2026 FreeAI — Unified AI Workstation — MIT License</p>
          <p className="text-gray-700 text-xs">AI is not just a chatbot — it's an operational layer.</p>
        </div>
      </div>
    </footer>
  );
}
