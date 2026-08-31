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

export default function Agents() {
  return (
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            24 <span className="gradient-text">Autonomous Agents</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Red Team, Blue Team, and Purple Team agents for complete security operations.
          </p>
        </div>

        {/* Red Team */}
        <section className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
              <span className="text-red-500 font-bold">R</span>
            </div>
            <h2 className="text-2xl font-semibold text-white">Red Team ({redTeamAgents.length})</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {redTeamAgents.map((agent, i) => (
              <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10">
                <h3 className="text-white font-medium mb-1">{agent.name}</h3>
                <p className="text-gray-400 text-sm">{agent.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Blue Team */}
        <section className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <span className="text-blue-500 font-bold">B</span>
            </div>
            <h2 className="text-2xl font-semibold text-white">Blue Team ({blueTeamAgents.length})</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {blueTeamAgents.map((agent, i) => (
              <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10">
                <h3 className="text-white font-medium mb-1">{agent.name}</h3>
                <p className="text-gray-400 text-sm">{agent.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Purple Team */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
              <span className="text-purple-500 font-bold">P</span>
            </div>
            <h2 className="text-2xl font-semibold text-white">Purple Team ({purpleTeamAgents.length})</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {purpleTeamAgents.map((agent, i) => (
              <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10">
                <h3 className="text-white font-medium mb-1">{agent.name}</h3>
                <p className="text-gray-400 text-sm">{agent.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
