import Link from 'next/link'
import { ArrowLeft, Shield, Lock, Eye, AlertTriangle, CheckCircle2 } from 'lucide-react'

const securityFeatures = [
  {
    icon: <Shield className="w-6 h-6" />,
    title: 'Aikido Integration',
    desc: 'Integrated security scanning from Aikido — SAST/DAST tests, vulnerability reporting from the dashboard.',
  },
  {
    icon: <Eye className="w-6 h-6" />,
    title: 'Pentest Agents',
    desc: 'Semgrep, Bandit, Safety, Trivy (SAST/DAST). 33 security skills across Red, Blue, and Purple teams.',
  },
  {
    icon: <Lock className="w-6 h-6" />,
    title: 'Auto-Patching',
    desc: 'Generate and apply safe fixes for critical/high vulnerabilities automatically.',
  },
  {
    icon: <AlertTriangle className="w-6 h-6" />,
    title: 'Security Scanning',
    desc: 'API key rotation (10 keys per provider), auto-pause on 429, dependency management.',
  },
]

const complianceItems = [
  { standard: 'SOC 2 Type II', status: 'Design in progress', detail: 'Security controls mapped to Trust Services Criteria' },
  { standard: 'ISO 27001', status: 'Framework aligned', detail: 'Information security management policies documented' },
  { standard: 'NIST 800-53', status: 'Controls mapped', detail: 'Security and privacy controls implemented' },
  { standard: 'CMMC L2', status: 'In progress', detail: 'Defense Industrial Base compliance framework' },
]

export default function Security() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Security <span className="gradient-text">Features</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Production-grade security tools for autonomous operations. Built for red teams, blue teams, and everything in between.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          {securityFeatures.map((feature) => (
            <div key={feature.title} className="page-card">
              <div className="w-12 h-12 rounded-lg bg-blue-500/15 flex items-center justify-center text-blue-400 mb-4">
                {feature.icon}
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">{feature.title}</h2>
              <p className="text-slate-400 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>

        <section className="mb-16" id="skills">
          <h2 className="text-2xl font-semibold text-white mb-6">Security Skills</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-red-500/10 border border-red-500/20">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center">
                  <span className="text-red-400 font-bold text-sm">R</span>
                </div>
                <h3 className="text-lg font-semibold text-red-400">Red Team (14)</h3>
              </div>
              <ul className="text-sm text-slate-400 space-y-2">
                <li className="flex items-center gap-2"><span className="text-red-400">›</span> API Sniffer</li>
                <li className="flex items-center gap-2"><span className="text-red-400">›</span> Cookie Harvester</li>
                <li className="flex items-center gap-2"><span className="text-red-400">›</span> Payload Engine</li>
                <li className="flex items-center gap-2"><span className="text-red-400">›</span> Vuln Scanner</li>
                <li className="flex items-center gap-2"><span className="text-red-400">›</span> Brute Force</li>
                <li className="flex items-center gap-2"><span className="text-red-400">›</span> Exploitation</li>
                <li className="flex items-center gap-2"><span className="text-red-400">›</span> Deserialization</li>
                <li className="flex items-center gap-2"><span className="text-red-400">›</span> SSRF Exploit</li>
              </ul>
            </div>
            <div className="p-6 rounded-xl bg-blue-500/10 border border-blue-500/20">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <span className="text-blue-400 font-bold text-sm">B</span>
                </div>
                <h3 className="text-lg font-semibold text-blue-400">Blue Team (12)</h3>
              </div>
              <ul className="text-sm text-slate-400 space-y-2">
                <li className="flex items-center gap-2"><span className="text-blue-400">›</span> SIEM Integration</li>
                <li className="flex items-center gap-2"><span className="text-blue-400">›</span> Forensics</li>
                <li className="flex items-center gap-2"><span className="text-blue-400">›</span> Hunting</li>
                <li className="flex items-center gap-2"><span className="text-blue-400">›</span> Hardening</li>
                <li className="flex items-center gap-2"><span className="text-blue-400">›</span> Incident Response</li>
                <li className="flex items-center gap-2"><span className="text-blue-400">›</span> Threat Intel</li>
                <li className="flex items-center gap-2"><span className="text-blue-400">›</span> Network Defense</li>
                <li className="flex items-center gap-2"><span className="text-blue-400">›</span> Malware Analysis</li>
              </ul>
            </div>
            <div className="p-6 rounded-xl bg-purple-500/10 border border-purple-500/20">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <span className="text-purple-400 font-bold text-sm">P</span>
                </div>
                <h3 className="text-lg font-semibold text-purple-400">Purple Team (7)</h3>
              </div>
              <ul className="text-sm text-slate-400 space-y-2">
                <li className="flex items-center gap-2"><span className="text-purple-400">›</span> SIM (Simulation)</li>
                <li className="flex items-center gap-2"><span className="text-purple-400">›</span> Validate</li>
                <li className="flex items-center gap-2"><span className="text-purple-400">›</span> Bridge</li>
                <li className="flex items-center gap-2"><span className="text-purple-400">›</span> Purple Testing</li>
                <li className="flex items-center gap-2"><span className="text-purple-400">›</span> Detection Engineering</li>
                <li className="flex items-center gap-2"><span className="text-purple-400">›</span> Tabletop Exercises</li>
                <li className="flex items-center gap-2"><span className="text-purple-400">›</span> Threat Emulation</li>
              </ul>
            </div>
          </div>
        </section>

        <section id="compliance">
          <h2 className="text-2xl font-semibold text-white mb-6">Compliance & Standards</h2>
          <div className="overflow-x-auto">
            <table className="page-table">
              <thead>
                <tr>
                  <th>Standard</th>
                  <th>Status</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {complianceItems.map((item) => (
                  <tr key={item.standard}>
                    <td className="text-white font-medium">{item.standard}</td>
                    <td>
                      <span className={`page-badge ${
                        item.status.includes('progress') || item.status.includes('In progress') ? 'page-badge-blue' :
                        item.status.includes('aligned') || item.status.includes('mapped') ? 'page-badge-green' :
                        'page-badge-red'
                      }`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="text-slate-400">{item.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  )
}
