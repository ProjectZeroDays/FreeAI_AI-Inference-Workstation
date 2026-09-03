import Link from 'next/link'
import { ArrowLeft, Mail, FlaskRound as FlaskConical, Terminal, Database } from 'lucide-react'

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
    ],
  },
]

export default function API() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            REST <span className="gradient-text">API Reference</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Complete API documentation for all FreeAI services. All endpoints require <code className="page-code">X-Auth-Token</code> header when auth is enabled.
          </p>
        </div>

        <div className="space-y-8">
          {apiSections.map((section) => (
            <div key={section.title} className="page-card">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-blue-500/15 flex items-center justify-center text-blue-400">
                  {section.icon}
                </div>
                <h2 className="text-lg font-semibold text-white">{section.title}</h2>
              </div>

              <div className="overflow-x-auto">
                <table className="page-table">
                  <thead>
                    <tr>
                      <th className="w-24">Method</th>
                      <th>Path</th>
                      <th>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {section.endpoints.map((ep) => (
                      <tr key={ep.path}>
                        <td>
                          <span className={`inline-flex px-2 py-1 rounded text-xs font-mono ${
                            ep.method.includes('GET') ? 'bg-green-500/20 text-green-400' :
                            ep.method.includes('POST') ? 'bg-blue-500/20 text-blue-400' :
                            ep.method.includes('DELETE') ? 'bg-red-500/20 text-red-400' :
                            'bg-slate-500/20 text-slate-400'
                          }`}>
                            {ep.method}
                          </span>
                        </td>
                        <td className="text-blue-400 font-mono text-sm">{ep.path}</td>
                        <td className="text-slate-400 text-sm">{ep.desc}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {section.title === 'Router API (:8010)' && (
                <div className="mt-6">
                  <h3 className="text-white font-medium mb-3 text-sm">Example Request</h3>
                  <pre className="page-pre">{`curl -X POST localhost:8010/route \\
  -H "Content-Type: application/json" \\
  -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'

// Response:
{
  "model_used": "openai/gpt-4o-mini",
  "task_type": "general_code",
  "confidence": 0.87,
  "elapsed_ms": 342,
  "response": "..."
}`}</pre>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-10 text-center">
          <Link href="/docs" className="page-nav-link inline-flex">
            <ArrowLeft size={16} />
            Back to Documentation
          </Link>
        </div>
      </div>
    </div>
  )
}
