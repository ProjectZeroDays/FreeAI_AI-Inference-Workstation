import Link from 'next/link'
import { ArrowLeft, Heart, Code, Users } from 'lucide-react'

const roles = [
  { title: 'Backend Engineer', desc: 'Flask, FastAPI, Python automation', count: 3 },
  { title: 'Frontend Developer', desc: 'React, Next.js, TypeScript, Tailwind', count: 2 },
  { title: 'DevOps / Platform', desc: 'Docker, Kubernetes, CI/CD', count: 2 },
  { title: 'Security Researcher', desc: 'Red team, vulnerability research', count: 2 },
  { title: 'Technical Writer', desc: 'Documentation, tutorials, guides', count: 1 },
]

const benefits = [
  'Fully remote, async-first culture',
  'Open source contributions welcomed',
  'Conference budget & speaking opportunities',
  'Hardware stipend for dev machines',
  'Direct impact on thousands of users',
]

export default function LegalCareers() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <h1 className="text-4xl font-bold text-white mb-4">Careers <span className="gradient-text">&amp; Community</span></h1>
        <p className="text-slate-400 text-lg mb-12">
          Join the team building the future of autonomous AI operations.
        </p>

        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-blue-500/15 flex items-center justify-center text-blue-400">
              <Code size={20} />
            </div>
            <h2 className="text-2xl font-semibold text-white">Open Roles</h2>
          </div>
          <div className="space-y-4">
            {roles.map((role) => (
              <div key={role.title} className="page-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-white font-semibold">{role.title}</h3>
                  <p className="text-slate-400 text-sm mt-1">{role.desc}</p>
                </div>
                <span className="page-badge page-badge-blue flex-shrink-0">{role.count} position{role.count > 1 ? 's' : ''}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-green-500/15 flex items-center justify-center text-green-400">
              <Heart size={20} />
            </div>
            <h2 className="text-2xl font-semibold text-white">Benefits</h2>
          </div>
          <ul className="space-y-3">
            {benefits.map((b) => (
              <li key={b} className="flex items-center gap-3 text-slate-300">
                <CheckIcon />
                {b}
              </li>
            ))}
          </ul>
        </section>

        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-purple-500/15 flex items-center justify-center text-purple-400">
              <Users size={20} />
            </div>
            <h2 className="text-2xl font-semibold text-white">Contribute</h2>
          </div>
          <p className="text-slate-400 leading-relaxed mb-6">
            Not ready to join full-time? You can contribute to FreeAI through GitHub. We welcome pull requests, bug reports, documentation improvements, and feature suggestions. Check out our <Link href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/blob/main/CONTRIBUTING.md" className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noopener noreferrer">Contributing Guide</Link> to get started.
          </p>
          <Link
            href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation"
            target="_blank" rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold transition-all"
          >
            <Code size={16} />
            View on GitHub
          </Link>
        </section>
      </div>
    </div>
  )
}

function CheckIcon() {
  return (
    <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  )
}
