import Link from 'next/link'
import { ArrowLeft, Terminal, Activity, Cpu, Shield, Zap } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Dashboard <span className="gradient-text">Preview</span>
          </h1>
          <p className="text-slate-400 text-lg">
            The FreeAI Dashboard runs at <code className="text-blue-400 bg-blue-500/10 px-2 py-1 rounded text-sm">http://localhost:8030</code> after deployment.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[
            { icon: <Activity className="w-6 h-6" />, label: 'GPU Utilization', value: '87%', color: 'text-green-400' },
            { icon: <Cpu className="w-6 h-6" />, label: 'Active Models', value: '8', color: 'text-blue-400' },
            { icon: <Shield className="w-6 h-6" />, label: 'Security Score', value: 'A+', color: 'text-purple-400' },
            { icon: <Zap className="w-5 h-5" />, label: 'Agents Running', value: '24', color: 'text-yellow-400' },
          ].map((stat, i) => (
            <div key={i} className="p-6 rounded-xl bg-slate-800/60 border border-slate-700">
              <div className={`w-12 h-12 rounded-lg bg-slate-700/60 flex items-center justify-center mb-4 ${stat.color}`}>
                {stat.icon}
              </div>
              <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-sm text-slate-400">{stat.label}</div>
            </div>
          ))}
        </div>

        <div className="p-8 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-slate-700 text-center">
          <Terminal className="w-12 h-12 text-blue-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-4">Dashboard not running?</h2>
          <p className="text-slate-400 mb-6 max-w-lg mx-auto">
            Deploy FreeAI first to access the live dashboard with real-time metrics, agent controls, and security monitoring.
          </p>
          <Link
            href="/deploy"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold transition-all hover:scale-105"
          >
            Go to Deploy Guide
          </Link>
        </div>
      </div>
    </div>
  )
}
