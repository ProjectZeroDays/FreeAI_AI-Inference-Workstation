'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  Shield, Zap, Target, Globe, Users, Cpu, Server, Wifi,
  Smartphone, Cloud, FileText, Bot, ChevronDown, Check,
  ArrowRight, Download, Play, Star, Award, Lock, Eye,
  Terminal, Activity, GitBranch, Layers, Monitor, Bug
} from 'lucide-react';

export default function Home() {
  const [scrollY, setScrollY] = useState(0);
  const [activeSection, setActiveSection] = useState('hero');
  const [counters, setCounters] = useState({ downloads: 0, agents: 0, countries: 0, vulns: 0 });
  const statsRef = useRef<HTMLDivElement>(null);
  const [statsVisible, setStatsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
      
      const sections = ['hero', 'what-is', 'agents', 'providers', 'brain', 'iso', 'deploy', 'security', 'faq'];
      for (const section of sections) {
        const el = document.getElementById(section);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 200 && rect.bottom >= 200) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    const checkStats = () => {
      if (statsRef.current) {
        const rect = statsRef.current.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.8 && !statsVisible) {
          setStatsVisible(true);
          animateCounters();
        }
      }
    };

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

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('scroll', checkStats);
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('scroll', checkStats);
    };
  }, [statsVisible]);

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(0) + 'K';
    return num.toString();
  };

  const agents = [
    // RED TEAM
    { name: 'Red Orchestrator', role: 'red', icon: Target, description: 'Autonomous red team coordination' },
    { name: 'PhishingSimulator', role: 'red', icon: Eye, description: 'Enterprise phishing simulations' },
    { name: 'CredsHarvester', role: 'red', icon: Bot, description: 'Credential harvesting operations' },
    { name: 'LlmAdversarial', role: 'red', icon: Terminal, description: 'LLM prompt injection attacks' },
    { name: 'WifiRogue', role: 'red', icon: Wifi, description: 'WiFi deauth & rogue AP attacks' },
    { name: 'WifiJamming', role: 'red', icon: Wifi, description: 'Wireless jamming operations' },
    { name: 'ExploitDev', role: 'red', icon: Shield, description: 'Custom exploit development' },
    { name: 'ZeroClickFinder', role: 'red', icon: Zap, description: 'Zero-click vulnerability hunting' },
    { name: 'VulnAssessor', role: 'red', icon: Activity, description: 'Vulnerability assessment engine' },
    { name: 'NetworkScanner', role: 'red', icon: Globe, description: 'Full network reconnaissance' },
    { name: 'SocialEngineer', role: 'red', icon: Users, description: 'Social engineering campaigns' },
    { name: 'WebAppScanner', role: 'red', icon: Cloud, description: 'Web application pentesting' },
    
    // BLUE TEAM
    { name: 'Blue Orchestrator', role: 'blue', icon: Shield, description: 'Defensive operations coordination' },
    { name: 'ThreatHunter', role: 'blue', icon: Eye, description: 'Proactive threat hunting' },
    { name: 'IocAnalyzer', role: 'blue', icon: Activity, description: 'IOC pattern analysis' },
    { name: 'MalwareAnalyzer', role: 'blue', icon: Bug, description: 'Malware behavior analysis' },
    { name: 'ForensicAnalyst', role: 'blue', icon: FileText, description: 'Digital forensics investigations' },
    { name: 'IncidentResponder', role: 'blue', icon: Zap, description: 'Automated incident response' },
    { name: 'NetworkDefender', role: 'blue', icon: Globe, description: 'Network defense operations' },
    { name: 'LogAnalyzer', role: 'blue', icon: Terminal, description: 'SIEM log correlation' },
    { name: 'DeceptionEngine', role: 'blue', icon: Eye, description: 'Honeypot & canary deployment' },
    
    // PURPLE TEAM
    { name: 'Purple Orchestrator', role: 'purple', icon: GitBranch, description: 'Purple team collaboration' },
    { name: 'AttackSimulation', role: 'purple', icon: Target, description: 'ATT&CK-based simulations' },
    { name: 'DefenseValidation', role: 'purple', icon: Shield, description: 'Control validation engine' },
    { name: 'RemediationBot', role: 'purple', icon: Zap, description: 'Auto-remediation workflows' },
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
  ];

  const providers = [
    { name: 'Meta', model: 'Llama 3.1' },
    { name: 'OpenAI', model: 'GPT-4o' },
    { name: 'Anthropic', model: 'Claude 3.5' },
    { name: 'Google', model: 'Gemini 1.5' },
    { name: 'Mistral', model: 'Mistral Large' },
    { name: 'Cohere', model: 'Command R+' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-navy-800 to-blue-900">
      {/* HERO SECTION */}
      <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
        {/* Animated background shapes */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="hero-shape w-96 h-96 bg-blue-500/20 top-20 -left-20 animate-float" />
          <div className="hero-shape w-64 h-64 bg-purple-500/20 top-40 right-20 animate-float-reverse" />
          <div className="hero-shape w-48 h-48 bg-cyan-500/20 bottom-40 left-1/4 animate-pulse-glow" />
          <div className="hero-shape w-32 h-32 bg-indigo-500/30 bottom-20 right-1/3 animate-float" />
        </div>

        <div className="container mx-auto px-6 relative z-10">
          <div className="text-center max-w-5xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 mb-8 animate-float-up">
              <Star className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-medium">The #1 Open Source AI Security Platform</span>
            </div>

            {/* Main heading */}
            <h1 className="text-5xl md:text-7xl font-black mb-6 leading-tight animate-float-up" style={{ animationDelay: '0.1s' }}>
              Your Cybersecurity
              <br />
              <span className="gradient-text-animated">Workforce</span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto animate-float-up" style={{ animationDelay: '0.2s' }}>
              Deploy <strong className="text-white">24 autonomous agents</strong> for offensive security, 
              vulnerability research, and AI-powered attack simulation.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-float-up" style={{ animationDelay: '0.3s' }}>
              <Link href="/deploy" className="btn-primary px-8 py-4 rounded-xl text-lg font-semibold flex items-center justify-center gap-2">
                <Download className="w-5 h-5" />
                Download FreeAI
              </Link>
              <Link href="/docs" className="px-8 py-4 rounded-xl text-lg font-semibold border border-white/20 hover:bg-white/10 transition-all flex items-center justify-center gap-2">
                <Play className="w-5 h-5" />
                Watch Demo
              </Link>
            </div>

            {/* Hero image/dashboard mockup */}
            <div className="relative max-w-4xl mx-auto animate-scale-in" style={{ animationDelay: '0.5s' }}>
              <div className="glass-card p-2 glow-blue">
                <div className="bg-navy-900 rounded-lg overflow-hidden">
                  {/* Dashboard mockup */}
                  <div className="p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-3 h-3 rounded-full bg-red-500" />
                      <div className="w-3 h-3 rounded-full bg-yellow-500" />
                      <div className="w-3 h-3 rounded-full bg-green-500" />
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      {['Red Team Active', 'Blue Team Monitoring', 'Purple Coordination'].map((label, i) => (
                        <div key={i} className="bg-white/5 rounded-lg p-4 text-center">
                          <div className="text-2xl font-bold gradient-text">{i + 1}</div>
                          <div className="text-xs text-gray-400 mt-1">{label}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-8 h-8 text-white/50" />
        </div>
      </section>

      {/* STATS SECTION */}
      <section ref={statsRef} className="py-20 bg-black/20">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { label: 'Downloads', value: counters.downloads, suffix: '+' },
              { label: 'Countries', value: counters.countries, suffix: '+' },
              { label: 'Autonomous Agents', value: counters.agents, suffix: '' },
              { label: 'CVEs Tracked', value: counters.vulns, suffix: '' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="stat-number">
                  {stat.value > 0 ? formatNumber(stat.value) : '0'}{stat.suffix}
                </div>
                <div className="text-gray-400 mt-2">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WHAT IS FREEAI SECTION */}
      <section id="what-is" className="py-32 relative">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold mb-6">
                What is{' '}
                <span className="gradient-text-animated">FreeAI</span>?
              </h2>
              <p className="text-gray-300 text-lg mb-6">
                FreeAI is an open-source AI security platform that deploys <strong className="text-white">24 autonomous agents</strong> 
                across Red, Blue, and Purple teams. Built on cutting-edge LLM technology, it provides 
                enterprise-grade cybersecurity automation without the enterprise-grade price tag.
              </p>
              <ul className="space-y-4">
                {[
                  'Autonomous red team operations',
                  'Real-time threat intelligence',
                  'Multi-provider AI orchestration',
                  'Live ISO deployment options',
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center">
                      <Check className="w-4 h-4 text-green-400" />
                    </div>
                    <span className="text-gray-300">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-3xl blur-3xl" />
              <div className="relative glass-card p-8">
                <div className="grid grid-cols-2 gap-4">
                  {['Red Team', 'Blue Team', 'Purple Team', 'Intelligence'].map((team, i) => (
                    <div key={i} className="bg-white/5 rounded-xl p-6 text-center hover:bg-white/10 transition-all cursor-pointer">
                      <div className="text-3xl font-bold gradient-text mb-2">{i + 1}</div>
                      <div className="text-sm text-gray-400">{team}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AGENTS SECTION */}
      <section id="agents" className="py-32 bg-black/20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Meet Your{' '}
              <span className="gradient-text">Agent Workforce</span>
            </h2>
            <p className="text-gray-400 text-xl max-w-2xl mx-auto">
              24 specialized AI agents working 24/7 to secure your infrastructure
            </p>
          </div>

          {/* Team filter tabs */}
          <div className="flex justify-center gap-4 mb-12">
            {['All', 'Red Team', 'Blue Team', 'Purple Team'].map((tab, i) => (
              <button
                key={tab}
                className={`px-6 py-2 rounded-full transition-all ${
                  i === 0 ? 'bg-blue-500 text-white' : 'bg-white/10 text-gray-400 hover:bg-white/20'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Agents grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {agents.map((agent, i) => (
              <div
                key={i}
                className="agent-card glass-card p-6 cursor-pointer"
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
                  agent.role === 'red' ? 'bg-red-500/20' :
                  agent.role === 'blue' ? 'bg-blue-500/20' :
                  'bg-purple-500/20'
                }`}>
                  <agent.icon className={`w-6 h-6 ${
                    agent.role === 'red' ? 'text-red-400' :
                    agent.role === 'blue' ? 'text-blue-400' :
                    'text-purple-400'
                  }`} />
                </div>
                <h3 className="font-bold text-white mb-2">{agent.name}</h3>
                <p className="text-sm text-gray-400">{agent.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI PROVIDERS SECTION */}
      <section id="providers" className="py-32">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Connect With{' '}
              <span className="gradient-text">Top AI Providers</span>
            </h2>
            <p className="text-gray-400 text-xl max-w-2xl mx-auto">
              Integration with the world's leading LLM providers
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {providers.map((provider, i) => (
              <div key={i} className="glass-card p-8 text-center hover:scale-105 transition-transform cursor-pointer">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-white/10 flex items-center justify-center">
                  <Cpu className="w-8 h-8 text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{provider.name}</h3>
                <p className="text-gray-400">{provider.model}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link href="/providers" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300">
              View all 21+ providers <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ONE BRAIN PLATFORM */}
      <section id="brain" className="py-32 bg-black/20 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="hero-shape w-96 h-96 bg-purple-500/10 top-0 right-0 animate-float" />
          <div className="hero-shape w-64 h-64 bg-blue-500/10 bottom-0 left-0 animate-float-reverse" />
        </div>

        <div className="container mx-auto px-6 relative z-10">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="order-2 md:order-1">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-3xl blur-2xl animate-pulse-glow" />
                <div className="relative glass-card p-8">
                  <div className="grid grid-cols-2 gap-6">
                    {[
                      { icon: Bot, label: 'Orchestrator', desc: 'Central coordination' },
                      { icon: Globe, label: 'Internet Engine', desc: 'Web intelligence' },
                      { icon: Layers, label: 'Data Lake', desc: 'Asset discovery' },
                      { icon: Zap, label: 'Event Stream', desc: 'Real-time alerts' },
                    ].map((item, i) => (
                      <div key={i} className="text-center p-4 bg-white/5 rounded-xl">
                        <item.icon className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                        <div className="font-semibold text-white">{item.label}</div>
                        <div className="text-xs text-gray-400">{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div className="order-1 md:order-2">
              <h2 className="text-4xl md:text-5xl font-bold mb-6">
                The{' '}
                <span className="gradient-text-animated">One Brain</span>
                <br />Platform
              </h2>
              <p className="text-gray-300 text-lg mb-6">
                FreeAI's central orchestration layer connects all agents, data sources, 
                and AI providers into a unified security operations center.
              </p>
              <ul className="space-y-4">
                {[
                  'Single-pane glass operations center',
                  'Real-time agent coordination',
                  'Cross-team intelligence sharing',
                  'Automated reporting & compliance',
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <Check className="w-4 h-4 text-blue-400" />
                    </div>
                    <span className="text-gray-300">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* LIVE ISO SECTION */}
      <section id="iso" className="py-32">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Live ISO{' '}
              <span className="gradient-text">Variants</span>
            </h2>
            <p className="text-gray-400 text-xl max-w-2xl mx-auto">
              Boot and deploy in minutes with our pre-configured live environments
            </p>
          </div>

          <div className="grid md:grid-cols-5 gap-6">
            {isoVariants.map((iso, i) => (
              <div key={i} className="glass-card p-6 text-center hover:scale-105 transition-transform cursor-pointer">
                <iso.icon className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                <h3 className="font-bold text-white mb-2">{iso.name}</h3>
                <div className="flex justify-center gap-2 mb-4">
                  <span className="text-xs px-2 py-1 rounded-full bg-white/10 text-gray-400">{iso.version}</span>
                  <span className="text-xs px-2 py-1 rounded-full bg-white/10 text-gray-400">{iso.size}</span>
                </div>
                <Link
                  href="/iso"
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  Download →
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* DEPLOY SECTION */}
      <section id="deploy" className="py-32 bg-black/20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Deploy{' '}
              <span className="gradient-text">Your Way</span>
            </h2>
            <p className="text-gray-400 text-xl max-w-2xl mx-auto">
              Multiple deployment options to fit your infrastructure
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {[
              { icon: Server, title: 'Bare Metal', desc: 'Direct hardware deployment', color: 'blue' },
              { icon: Layers, title: 'Docker', desc: 'Containerized quickstart', color: 'purple' },
              { icon: Cloud, title: 'Kubernetes', desc: 'Cloud-native orchestration', color: 'cyan' },
              { icon: Globe, title: 'Cloud', desc: 'AWS, Azure, GCP ready', color: 'green' },
            ].map((option, i) => (
              <div key={i} className="glass-card p-8 text-center hover:scale-105 transition-transform cursor-pointer">
                <div className={`w-16 h-16 mx-auto mb-6 rounded-2xl bg-${option.color}-500/20 flex items-center justify-center`}>
                  <option.icon className={`w-8 h-8 text-${option.color}-400`} />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{option.title}</h3>
                <p className="text-gray-400">{option.desc}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link
              href="/deploy"
              className="btn-primary px-8 py-4 rounded-xl font-semibold inline-flex items-center gap-2"
            >
              View all deployment methods <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* SECURITY SECTION */}
      <section id="security" className="py-32">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl font-bold mb-6">
                Enterprise-Grade{' '}
                <span className="gradient-text">Security</span>
              </h2>
              <p className="text-gray-300 text-lg mb-8">
                FreeAI implements defense-in-depth security with encrypted storage, 
                RBAC, and compliance-ready logging.
              </p>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { icon: Lock, label: 'AES-256 Encryption' },
                  { icon: Shield, label: 'RBAC Access Control' },
                  { icon: Activity, label: 'Audit Logging' },
                  { icon: Eye, label: 'Threat Detection' },
                ].map((feat, i) => (
                  <div key={i} className="flex items-center gap-3 p-4 bg-white/5 rounded-xl">
                    <feat.icon className="w-6 h-6 text-blue-400" />
                    <span className="text-sm text-gray-300">{feat.label}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-3xl blur-3xl" />
              <div className="relative glass-card p-8">
                <div className="space-y-4">
                  {['Network Security: Active', 'Threat Detection: Enabled', 'Encryption: AES-256', 'RBAC: Configured'].map((item, i) => (
                    <div key={i} className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                      <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-gray-300">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ SECTION */}
      <section id="faq" className="py-32 bg-black/20">
        <div className="container mx-auto px-6 max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Frequently Asked{' '}
              <span className="gradient-text">Questions</span>
            </h2>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <FAQItem key={i} question={faq.q} answer={faq.a} />
            ))}
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="hero-shape w-96 h-96 bg-blue-500/20 top-0 left-1/4 animate-float" />
          <div className="hero-shape w-64 h-64 bg-purple-500/20 bottom-0 right-1/4 animate-float-reverse" />
        </div>
        
        <div className="container mx-auto px-6 text-center relative z-10">
          <h2 className="text-4xl md:text-6xl font-bold mb-6">
            Ready to Deploy Your{' '}
            <span className="gradient-text-animated">Workforce</span>?
          </h2>
          <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
            Join thousands of security professionals using FreeAI to automate their security operations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/deploy"
              className="btn-primary px-10 py-4 rounded-xl text-lg font-semibold flex items-center justify-center gap-2"
            >
              <Download className="w-5 h-5" />
              Download Now
            </Link>
            <Link
              href="/docs"
              className="px-10 py-4 rounded-xl text-lg font-semibold border border-white/20 hover:bg-white/10 transition-all"
            >
              Read Documentation
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="glass-card overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-6 text-left flex justify-between items-center hover:bg-white/5 transition-colors"
      >
        <span className="font-semibold text-white">{question}</span>
        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="px-6 pb-6 text-gray-400">
          {answer}
        </div>
      )}
    </div>
  );
}

function Footer() {
  return (
    <footer className="py-12 border-t border-white/10">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
              <span className="text-white font-bold text-sm">F</span>
            </div>
            <span className="font-bold text-xl">FreeAI</span>
          </div>
          
          <div className="flex gap-8 text-sm text-gray-400">
            <Link href="/docs" className="hover:text-white transition-colors">Docs</Link>
            <Link href="/blog" className="hover:text-white transition-colors">Blog</Link>
            <Link href="/agents" className="hover:text-white transition-colors">Agents</Link>
            <Link href="/security" className="hover:text-white transition-colors">Security</Link>
            <Link href="https://github.com/ProjectZeroDays" className="hover:text-white transition-colors">GitHub</Link>
          </div>
          
          <div className="text-sm text-gray-500">
            © 2024 FreeAI. GPL-3.0 License.
          </div>
        </div>
      </div>
    </footer>
  );
}
