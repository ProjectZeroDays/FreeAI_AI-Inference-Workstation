'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Menu, X, Moon, Sun, Github, Download } from 'lucide-react'

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/#ask-agents', label: 'Ask Agents' },
  { href: '/#artifacts', label: 'Artifacts' },
  { href: '/#capabilities', label: 'Capabilities' },
  { href: '/agents', label: 'Agents' },
  { href: '/deploy', label: 'Deploy' },
  { href: '/providers', label: 'Providers' },
  { href: '/iso', label: 'Live ISO' },
  { href: '/api', label: 'API' },
  { href: '/docs', label: 'Docs' },
  { href: '/blog', label: 'Blog' },
  { href: '/security', label: 'Security' },
]

export default function Header() {
  const [isOpen, setIsOpen] = useState(false)
  const [isDark, setIsDark] = useState(true)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('theme')
    if (saved) setIsDark(saved === 'dark')

    const handleScroll = () => {
      setScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const toggleTheme = () => {
    const newTheme = !isDark
    setIsDark(newTheme)
    localStorage.setItem('theme', newTheme ? 'dark' : 'light')
  }

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled 
        ? 'bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm' 
        : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold text-sm">F</span>
            </div>
            <span className="font-bold text-lg text-slate-900">FreeAI</span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="px-3 py-2 rounded-md text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            >
              {isDark ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <a
              href="https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            >
              <Github size={20} />
            </a>
            <Link
              href="/deploy"
              className="hidden md:inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-all hover:scale-105"
            >
              <Download size={14} />
              Deploy
            </Link>
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden p-2 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden bg-white/95 backdrop-blur-md border-b border-slate-200">
          <nav className="px-4 py-4 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className="block px-3 py-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/deploy"
              onClick={() => setIsOpen(false)}
              className="block px-3 py-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white text-center font-medium transition-colors mt-2"
            >
              Deploy FreeAI
            </Link>
          </nav>
        </div>
      )}
    </header>
  )
}
