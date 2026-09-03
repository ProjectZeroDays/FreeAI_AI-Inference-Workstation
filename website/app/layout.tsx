import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Script from 'next/script'
import './globals.css'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import Chat from '@/components/Chat'

const inter = Inter({ subsets: ['latin'], display: 'swap' })

export const metadata: Metadata = {
  title: {
    default: 'FreeAI — AI Inference Workstation',
    template: '%s | FreeAI',
  },
  description: 'Self-hosted AI inference workstation with autonomous agents, GPU acceleration, and full security tooling. Deploy locally or to any cloud.',
  keywords: ['AI', 'LLM', 'inference', 'autonomous agents', 'security', 'GPU', 'llama.cpp', 'vLLM', 'red team', 'blue team', 'pentesting'],
  authors: [{ name: 'ProjectZeroDays' }],
  creator: 'ProjectZeroDays',
  publisher: 'ProjectZeroDays',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    title: 'FreeAI — AI Inference Workstation',
    description: 'Self-hosted AI inference workstation with autonomous agents, GPU acceleration, and full security tooling.',
    type: 'website',
    url: 'https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation/',
    siteName: 'FreeAI',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'FreeAI Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'FreeAI — AI Inference Workstation',
    description: 'Self-hosted AI inference workstation with autonomous agents and GPU acceleration.',
  },
  alternates: {
    canonical: 'https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation/',
  },
  category: 'technology',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <meta name="theme-color" content="#020617" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <Script id="json-ld-org" strategy="afterInteractive">
          {`
            {
              "@context": "https://schema.org",
              "@type": "Organization",
              "name": "FreeAI",
              "url": "https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation",
              "description": "Self-hosted AI inference workstation with autonomous agents, GPU acceleration, and full security tooling.",
              "founder": "ProjectZeroDays",
              "foundingDate": "2026",
              "sameAs": [
                "https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation"
              ],
              "knowsAbout": ["Artificial Intelligence", "Cybersecurity", "Penetration Testing", "LLM Inference", "GPU Computing"],
              "license": "GPL-3.0"
            }
          `}
        </Script>
        <Script id="json-ld-software" strategy="afterInteractive">
          {`
            {
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "FreeAI",
              "operatingSystem": "Linux, Windows, macOS",
              "applicationCategory": "DeveloperApplication",
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
              },
              "description": "Self-hosted AI inference workstation with 24 autonomous agents for red team, blue team, and purple team operations.",
              "softwareVersion": "1.11.0",
              "license": "https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/blob/main/LICENSE",
              "installUrl": "https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation/deploy"
            }
          `}
        </Script>
      </head>
      <body className={`${inter.className} bg-[#020617] text-slate-100 min-h-screen`}>
        <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[60] focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg">
          Skip to main content
        </a>
        <Header />
        <main id="main-content">{children}</main>
        <Footer />
        <Chat />
      </body>
    </html>
  )
}
