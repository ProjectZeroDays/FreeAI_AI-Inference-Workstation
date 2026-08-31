import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

const inter = Inter({ subsets: ['latin'], display: 'swap' })

export const metadata: Metadata = {
  title: 'FreeAI — The AI operational layer for your fleet',
  description: 'From digital workplace to autonomous workplace. FreeAI is the AI operational layer for your entire fleet — ask anything, predict impact, automate with approvals.',
  keywords: ['AI', 'LLM', 'inference', 'autonomous agents', 'security', 'endpoint management', 'red team', 'blue team'],
  authors: [{ name: 'ProjectZeroDays' }],
  openGraph: {
    title: 'FreeAI — The AI operational layer for your fleet',
    description: 'Ask anything, predict impact, automate with approvals. 24 autonomous agents for your entire security fleet.',
    type: 'website',
    url: 'https://freeai.projectzerodays.com',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'FreeAI — The AI operational layer for your fleet',
    description: 'Ask anything, predict impact, automate with approvals.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} bg-white text-slate-900 min-h-screen`}>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  )
}
