import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

const isoVariants = [
  { name: 'Ubuntu 24.04 XFCE', desc: 'Default desktop with full FreeAI stack pre-loaded', command: 'Try Live / Install / Rescue' },
  { name: 'Kali Linux Rolling', desc: 'Full penetration-testing suite with networking preserved', command: 'Try Kali Live' },
  { name: 'Kodachi Linux', desc: 'Security-focused distro — Kali hardened with extra privacy tools', command: 'Try Kodachi Live' },
  { name: 'Debian 12', desc: 'Stable base with XFCE desktop and FreeAI tools', command: 'Try Debian Live' },
  { name: 'NixOS Minimum', desc: 'Declarative, reproducible, secure by default', command: 'Try NixOS Live' },
]

const bootMenu = [
  { entry: 'FreeAIOS Live', action: 'Standard live session with all FreeAI tools' },
  { entry: 'Install FreeAI', action: 'Unattended Subiquity install, first-boot provision' },
  { entry: 'Try Ubuntu Server', action: 'Stock live session (RAM)' },
  { entry: 'Try Kali Linux', action: 'Kali XFCE rolling live mode' },
  { entry: 'Try NixOS', action: 'NixOS minimal live session' },
  { entry: 'Rescue shell', action: 'Live session into rescue target' },
]

export default function ISO() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            FreeAIOS — <span className="gradient-text">Live ISO</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Bootable workstations for Ubuntu, Kali, Kodachi, Debian, and NixOS. No install required — try before you commit.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {isoVariants.map((iso) => (
            <div key={iso.name} className="page-card">
              <h3 className="text-lg font-semibold text-white mb-2">{iso.name}</h3>
              <p className="text-slate-400 text-sm mb-4 leading-relaxed">{iso.desc}</p>
              <code className="page-code">{iso.command}</code>
            </div>
          ))}
        </div>

        <section className="mb-16">
          <h2 className="text-2xl font-semibold text-white mb-6">Build Your Own ISO</h2>
          <div className="page-card">
            <pre className="page-pre">{`# Requirements
sudo apt-get install -y xorriso isolinux

# Build from Ubuntu ISO
UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso \\
./live/build-live.sh

# Optional: bake repo into ISO for offline install
REPO_TARBALL=../dist/freeai-v1.2.0.tar.gz \\
./live/build-live.sh`}</pre>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white mb-6">GRUB Boot Menu</h2>
          <div className="overflow-x-auto">
            <table className="page-table">
              <thead>
                <tr>
                  <th>Entry</th>
                  <th>What it does</th>
                </tr>
              </thead>
              <tbody>
                {bootMenu.map((entry, i) => (
                  <tr key={i}>
                    <td className="text-white font-medium">{entry.entry}</td>
                    <td className="text-slate-400">{entry.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  )
}
