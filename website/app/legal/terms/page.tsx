import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function LegalTerms() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <h1 className="text-4xl font-bold text-white mb-4">Terms <span className="gradient-text">of Service</span></h1>
        <p className="text-slate-500 text-sm mb-10">Last updated: September 2026</p>

        <div className="space-y-8 text-slate-300 leading-relaxed">
          <section>
            <h2 className="text-xl font-semibold text-white mb-3">1. License</h2>
            <p>FreeAI is licensed under GPL-3.0. You are free to use, modify, and distribute the software in accordance with the terms of this license. The software is provided "as is" without warranty of any kind.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">2. Acceptable Use</h2>
            <p>You agree to use FreeAI responsibly and in compliance with all applicable laws. You are responsible for your own deployment, configuration, and use of the software. The authors are not liable for any damages arising from use of the software.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">3. No Liability</h2>
            <p>To the fullest extent permitted by law, the authors of FreeAI shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the software.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">4. Community Guidelines</h2>
            <p>When participating in our community (GitHub, discussions, etc.), you agree to follow our community guidelines and treat others with respect. Harassment, abuse, or unethical use of the software will not be tolerated.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">5. Modifications</h2>
            <p>We reserve the right to modify these terms at any time. Continued use of the software after changes constitutes acceptance of the new terms.</p>
          </section>
        </div>
      </div>
    </div>
  )
}
