import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { motion } from 'framer-motion'

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
  { port: ':8888', service: 'JupyterLab', desc: 'Interactive Python' },
  { port: ':6080', service: 'Desktop (VNC)', desc: 'XFCE remote desktop' },
]

export default function Deploy() {
  return (
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Deployment <span className="gradient-text">Guide</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Deploy anywhere — bare metal, Docker, Kubernetes, cloud, or Live ISO.
          </p>
        </motion.div>

        <div className="space-y-12">
          {deployMethods.map((method, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-xl bg-white/5 border border-white/10"
            >
              <h2 className="text-2xl font-semibold text-white mb-2">{method.title}</h2>
              <p className="text-gray-400 mb-4">{method.description}</p>
              <pre className="bg-black/50 rounded-lg p-4 text-sm text-green-400 overflow-x-auto font-mono">
                {method.command}
              </pre>
            </motion.div>
          ))}
        </div>

        {/* Hardware Requirements */}
        <motion.section initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mt-16">
          <h2 className="text-2xl font-semibold text-white mb-6">Hardware Requirements</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/10">
                  {['Tier', 'GPU VRAM', 'RAM', 'Storage', 'What Runs'].map((h) => (
                    <th key={h} className="pb-4 text-gray-400 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {hardwareReqs.map((req, i) => (
                  <tr key={i} className="hover:bg-white/5 transition-colors">
                    <td className="py-4 text-white font-medium">{req.tier}</td>
                    <td className="py-4 text-gray-300">{req.vram}</td>
                    <td className="py-4 text-gray-300">{req.ram}</td>
                    <td className="py-4 text-gray-300">{req.storage}</td>
                    <td className="py-4 text-gray-400 text-sm">{req.runs}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.section>

        {/* Service Ports */}
        <motion.section initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mt-16">
          <h2 className="text-2xl font-semibold text-white mb-6">Service Ports</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/10">
                  {['Port', 'Service', 'Description'].map((h) => (
                    <th key={h} className="pb-4 text-gray-400 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {servicePorts.map((port, i) => (
                  <tr key={i} className="hover:bg-white/5 transition-colors">
                    <td className="py-4 text-blue-400 font-mono">{port.port}</td>
                    <td className="py-4 text-white font-medium">{port.service}</td>
                    <td className="py-4 text-gray-400">{port.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.section>
      </div>
    </div>
  )
}
