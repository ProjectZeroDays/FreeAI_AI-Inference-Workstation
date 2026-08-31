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
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Blog & <span className="gradient-text">Release Notes</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Latest updates and tutorials from the FreeAI team.
          </p>
        </div>

        <div className="space-y-8">
          {releases.map((release, i) => (
            <article key={release.version} className="p-6 rounded-xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-4 mb-4">
                <span className="px-3 py-1 rounded-full bg-primary/20 text-primary text-sm font-medium">
                  {release.version}
                </span>
                <span className="text-gray-500 text-sm">{release.date}</span>
              </div>
              <h2 className="text-2xl font-semibold text-white mb-4">{release.title}</h2>
              <ul className="space-y-2">
                {release.features.map((feature, j) => (
                  <li key={j} className="flex items-center gap-2 text-gray-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </div>
    </div>
  )
}
