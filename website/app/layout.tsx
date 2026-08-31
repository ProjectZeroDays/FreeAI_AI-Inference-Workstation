import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'FreeAI — Unified AI Workstation',
  description: 'Local LLMs, autonomous agents, full SDLC automation, security tools, and multi-provider routing. One self-hosted stack.',
  keywords: ['AI', 'LLM', 'inference', 'autonomous agents', 'SDLC', 'security', 'GPU', 'local AI'],
  authors: [{ name: 'ProjectZeroDays' }],
  openGraph: {
    title: 'FreeAI — Unified AI Workstation',
    description: 'Local LLMs, autonomous agents, full SDLC automation, security tools, and multi-provider routing.',
    type: 'website',
    url: 'https://freeai.projectzerodays.com',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'FreeAI — Unified AI Workstation',
    description: 'Local LLMs, autonomous agents, full SDLC automation.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-navy-900 text-gray-100 min-h-screen`}>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  )
}
