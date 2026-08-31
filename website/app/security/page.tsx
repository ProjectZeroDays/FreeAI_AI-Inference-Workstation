import Link from 'next/link'
import { ArrowLeft, Shield, Lock, Eye, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'

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

export default function Security() {
  return (
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Security <span className="gradient-text">Features</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Production-grade security tools for autonomous operations.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          {securityFeatures.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-xl bg-white/5 border border-white/10"
            >
              <div className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center text-primary mb-4">
                {feature.icon}
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">{feature.title}</h2>
              <p className="text-gray-400">{feature.desc}</p>
            </motion.div>
          ))}
        </div>

        <motion.section initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <h2 className="text-2xl font-semibold text-white mb-6">Security Skills</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-red-500/10 border border-red-500/20">
              <h3 className="text-lg font-semibold text-red-400 mb-2">Red Team (14)</h3>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• API Sniffer</li>
                <li>• Cookie Harvester</li>
                <li>• Payload Engine</li>
                <li>• Vuln Scanner</li>
                <li>• Brute Force</li>
                <li>• Exploitation</li>
              </ul>
            </div>
            <div className="p-6 rounded-xl bg-blue-500/10 border border-blue-500/20">
              <h3 className="text-lg font-semibold text-blue-400 mb-2">Blue Team (12)</h3>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• SIEM Integration</li>
                <li>• Forensics</li>
                <li>• Hunting</li>
                <li>• Hardening</li>
                <li>• Incident Response</li>
                <li>• Threat Intel</li>
              </ul>
            </div>
            <div className="p-6 rounded-xl bg-purple-500/10 border border-purple-500/20">
              <h3 className="text-lg font-semibold text-purple-400 mb-2">Purple Team (7)</h3>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• SIM (Simulation)</li>
                <li>• Validate</li>
                <li>• Bridge</li>
                <li>• Purple Testing</li>
                <li>• Detection Engineering</li>
                <li>• Tabletop Exercises</li>
              </ul>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  )
}
