import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

const releases = [
  {
    version: 'v1.2.0',
    date: '2026-08-31',
    title: 'Autonomous SDLC Agents & Aikido Security',
    features: ['7-phase SDLC automation', 'Aikido integration', '33 security skills', 'Live ISO builder'],
  },
  {
    version: 'v1.1.0',
    date: '2026-08-28',
    title: 'Model Router v2',
    features: ['Confidence-scored routing', 'Fallback chains', 'LRU cache', 'Rate limiting'],
  },
  {
    version: 'v1.0.0',
    date: '2026-08-25',
    title: 'Initial Release',
    features: ['GPU inference layer', 'Agent API', 'Dashboard', 'Basic workflows'],
  },
]

export default function Blog() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Blog & <span className="gradient-text">Release Notes</span>
          </h1>
          <p className="text-slate-400 text-lg">
            Latest updates and tutorials from the FreeAI team.
          </p>
        </div>

        <div className="space-y-8">
          {releases.map((release) => (
            <article key={release.version} className="page-card">
              <div className="flex items-center gap-4 mb-4">
                <span className="page-badge page-badge-blue">{release.version}</span>
                <span className="text-slate-500 text-sm">{release.date}</span>
              </div>
              <h2 className="text-2xl font-semibold text-white mb-4">{release.title}</h2>
              <ul className="space-y-2">
                {release.features.map((feature, j) => (
                  <li key={j} className="flex items-center gap-3 text-slate-300 text-sm">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>

        <div className="mt-12 p-6 rounded-xl bg-slate-800/60 border border-slate-700 text-center">
          <p className="text-slate-400 text-sm">
            More posts coming soon. Follow our{' '}
            <Link href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation" className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noopener noreferrer">
              GitHub releases
            </Link>{' '}
            for the latest updates.
          </p>
        </div>
      </div>
    </div>
  )
}
