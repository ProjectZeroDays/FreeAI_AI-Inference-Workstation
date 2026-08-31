import Link from 'next/link'
import { ArrowLeft, Mail, FlaskRound as FlaskConical, Terminal, Database } from 'lucide-react'
import { motion } from 'framer-motion'

const apiSections = [
  {
    title: 'Router API (:8010)',
    icon: <Terminal className="w-5 h-5" />,
    endpoints: [
      { method: 'GET', path: '/health', desc: 'Liveness + mock flag' },
      { method: 'GET', path: '/models', desc: 'Roster: name/role/strengths/endpoint' },
      { method: 'POST', path: '/route', desc: '{prompt, max_tokens?, temperature?, agent?}' },
      { method: 'GET', path: '/metrics', desc: 'Counters, per-task/model, latency_avg_ms' },
    ],
  },
  {
    title: 'Agent API (:8020)',
    icon: <Mail className="w-5 h-5" />,
    endpoints: [
      { method: 'POST', path: '/agent/project', desc: 'Full project generation' },
      { method: 'POST', path: '/agent/refactor', desc: 'Code refactoring' },
      { method: 'POST', path: '/agent/debug', desc: 'Debug assistance' },
      { method: 'POST', path: '/agent/analyze', desc: 'Code analysis' },
      { method: 'POST', path: '/agent/orchestrate', desc: 'Multi-agent orchestration' },
      { method: 'POST', path: '/agent/chat', desc: 'Chat with session memory' },
      { method: 'GET/DELETE', path: '/memory/{session_id}', desc: 'Session memory management' },
    ],
  },
  {
    title: 'Workflow Engine (:8040)',
    icon: <FlaskConical className="w-5 h-5" />,
    endpoints: [
      { method: 'GET', path: '/workflows', desc: 'List available workflows' },
      { method: 'POST', path: '/workflow/run', desc: 'Execute workflow' },
      { method: 'POST', path: '/workflow/run-inline', desc: 'Run inline definition' },
      { method: 'GET', path: '/workflow/export/{name}', desc: 'Export workflow' },
      { method: 'POST', path: '/workflow/validate', desc: 'Validate workflow steps' },
    ],
  },
  {
    title: 'Autonomous SDLC (:8050)',
    icon: <Database className="w-5 h-5" />,
    endpoints: [
      { method: 'POST', path: '/auto/start', desc: 'Start autonomous run' },
      { method: 'GET', path: '/auto/runs', desc: 'List all runs' },
      { method: 'GET', path: '/auto/runs/{id}', desc: 'Get run status' },
      { method: 'POST', path: '/auto/runs/{id}/cancel', desc: 'Cancel run' },
      { method: 'GET', path: '/auto/runs/{id}/artifact', desc: 'Download artifact' },
      { method: 'POST', path: '/auto/runs/{id}/shell', desc: 'Execute shell command' },
    ],
  },
]

export default function API() {
  return (
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            REST <span className="gradient-text">API Reference</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Complete API documentation for all FreeAI services.
          </p>
        </motion.div>

        <div className="space-y-12">
          {apiSections.map((section, i) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-xl bg-white/5 border border-white/10"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
                  {section.icon}
                </div>
                <h2 className="text-xl font-semibold text-white">{section.title}</h2>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="pb-3 text-gray-400 font-medium w-24">Method</th>
                      <th className="pb-3 text-gray-400 font-medium">Path</th>
                      <th className="pb-3 text-gray-400 font-medium">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {section.endpoints.map((ep, j) => (
                      <tr key={j} className="hover:bg-white/5 transition-colors">
                        <td className="py-3">
                          <span className={`inline-flex px-2 py-1 rounded text-xs font-mono ${
                            ep.method.includes('GET') ? 'bg-green-500/20 text-green-400' :
                            ep.method.includes('POST') ? 'bg-blue-500/20 text-blue-400' :
                            ep.method.includes('DELETE') ? 'bg-red-500/20 text-red-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {ep.method}
                          </span>
                        </td>
                        <td className="py-3 text-blue-400 font-mono text-sm">{ep.path}</td>
                        <td className="py-3 text-gray-400 text-sm">{ep.desc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {section.title === 'Router API (:8010)' && (
                <div className="mt-6">
                  <h3 className="text-white font-medium mb-3">Example Request</h3>
                  <pre className="bg-black/50 rounded-lg p-4 text-sm text-green-400 overflow-x-auto font-mono">
{`curl -X POST localhost:8010/route \\
  -H "Content-Type: application/json" \\
  -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'

// Response:
{
  "model_used": "openai/gpt-4o-mini",
  "task_type": "general_code",
  "confidence": 0.87,
  "elapsed_ms": 342,
  "response": "..."
}`}
                  </pre>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
