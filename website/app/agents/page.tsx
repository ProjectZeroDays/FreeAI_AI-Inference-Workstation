import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

const redTeamAgents = [
  { name: 'API Sniffer', desc: 'CDP Network domain interception, endpoint mapping' },
  { name: 'Cookie Harvester', desc: 'Session harvesting, cookie crafting, Netscape export' },
  { name: 'Payload Engine', desc: 'Polymorphic AES-256-GCM + XOR encryption, 9 formats' },
  { name: 'Vuln Scanner', desc: 'nmap, nuclei, sqlmap, ffuf, OWASP ZAP + NIST reports' },
  { name: 'Brute Force', desc: 'hashcat GPU, rainbow tables, hydra, JWT/ZIP/SSH' },
  { name: 'Exploitation', desc: 'Metasploit API, privilege escalation, lateral movement' },
  { name: 'Deserialization', desc: 'Java/PHP/.NET deserialization attack generation' },
  { name: 'SSRF Exploit', desc: 'Server-side request forgery detection and exploitation' },
  { name: 'Memory Corruption', desc: 'Buffer overflow, UAF, heap spray techniques' },
  { name: 'File Parse Exploit', desc: 'PDF, Office, Image format vulnerability exploitation' },
  { name: 'Messaging RCE', desc: 'SMS, Email, IM protocol exploitation' },
  { name: 'Android Exploit', desc: 'Android app vulnerability research and exploitation' },
  { name: 'IoT Exploit', desc: 'IoT device firmware analysis and exploitation' },
  { name: 'Chained Zero Day', desc: 'Multi-stage exploit chain development' },
]

const blueTeamAgents = [
  { name: 'SIEM Integration', desc: 'Log aggregation, alert correlation' },
  { name: 'Forensics', desc: 'Memory dump analysis, timeline reconstruction' },
  { name: 'Hunting', desc: 'ATT&CK mapping, IoC hunting, persistence detection' },
  { name: 'Hardening', desc: 'CIS benchmarks, vulnerability remediation' },
  { name: 'Incident Response', desc: 'Automated containment, evidence preservation' },
  { name: 'Threat Intel', desc: 'IOC feeds, TTP mapping, threat intelligence' },
  { name: 'Network Defense', desc: 'IDS/IPS configuration, traffic analysis' },
  { name: 'Malware Analysis', desc: 'Static/dynamic malware analysis' },
  { name: 'Compliance', desc: 'PCI-DSS, HIPAA, SOC2 compliance checks' },
  { name: 'Vuln Scanner', desc: 'Continuous vulnerability scanning' },
  { name: 'Identity Mgmt', desc: 'IAM configuration, access control audit' },
  { name: 'Security Config', desc: 'Secure baseline configuration' },
]

const purpleTeamAgents = [
  { name: 'SIM (Simulation)', desc: 'Attack simulation, detection validation' },
  { name: 'Validate', desc: 'Defense testing, gap analysis' },
  { name: 'Bridge', desc: 'Red→Blue handoff, JIRA ticket generation' },
  { name: 'Purple Testing', desc: 'Automated attack-defend cycles' },
  { name: 'Detection Engineering', desc: 'Signature development, rules tuning' },
  { name: 'Tabletop Exercises', desc: 'Incident response scenario simulation' },
  { name: 'Threat Emulation', desc: 'Adversary behavior simulation' },
]

const teamConfig = [
  { name: 'Red', color: 'red', count: redTeamAgents.length, hex: '#ef4444' },
  { name: 'Blue', color: 'blue', count: blueTeamAgents.length, hex: '#3b82f6' },
  { name: 'Purple', color: 'purple', count: purpleTeamAgents.length, hex: '#8b5cf6' },
]

export default function Agents() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            24 <span className="gradient-text">Autonomous Agents</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Red Team, Blue Team, and Purple Team agents for complete security operations.
          </p>
        </div>

        {/* Team summary */}
        <div className="flex flex-wrap gap-4 mb-12">
          {teamConfig.map((t) => (
            <div key={t.name} className="page-card flex items-center gap-3 px-5 py-3">
              <div className="w-3 h-3 rounded-full" style={{ background: t.hex }} />
              <span className="text-white font-semibold">{t.name} Team</span>
              <span className="text-slate-400 text-sm">{t.count} agents</span>
            </div>
          ))}
        </div>

        {/* Red Team */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
              <span className="text-red-400 font-bold">R</span>
            </div>
            <h2 className="text-xl font-semibold text-white">Red Team — Offensive Security</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {redTeamAgents.map((agent) => (
              <div key={agent.name} className="page-card p-4">
                <h3 className="text-white font-medium mb-1">{agent.name}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{agent.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Blue Team */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <span className="text-blue-400 font-bold">B</span>
            </div>
            <h2 className="text-xl font-semibold text-white">Blue Team — Defensive Operations</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {blueTeamAgents.map((agent) => (
              <div key={agent.name} className="page-card p-4">
                <h3 className="text-white font-medium mb-1">{agent.name}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{agent.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Purple Team */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
              <span className="text-purple-400 font-bold">P</span>
            </div>
            <h2 className="text-xl font-semibold text-white">Purple Team — Collaboration</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {purpleTeamAgents.map((agent) => (
              <div key={agent.name} className="page-card p-4">
                <h3 className="text-white font-medium mb-1">{agent.name}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{agent.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
