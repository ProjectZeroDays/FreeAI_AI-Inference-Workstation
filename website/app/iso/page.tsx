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
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            FreeAIOS — <span className="gradient-text">Live ISO</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Bootable workstations for Ubuntu, Kali, Kodachi, Debian, and NixOS.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {isoVariants.map((iso) => (
            <div key={iso.name} className="p-6 rounded-xl bg-white/5 border border-white/10">
              <h3 className="text-lg font-semibold text-white mb-2">{iso.name}</h3>
              <p className="text-gray-400 text-sm mb-4">{iso.desc}</p>
              <code className="text-xs text-blue-400 bg-blue-500/10 px-2 py-1 rounded">{iso.command}</code>
            </div>
          ))}
        </div>

        <section className="mb-16">
          <h2 className="text-2xl font-semibold text-white mb-6">Build Your Own ISO</h2>
          <pre className="bg-black/50 rounded-lg p-6 text-sm text-green-400 overflow-x-auto font-mono">
{`# Requirements
sudo apt-get install -y xorriso isolinux

# Build from Ubuntu ISO
UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso \\
./live/build-live.sh

# Optional: bake repo into ISO for offline install
REPO_TARBALL=../dist/freeai-v1.2.0.tar.gz \\
./live/build-live.sh`}
          </pre>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white mb-6">GRUB Boot Menu</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="pb-4 text-gray-400 font-medium">Entry</th>
                  <th className="pb-4 text-gray-400 font-medium">What it does</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {bootMenu.map((entry, i) => (
                  <tr key={i} className="hover:bg-white/5 transition-colors">
                    <td className="py-4 text-white font-medium">{entry.entry}</td>
                    <td className="py-4 text-gray-400">{entry.action}</td>
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
