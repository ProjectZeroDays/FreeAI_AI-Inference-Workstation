import Link from 'next/link'
import { ArrowLeft, Shield, Eye, Lock, AlertTriangle } from 'lucide-react'

export default function LegalPrivacy() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <h1 className="text-4xl font-bold text-white mb-4">Privacy <span className="gradient-text">Policy</span></h1>
        <p className="text-slate-500 text-sm mb-10">Last updated: September 2026</p>

        <div className="space-y-8 text-slate-300 leading-relaxed">
          <section>
            <h2 className="text-xl font-semibold text-white mb-3">1. Information We Collect</h2>
            <p>We collect information you provide directly, such as your email address when you sign up for early access or contact us. We also automatically collect certain information when you visit our site, including your IP address, browser type, and pages viewed.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">2. How We Use Your Information</h2>
            <p>We use the information we collect to: provide and improve our services, communicate with you about updates and features, respond to your comments and questions, and send you promotional materials (with your consent).</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">3. Data Storage & Security</h2>
            <p>Your data is stored securely and is never shared with third-party advertisers. We use industry-standard encryption and security practices to protect your information. As a security-focused product, we take data protection seriously.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">4. Cookies & Tracking</h2>
            <p>Our website uses essential cookies for functionality and analytics cookies to understand how visitors interact with our site. You can control cookie preferences through your browser settings.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">5. Your Rights</h2>
            <p>You have the right to access, correct, or delete your personal data at any time. Contact us at privacy@projectzerodays.com for any data-related requests.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-white mb-3">6. Open Source Commitment</h2>
            <p>FreeAI is open source (GPL-3.0). Our code is public, and we believe in transparency. You can review exactly how data is handled in our repository.</p>
          </section>
        </div>
      </div>
    </div>
  )
}
