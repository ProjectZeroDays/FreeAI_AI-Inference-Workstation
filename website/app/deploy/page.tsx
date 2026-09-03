import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

const deployMethods = [
  {
    title: 'Bare Metal Provisioner',
    command: `git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation
sudo ./hardware/install-stack.sh
bash models/auto-download-models.sh`,
    description: 'Auto-detects GPU, installs NVIDIA drivers, CUDA, Docker, configures everything.',
  },
  {
    title: 'Docker Compose',
    command: `# Split services
docker compose up -d --build

# All-in-one
docker compose --profile allinone up -d

# With desktop
docker compose --profile desktop up -d

# With VLLM
docker compose --profile vllm up -d`,
    description: 'Any host with NVIDIA Docker support.',
  },
  {
    title: 'Kubernetes',
    command: `kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/models-pvc.yml
kubectl apply -f k8s/`,
    description: 'Cloud-native deployments with GPU support.',
  },
  {
    title: 'Cloud GPU Providers',
    command: `# Vast.ai
template env PROVISIONING_SCRIPT=<release bundle URL>

# RunPod
Docker template from GHCR all-in-one image

# Lambda / Paperspace
bare Ubuntu + install-stack.sh`,
    description: 'On-demand GPU instances from major providers.',
  },
  {
    title: 'Live ISO (FreeAIOS)',
    command: `# Build on any Ubuntu host
sudo apt-get install -y xorriso isolinux
UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso ./live/build-live.sh`,
    description: 'GRUB boot menu: Try Live / Install to disk / Rescue shell.',
  },
]

const hardwareReqs = [
  { tier: 'Floor', vram: '8 GB', ram: '32 GB', storage: '500 GB SSD', runs: 'Subset of roster Q4_K (9B-class)' },
  { tier: 'Recommended', vram: '16 GB', ram: '64 GB DDR5', storage: '1 TB + 2 TB models', runs: 'Full 8-model roster Q6_K, 24/7 SDLC' },
  { tier: 'Headroom', vram: '24 GB', ram: '96-128 GB', storage: '+4 TB models', runs: 'Larger coders + vLLM coexistence' },
]

const servicePorts = [
  { port: ':8030', service: 'Dashboard', desc: 'Web UI + REST API' },
  { port: ':8010', service: 'Router', desc: 'AI model routing engine' },
  { port: ':8020', service: 'Agents', desc: 'Agent API' },
  { port: ':8040', service: 'Workflow', desc: 'Workflow engine' },
  { port: ':8050', service: 'Autonomous', desc: 'SDLC automation' },
  { port: ':9001', service: 'llama.cpp', desc: 'Local GGUF inference' },
  { port: ':9002', service: 'vLLM', desc: 'High-throughput serving' },
  { port: ':9100', service: 'FreeToken', desc: 'Edge MoE engine' },
]

export default function Deploy() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Deployment <span className="gradient-text">Guide</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Deploy anywhere — bare metal, Docker, Kubernetes, cloud, or Live ISO.
          </p>
        </div>

        <div className="space-y-8 mb-16">
          {deployMethods.map((method, i) => (
            <div key={i} className="page-card">
              <h2 className="text-xl font-semibold text-white mb-2">{method.title}</h2>
              <p className="text-slate-400 mb-4 text-sm">{method.description}</p>
              <pre className="page-pre">{method.command}</pre>
            </div>
          ))}
        </div>

        {/* Hardware Requirements */}
        <section className="mb-16">
          <h2 className="text-2xl font-semibold text-white mb-6">Hardware Requirements</h2>
          <div className="overflow-x-auto">
            <table className="page-table">
              <thead>
                <tr>
                  {['Tier', 'GPU VRAM', 'RAM', 'Storage', 'What Runs'].map((h) => (
                    <th key={h}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {hardwareReqs.map((req, i) => (
                  <tr key={i}>
                    <td className="text-white font-medium">{req.tier}</td>
                    <td className="text-slate-300">{req.vram}</td>
                    <td className="text-slate-300">{req.ram}</td>
                    <td className="text-slate-300">{req.storage}</td>
                    <td className="text-slate-400 text-sm">{req.runs}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Service Ports */}
        <section>
          <h2 className="text-2xl font-semibold text-white mb-6">Service Ports</h2>
          <div className="overflow-x-auto">
            <table className="page-table">
              <thead>
                <tr>
                  {['Port', 'Service', 'Description'].map((h) => (
                    <th key={h}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {servicePorts.map((port, i) => (
                  <tr key={i}>
                    <td className="text-blue-400 font-mono">{port.port}</td>
                    <td className="text-white font-medium">{port.service}</td>
                    <td className="text-slate-400">{port.desc}</td>
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
