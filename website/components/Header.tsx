'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Menu, X, Github, Download } from 'lucide-react'

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/#capabilities', label: 'Features' },
  { href: '/agents', label: 'Agents' },
  { href: '/deploy', label: 'Deploy' },
  { href: '/providers', label: 'Providers' },
  { href: '/iso', label: 'Live ISO' },
]

export default function Header() {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled
        ? 'bg-[#020617]/90 backdrop-blur-md border-b border-white/10 shadow-lg shadow-black/20'
        : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2" aria-label="FreeAI Home">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <span className="text-white font-bold text-sm">F</span>
            </div>
            <span className="font-bold text-lg text-white">FreeAI</span>
          </Link>

          <nav className="hidden md:flex items-center gap-1" aria-label="Main navigation">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="px-3 py-2 rounded-md text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <a
              href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-md text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
              aria-label="GitHub repository"
            >
              <Github size={20} />
            </a>
            <Link
              href="/deploy"
              className="hidden md:inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold transition-all hover:scale-105 hover:shadow-lg hover:shadow-blue-500/25"
            >
              <Download size={14} />
              Deploy
            </Link>
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden p-2 rounded-md text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
              aria-label={isOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={isOpen}
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden bg-[#020617]/95 backdrop-blur-md border-b border-white/10">
          <nav className="px-4 py-4 space-y-1" aria-label="Mobile navigation">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className="block px-3 py-2 rounded-md text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/deploy"
              onClick={() => setIsOpen(false)}
              className="block px-3 py-2 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-center font-medium transition-colors mt-2"
            >
              Deploy FreeAI
            </Link>
          </nav>
        </div>
      )}
    </header>
  )
}
