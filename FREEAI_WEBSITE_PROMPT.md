# FREEAI WEBSITE IMPLEMENTATION PROMPT — AGNES 2.5 AI CODER

## PROJECT OVERVIEW
Build a complete, production-ready documentation website for **FreeAI** — a unified AI inference workstation. The site must showcase all 174+ features, deployment methods, and technical capabilities. Target audience: developers, DevOps, security researchers, AI engineers.

---

## CORE REQUIREMENTS

### Technology Stack
- **Framework**: Next.js 14+ with App Router (React 18)
- **Styling**: Tailwind CSS + Framer Motion for animations
- **Language**: TypeScript
- **Deployment**: Vercel (primary), Docker (alternative)
- **Docs Engine**: MDX for content, Algolia for search
- **Theme**: Dark-first with light mode toggle

### Site Structure (10 Pages)
1. `/` — Landing page (hero, features, CTA)
2. `/docs` — Documentation index
3. `/deploy` — Deployment guide (all methods)
4. `/features` — Feature catalog (174+ items)
5. `/agents` — Agent system documentation
6. `/security` — Security features
7. `/providers` — AI provider configuration
8. `/iso` — Live ISO information
9. `/api` — REST API reference
10. `/blog` — Release notes, tutorials

---

## PAGE-BY-PAGE BREAKDOWN

### 1. LANDING PAGE (`/`)

```html
<!-- HERO SECTION -->
<section class="relative min-h-screen overflow-hidden">
  <!-- Background gradient orbs (3 animated) -->
  <div class="hero-orb hero-orb--1" />
  <div class="hero-orb hero-orb--2" />
  <div class="hero-orb hero-orb--3" />
  
  <!-- Content -->
  <div class="container mx-auto px-6 py-24">
    <!-- Eyebrow badge -->
    <div class="eyebrow mb-4">
      <span class="dot bg-green-500"></span>
      v1.2.0 — Autonomous SDLC Agents & Aikido Security
    </div>
    
    <!-- Main headline -->
    <h1 class="text-6xl font-bold leading-tight">
      The AI workstation<br>
      <span class="gradient-text">that thinks ahead.</span>
    </h1>
    
    <!-- Subheadline -->
    <p class="text-xl text-gray-400 mt-6 max-w-2xl">
      FreeAI unifies GPU-optimized model serving, autonomous SDLC agents, 
      security scanning, and builder tools — all in one self-hosted stack.
    </p>
    
    <!-- CTA Buttons -->
    <div class="mt-10 flex gap-4">
      <a href="/deploy" class="btn-primary">
        <svg>...</svg>
        Install FreeAI
      </a>
      <a href="/docs" class="btn-secondary">
        <svg>...</svg>
        Read Docs
      </a>
    </div>
    
    <!-- Stats Grid -->
    <div class="hero-stats grid grid-cols-5 gap-8 mt-20">
      <div class="hero-stat">
        <div class="num text-4xl font-bold">174</div>
        <div class="label">Features</div>
      </div>
      <div class="hero-stat">
        <div class="num text-4xl font-bold">55+</div>
        <div class="label">Skills</div>
      </div>
      <div class="hero-stat">
        <div class="num text-4xl font-bold">24</div>
        <div class="label">Agents</div>
      </div>
      <div class="hero-stat">
        <div class="num text-4xl font-bold">40+</div>
        <div class="label">MCPs</div>
      </div>
      <div class="hero-stat">
        <div class="num text-4xl font-bold">21+</div>
        <div class="label">Providers</div>
      </div>
    </div>
  </div>
</section>

<!-- FEATURE CARDS SECTION -->
<section class="py-24 dot-grid-bg">
  <div class="container mx-auto px-6">
    <div class="section-head">
      <div class="eyebrow">What's Inside</div>
      <h2 class="section-title">One workstation.<br><span class="grad">Every tool you need.</span></h2>
    </div>
    
    <div class="feature-grid">
      <!-- Card 1: Model Router -->
      <div class="feature-card">
        <div class="feature-icon">🔀</div>
        <h3>Model Router</h3>
        <p>Classifies prompts, routes to best backend, automatic fallback chains, LRU cache, 21+ providers.</p>
      </div>
      
      <!-- Card 2: Autonomous Agents -->
      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3>Autonomous Agents</h3>
        <p>7-phase SDLC: plan → code → verify → fix → review → document → package. Real compilation tests.</p>
      </div>
      
      <!-- Card 3: Workflow Engine -->
      <div class="feature-card">
        <div class="feature-icon">⚙️</div>
        <h3>Workflow Engine</h3>
        <p>Visual pipeline designer with validation, templates, audit logs, export/import.</p>
      </div>
      
      <!-- Card 4: Security -->
      <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <h3>Security</h3>
        <p>Aikido integration, pentest agents, auto-patching, 33 security skills (14 Red, 12 Blue, 7 Purple).</p>
      </div>
      
      <!-- Card 5: GPU Inference -->
      <div class="feature-card">
        <div class="feature-icon">🎮</div>
        <h3>GPU Inference</h3>
        <p>llama.cpp (:9001), vLLM (:9002), FreeToken (:9100) — local GGUF serving with 21+ bridges.</p>
      </div>
      
      <!-- Card 6: Live ISO -->
      <div class="feature-card">
        <div class="feature-icon">💿</div>
        <h3>Live ISO</h3>
        <p>Bootable FreeAIOS — Ubuntu/Kodachi/Kali/NixOS with install, live, and rescue modes.</p>
      </div>
    </div>
  </div>
</section>

<!-- DEPLOYMENT METHODS -->
<section class="py-24 bg-elev-2">
  <div class="container mx-auto px-6">
    <h2 class="section-title">Deploy Anywhere</h2>
    
    <div class="deploy-table">
      <table>
        <thead>
          <tr>
            <th>Method</th>
            <th>Command</th>
            <th>Best For</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Bare Metal</strong></td>
            <td><code>curl -fsSL install.sh | bash</code></td>
            <td>Production servers</td>
          </tr>
          <tr>
            <td><strong>Docker Compose</strong></td>
            <td><code>docker compose --profile allinone up -d</code></td>
            <td>Any host with NVIDIA Docker</td>
          </tr>
          <tr>
            <td><strong>Kubernetes</strong></td>
            <td><code>kubectl apply -f k8s/</code></td>
            <td>Cloud-native deployments</td>
          </tr>
          <tr>
            <td><strong>Vast.ai</strong></td>
            <td>Custom template (32GB+ VRAM)</td>
            <td>On-demand GPU instances</td>
          </tr>
          <tr>
            <td><strong>Live ISO</strong></td>
            <td>Boot <code>freeaios-amd64.iso</code></td>
            <td>No-install, bootable workstation</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<!-- ARCHITECTURE DIAGRAM -->
<section class="py-24">
  <div class="container mx-auto px-6">
    <h2 class="section-title">Architecture</h2>
    
    <div class="architecture-diagram">
      <pre class="code-block">
                    ┌───────────────────────────────────────────────────────┐
                    │              FreeAI Dashboard (:8080)                 │
                    │        Flask + Chart.js + SSE + Authentication        │
                    ├───────────────────────────┬────────────────┬──────────┤
                    │  Router  │ Agents    │ Workflow │      Autonomous     │
                    │  :8010   │ :8020     │  :8040   │       :8050         │
                    │          │           │          │                     │
                    │ classify │ plan→code │ chain    │   7-phase SDLC      │
                    │ fallback │ verify    │ validate │   real compilation  │
                    │ cache    │ fix       │ template │   auto-package      │
                    ├───────────────────────────┴────────────────┴──────────┤
                    │              MCP Registry (40+ servers)               │
                    │    Aikido · SendGrid · Twilio · Telegram · WhatsApp   │
                    ├───────────────────────────────────────────────────────┤
                    │                  GPU Inference Layer                  │
                    │ llama.cpp  (:9001) · vLLM (:9002) · FreeToken (:9100) │
                    └───────────────────────────────────────────────────────┘
      </pre>
    </div>
  </div>
</section>

<!-- PROVIDER LOGO MARQUEE -->
<div class="logo-marquee-wrap">
  <div class="logo-marquee">
    <a href="#"><svg>...</svg><span>OpenAI</span></a>
    <a href="#"><svg>...</svg><span>Anthropic</span></a>
    <a href="#"><svg>...</svg><span>llama.cpp</span></a>
    <a href="#"><svg>...</svg><span>vLLM</span></a>
    <a href="#"><svg>...</svg><span>OpenRouter</span></a>
    <a href="#"><svg>...</svg><span>Hermes</span></a>
    <a href="#"><svg>...</svg><span>OpenClaw</span></a>
    <a href="#"><svg>...</svg><span>OpenCode</span></a>
    <a href="#"><svg>...</svg><span>MimoCode</span></a>
    <a href="#"><svg>...</svg><span>JCode</span></a>
    <a href="#"><svg>...</svg><span>ZCode</span></a>
    <a href="#"><svg>...</svg><span>NVIDIA</span></a>
  </div>
</div>
```

### 2. DEPLOY PAGE (`/deploy`)

```html
<!-- DEPLOYMENT METHODS SECTION -->
<section class="py-24">
  <div class="container mx-auto px-6">
    <h1 class="text-4xl font-bold mb-8">Deployment Guide</h1>
    
    <!-- Bare Metal -->
    <div class="deploy-method">
      <h2>Bare Metal Provisioner</h2>
      <code class="block">
        git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git<br>
        cd FreeAI_AI_Inference_Workstation<br>
        sudo ./hardware/install-stack.sh<br>
        bash models/auto-download-models.sh
      </code>
      <p>Auto-detects GPU, installs NVIDIA drivers, CUDA, Docker, configures everything.</p>
    </div>
    
    <!-- Docker Compose -->
    <div class="deploy-method">
      <h2>Docker Compose</h2>
      <code class="block">
        # Split services<br>
        docker compose up -d --build<br><br>
        # All-in-one<br>
        docker compose --profile allinone up -d<br><br>
        # With desktop<br>
        docker compose --profile desktop up -d<br><br>
        # With VLLM<br>
        docker compose --profile vllm up -d
      </code>
    </div>
    
    <!-- Kubernetes -->
    <div class="deploy-method">
      <h2>Kubernetes</h2>
      <code class="block">
        kubectl apply -f k8s/namespace.yml<br>
        kubectl apply -f k8s/models-pvc.yml<br>
        kubectl apply -f k8s/
      </code>
    </div>
    
    <!-- Cloud Providers -->
    <div class="deploy-method">
      <h2>Cloud GPU Providers</h2>
      <table>
        <tr><th>Provider</th><th>Path</th></tr>
        <tr><td>Vast.ai</td><td>template env PROVISIONING_SCRIPT</td></tr>
        <tr><td>RunPod</td><td>Docker template from GHCR</td></tr>
        <tr><td>Lambda / Paperspace</td><td>bare Ubuntu + install-stack.sh</td></tr>
        <tr><td>Hetzner GPU / OVH</td><td>same as Lambda</td></tr>
        <tr><td>AWS g5/g6</td><td>Terraform module (roadmap)</td></tr>
      </table>
    </div>
    
    <!-- Live ISO -->
    <div class="deploy-method">
      <h2>Live ISO (FreeAIOS)</h2>
      <code class="block">
        # Build on any Ubuntu host<br>
        sudo apt-get install -y xorriso isolinux<br>
        UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso ./live/build-live.sh
      </code>
      <p>GRUB boot menu: Try Live / Install to disk / Rescue shell</p>
    </div>
  </div>
</section>

<!-- HARDWARE REQUIREMENTS -->
<section class="py-24 bg-elev-2">
  <div class="container mx-auto px-6">
    <h2>Hardware Requirements</h2>
    <table>
      <tr>
        <th>Tier</th>
        <th>GPU VRAM</th>
        <th>RAM</th>
        <th>Storage</th>
        <th>What Runs</th>
      </tr>
      <tr>
        <td>Floor</td>
        <td>8 GB</td>
        <td>32 GB</td>
        <td>500 GB SSD</td>
        <td>Subset of roster Q4_K (9B-class)</td>
      </tr>
      <tr>
        <td>Recommended</td>
        <td>16 GB</td>
        <td>64 GB DDR5</td>
        <td>1 TB + 2 TB models</td>
        <td>Full 8-model roster Q6_K, 24/7 SDLC</td>
      </tr>
      <tr>
        <td>Headroom</td>
        <td>24 GB</td>
        <td>96-128 GB</td>
        <td>+4 TB models</td>
        <td>Larger coders + vLLM coexistence</td>
      </tr>
    </table>
  </div>
</section>

<!-- SERVICE PORTS TABLE -->
<section class="py-24">
  <div class="container mx-auto px-6">
    <h2>Service Ports</h2>
    <table>
      <tr><th>Service</th><th>Port</th><th>Description</th></tr>
      <tr><td>Dashboard</td><td>:8030</td><td>Web UI + REST API</td></tr>
      <tr><td>Router</td><td>:8010</td><td>AI model routing engine</td></tr>
      <tr><td>Agents</td><td>:8020</td><td>Agent API</td></tr>
      <tr><td>Workflow</td><td>:8040</td><td>Workflow engine</td></tr>
      <tr><td>Autonomous</td><td>:8050</td><td>SDLC automation</td></tr>
      <tr><td>llama.cpp</td><td>:9001</td><td>Local GGUF inference</td></tr>
      <tr><td>vLLM</td><td>:9002</td><td>High-throughput serving</td></tr>
      <tr><td>FreeToken</td><td>:9100</td><td>Edge MoE engine</td></tr>
      <tr><td>JupyterLab</td><td>:8888</td><td>Interactive Python</td></tr>
      <tr><td>Desktop (VNC)</td><td>:6080</td><td>XFCE remote desktop</td></tr>
    </table>
  </div>
</section>
```

### 3. FEATURES PAGE (`/features`)

```html
<!-- FEATURE CATALOG -->
<section class="py-24">
  <div class="container mx-auto px-6">
    <h1 class="text-4xl font-bold mb-12">174 Features</h1>
    
    <!-- Categorize into tabs -->
    <div class="feature-tabs">
      <button class="tab active">All</button>
      <button class="tab">Router</button>
      <button class="tab">Agents</button>
      <button class="tab">Security</button>
      <button class="tab">GPU</button>
      <button class="tab">Workflow</button>
      <button class="tab">Integration</button>
    </div>
    
    <!-- Feature grid -->
    <div class="feature-grid">
      <div class="feature-card">
        <h3>Model Router</h3>
        <ul>
          <li>Keyword classifier with confidence score</li>
          <li>Fallback chain across roster</li>
          <li>Degenerate output detection</li>
          <li>LRU response cache (X-Cache: HIT/MISS)</li>
          <li>Per-client rate limiting (429)</li>
          <li>Optional X-API-Key auth</li>
          <li>/metrics endpoint</li>
        </ul>
      </div>
      
      <div class="feature-card">
        <h3>Agent API</h3>
        <ul>
          <li>project / refactor / debug / analyze endpoints</li>
          <li>Profiles: strict, balanced, creative, verbose, minimal</li>
          <li>Session memory (20 turns x 100 sessions)</li>
          <li>Error envelopes</li>
          <li>Call counters</li>
        </ul>
      </div>
      
      <div class="feature-card">
        <h3>Workflow Engine</h3>
        <ul>
          <li>Registry-based pipelines</li>
          <li>Sequential + parallel steps</li>
          <li>3-attempt retry per step</li>
          <li>Missing-dependency validation</li>
          <li>JSONL audit log</li>
          <li>Export/import definitions</li>
          <li>4 shipped templates</li>
        </ul>
      </div>
      
      <div class="feature-card">
        <h3>Autonomous SDLC</h3>
        <ul>
          <li>7-phase lifecycle: plan→code→test→fix→review→doc→package</li>
          <li>Real verification: compileall, pytest, node --check</li>
          <li>Sandboxed workspaces</li>
          <li>Artifact tarball download</li>
          <li>Run cancellation</li>
          <li>Concurrency cap</li>
        </ul>
      </div>
      
      <div class="feature-card">
        <h3>Security</h3>
        <ul>
          <li>Aikido integration</li>
          <li>Pentest agents</li>
          <li>Auto-patching</li>
          <li>33 security skills (14 Red, 12 Blue, 7 Purple)</li>
          <li>API key rotation (10 keys per provider)</li>
          <li>Semgrep, Bandit, Safety, Trivy</li>
        </ul>
      </div>
      
      <div class="feature-card">
        <h3>GPU Inference</h3>
        <ul>
          <li>llama.cpp (:9001) — GGUF CUDA</li>
          <li>vLLM (:9002) — high throughput</li>
          <li>FreeToken (:9100) — edge MoE 290B+</li>
          <li>Hot model hot-swap (/admin/model-switch)</li>
          <li>MTP speculative decoding</li>
          <li>Parallel hot models (per-GPU CUDA_VISIBLE_DEVICES)</li>
        </ul>
      </div>
    </div>
  </div>
</section>
```

### 4. AGENTS PAGE (`/agents`)

```html
<!-- AGENT SYSTEMS -->
<section class="py-24">
  <div class="container mx-auto px-6">
    <h1 class="text-4xl font-bold mb-8">24 Autonomous Agents</h1>
    
    <div class="agent-grid">
      <!-- Red Team Agents -->
      <div class="agent-section">
        <h2>Red Team (14)</h2>
        <div class="agent-list">
          <div class="agent-card">
            <h3>API Sniffer</h3>
            <p>CDP Network domain interception, endpoint mapping</p>
          </div>
          <div class="agent-card">
            <h3>Cookie Harvester</h3>
            <p>Session harvesting, cookie crafting, Netscape export</p>
          </div>
          <div class="agent-card">
            <h3>Payload Engine</h3>
            <p>Polymorphic AES-256-GCM + XOR encryption, 9 formats</p>
          </div>
          <div class="agent-card">
            <h3>Vuln Scanner</h3>
            <p>nmap, nuclei, sqlmap, ffuf, OWASP ZAP + NIST reports</p>
          </div>
          <div class="agent-card">
            <h3>Brute Force</h3>
            <p>hashcat GPU, rainbow tables, hydra, JWT/ZIP/SSH</p>
          </div>
          <div class="agent-card">
            <h3>Exploitation</h3>
            <p>Metasploit API, privilege escalation, lateral movement</p>
          </div>
        </div>
      </div>
      
      <!-- Blue Team Agents -->
      <div class="agent-section">
        <h2>Blue Team (12)</h2>
        <div class="agent-list">
          <div class="agent-card">
            <h3>SIEM Integration</h3>
            <p>Log aggregation, alert correlation</p>
          </div>
          <div class="agent-card">
            <h3>Forensics</h3>
            <p>Memory dump analysis, timeline reconstruction</p>
          </div>
          <div class="agent-card">
            <h3>Hunting</h3>
            <p>ATT&CK mapping, IoC hunting, persistence detection</p>
          </div>
          <div class="agent-card">
            <h3>Hardening</h3>
            <p>CIS benchmarks, vulnerability remediation</p>
          </div>
          <div class="agent-card">
            <h3>Incident Response</h3>
            <p>Automated containment, evidence preservation</p>
          </div>
        </div>
      </div>
      
      <!-- Purple Team Agents -->
      <div class="agent-section">
        <h2>Purple Team (7)</h2>
        <div class="agent-list">
          <div class="agent-card">
            <h3>SIM</h3>
            <p>Attack simulation, detection validation</p>
          </div>
          <div class="agent-card">
            <h3>Validate</h3>
            <p>Defense testing, gap analysis</p>
          </div>
          <div class="agent-card">
            <h3>Bridge</h3>
            <p>Red→Blue handoff, JIRA ticket generation</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
```

### 5. PROVIDERS PAGE (`/providers`)

```html
<!-- AI PROVIDER MATRIX -->
<section class="py-24">
  <div class="container mx-auto px-6">
    <h1 class="text-4xl font-bold mb-8">21+ AI Providers</h1>
    
    <div class="provider-grid">
      <div class="provider-card">
        <h3>OpenAI</h3>
        <code>OPENAI_API_KEY=sk-...</code>
        <p>Models: gpt-4o, gpt-4-turbo, gpt-3.5-turbo</p>
      </div>
      
      <div class="provider-card">
        <h3>Anthropic</h3>
        <code>ANTHROPIC_API_KEY=sk-ant-...</code>
        <p>Models: claude-opus-4, claude-sonnet-4, claude-haiku-4</p>
      </div>
      
      <div class="provider-card">
        <h3>Google Gemini</h3>
        <code>GEMINI_API_KEY=...</code>
        <p>Models: gemini-2.0-flash, gemini-2.5-pro</p>
      </div>
      
      <div class="provider-card">
        <h3>Groq</h3>
        <code>GROQ_API_KEY=gsk_...</code>
        <p>Models: llama-3.1-405b, mixtral-8x7b</p>
      </div>
      
      <div class="provider-card">
        <h3>OpenRouter</h3>
        <code>OPENROUTER_API_KEY=...</code>
        <p>400+ models from all providers</p>
      </div>
      
      <div class="provider-card">
        <h3>Venice AI</h3>
        <code>VENICE_AI_API_KEY=...</code>
        <p>Uncensored models: gemma-4-uncensored, llama-3.1-405b</p>
      </div>
      
      <div class="provider-card">
        <h3>Agnes AI</h3>
        <code>AGNES_API_KEY=sk-...</code>
        <p>Models: agnes-2.0-flash, agnes-2.0-pro</p>
      </div>
      
      <div class="provider-card">
        <h3>HuggingFace</h3>
        <code>HUGGINGFACE_TOKEN=...</code>
        <p>Open source models via HF API</p>
      </div>
    </div>
    
    <!-- Provider Configuration -->
    <div class="config-section">
      <h2>Configuration</h2>
      <code class="block">
        # Add to .env<br>
        OPENAI_API_KEY=sk-...<br>
        ANTHROPIC_API_KEY=sk-ant-...<br>
        AGNES_API_KEY=sk-gE940pJBd02SRt3c8hBZPvQ3RsnM2gM14EuWJO3DkXeSbtb4<br><br>
        
        # Route to specific model<br>
        curl -X POST localhost:8010/route \<br>
          -H "Content-Type: application/json" \<br>
          -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'
      </code>
    </div>
  </div>
</section>
```

### 6. ISO PAGE (`/iso`)

```html
<!-- LIVE ISO INFORMATION -->
<section class="py-24">
  <div class="container mx-auto px-6">
    <h1 class="text-4xl font-bold mb-8">FreeAIOS — Live ISO</h1>
    
    <div class="iso-grid">
      <div class="iso-card">
        <h3>Ubuntu 24.04 XFCE</h3>
        <p>Default desktop environment with full FreeAI stack pre-loaded.</p>
        <code>Try Live / Install / Rescue</code>
      </div>
      
      <div class="iso-card">
        <h3>Kali Linux Rolling</h3>
        <p>Full penetration-testing suite with networking preserved.</p>
        <code>Try Kali Live</code>
      </div>
      
      <div class="iso-card">
        <h3>Kodachi Linux</h3>
        <p>Security-focused distro — Kali hardened with extra privacy tools.</p>
        <code>Try Kodachi Live</code>
      </div>
      
      <div class="iso-card">
        <h3>Debian 12</h3>
        <p>Stable base with XFCE desktop and FreeAI tools.</p>
        <code>Try Debian Live</code>
      </div>
      
      <div class="iso-card">
        <h3>NixOS Minimum</h3>
        <p>Declarative, reproducible, secure by default.</p>
        <code>Try NixOS Live</code>
      </div>
    </div>
    
    <!-- Build Instructions -->
    <div class="build-section">
      <h2>Build Your Own ISO</h2>
      <code class="block">
        # Requirements<br>
        sudo apt-get install -y xorriso isolinux<br><br>
        
        # Build from Ubuntu ISO<br>
        UBUNTU_ISO=ubuntu-24.04.2-live-server-amd64.iso \<br>
        ./live/build-live.sh<br><br>
        
        # Optional: bake repo into ISO for offline install<br>
        REPO_TARBALL=../dist/freeai-v1.2.0.tar.gz \<br>
        ./live/build-live.sh
      </code>
    </div>
    
    <!-- Boot Menu -->
    <div class="boot-menu-section">
      <h2>GRUB Boot Menu</h2>
      <table>
        <tr><th>Entry</th><th>What it does</th></tr>
        <tr><td>FreeAIOS Live</td><td>Standard live session with all FreeAI tools</td></tr>
        <tr><td>Install FreeAI</td><td>Unattended Subiquity install, first-boot provision</td></tr>
        <tr><td>Try Ubuntu Server</td><td>Stock live session (RAM)</td></tr>
        <tr><td>Try Kali Linux</td><td>Kali XFCE rolling live mode</td></tr>
        <tr><td>Try NixOS</td><td>NixOS minimal live session</td></tr>
        <tr><td>Rescue shell</td><td>Live session into rescue target</td></tr>
      </table>
    </div>
  </div>
</section>
```

### 7. API REFERENCE PAGE (`/api`)

```html
<!-- API REFERENCE -->
<section class="py-24">
  <div class="container mx-auto px-6">
    <h1 class="text-4xl font-bold mb-8">REST API Reference</h1>
    
    <!-- Router API -->
    <div class="api-section">
      <h2>Router API (:8010)</h2>
      <table>
        <tr><th>Method</th><th>Path</th><th>Notes</th></tr>
        <tr><td>GET</td><td>/health</td><td>Liveness + mock flag</td></tr>
        <tr><td>GET</td><td>/models</td><td>Roster: name/role/strengths/endpoint</td></tr>
        <tr><td>POST</td><td>/route</td><td>{prompt, max_tokens?, temperature?, agent?}</td></tr>
        <tr><td>GET</td><td>/metrics</td><td>Counters, per-task/model, latency_avg_ms</td></tr>
      </table>
      
      <h3>Example Request</h3>
      <code class="block">
        curl -X POST localhost:8010/route \<br>
          -H "Content-Type: application/json" \<br>
          -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'<br><br>
        // Response:<br>
        {<br>
          "model_used": "openai/gpt-4o-mini",<br>
          "task_type": "general_code",<br>
          "confidence": 0.87,<br>
          "elapsed_ms": 342,<br>
          "response": "..."<br>
        }
      </code>
    </div>
    
    <!-- Agent API -->
    <div class="api-section">
      <h2>Agent API (:8020)</h2>
      <table>
        <tr><th>Method</th><th>Path</th></tr>
        <tr><td>POST</td><td>/agent/project</td></tr>
        <tr><td>POST</td><td>/agent/refactor</td></tr>
        <tr><td>POST</td><td>/agent/debug</td></tr>
        <tr><td>POST</td><td>/agent/analyze</td></tr>
        <tr><td>POST</td><td>/agent/orchestrate</td></tr>
        <tr><td>POST</td><td>/agent/chat</td></tr>
        <tr><td>GET/DELETE</td><td>/memory/{session_id}</td></tr>
      </table>
    </div>
    
    <!-- Autonomous SDLC API -->
    <div class="api-section">
      <h2>Autonomous SDLC (:8050)</h2>
      <table>
        <tr><th>Method</th><th>Path</th></tr>
        <tr><td>POST</td><td>/auto/start</td></tr>
        <tr><td>GET</td><td>/auto/runs</td></tr>
        <tr><td>GET</td><td>/auto/runs/{id}</td></tr>
        <tr><td>POST</td><td>/auto/runs/{id}/cancel</td></tr>
        <tr><td>GET</td><td>/auto/runs/{id}/artifact</td></tr>
        <tr><td>POST</td><td>/auto/runs/{id}/shell</td></tr>
      </table>
    </div>
  </div>
</section>
```

---

## MACOS SUPPORT

### System Requirements
- macOS 12.0 (Monterey) or later
- Apple Silicon (M1/M2/M3) or Intel x86_64
- 16GB RAM minimum (32GB recommended)
- 50GB free storage

### Installation Methods

#### Method 1: Docker Desktop (Recommended)
```bash
# 1. Install Docker Desktop
brew install --cask docker

# 2. Clone repository
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation

# 3. Run with Docker Compose (CPU-only mode)
MOCK_LLM=1 docker compose --profile allinone up -d

# 4. Open dashboard
open http://localhost:8030
```

#### Method 2: Native Installation (Apple Silicon)
```bash
# 1. Install Homebrew packages
brew install python@3.11 gcc cmake ninja

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run in mock mode (no GPU)
MOCK_LLM=1 python3 router/router.py &
MOCK_LLM=1 python3 agents/api.py &
MOCK_LLM=1 python3 dashboard/backend.py &
```

#### Method 3: Without GPU (CPU Only)
```bash
# Set environment variable
export MOCK_LLM=1

# Run single command startup
python3 launch.py --mock
```

### macOS-Specific Notes
- **No NVIDIA CUDA**: GPU inference requires Linux. Use `MOCK_LLM=1` for CPU-only development
- **Docker Desktop**: Use colima for lighter footprint: `brew install colima`
- **ARM64 builds**: llama.cpp and vLLM support Apple Silicon via Metal (experimental)

---

## WINDOWS 10/11 SUPPORT

### System Requirements
- Windows 10/11 (64-bit)
- WSL2 (Windows Subsystem for Linux 2) REQUIRED
- 16GB RAM minimum
- NVIDIA GPU with CUDA 12.x support (optional for GPU inference)

### Installation via WSL2

#### Step 1: Install WSL2
```powershell
# Run as Administrator in PowerShell
wsl --install
# Restart computer when prompted
```

#### Step 2: Install Ubuntu in WSL
```bash
# Open WSL terminal
wsl --install -d Ubuntu-22.04
```

#### Step 3: Install FreeAI in WSL
```bash
# Update WSL
wsl --update

# Enter WSL
wsl

# Clone and install
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation
sudo ./hardware/install-stack.sh
```

### Windows Native (Alternative)
```powershell
# 1. Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop/

# 2. Enable WSL2 backend in Docker settings

# 3. Clone repository
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation

# 4. Run with Docker Compose
docker compose --profile allinone up -d

# 5. Access dashboard
Start-Process "http://localhost:8030"
```

### Windows GPU Support
- **NVIDIA Driver**: Install latest from nvidia.com
- **CUDA Toolkit**: Version 12.x required
- **WSL2 GPU passthrough**: Enable with `wsl --set-version Ubuntu-22.04 2`

---

## TECHNICAL SPECIFICATIONS

### Color Palette
```css
:root {
  --primary: #0241e3;
  --primary-hover: #0137c4;
  --primary-soft: rgba(2, 65, 227, .1);
  --success: #16A34A;
  --warning: #D97706;
  --danger: #DC2626;
  --bg: #060a18;
  --bg-elev-1: #0e1630;
  --bg-elev-2: #121b3a;
  --text-primary: #f1f6ff;
  --text-secondary: #c9d3e8;
}
```

### Typography
- **Primary Font**: Outfit (weights: 300, 400, 500, 600, 700, 800)
- **Mono Font**: JetBrains Mono (weights: 400, 500)
- **Sizes**: Display (56px), H1 (40px), H2 (28px), Body (15px), Small (13px)

### Animations
- **Scroll reveal**: IntersectionObserver-based fade-in
- **Marquee**: CSS animation for logo scroll
- **Hover effects**: Transform + shadow transitions
- **Stats counter**: requestAnimationFrame easing

---

## DELIVERABLES

1. **Complete Next.js project** with all 10 pages
2. **TypeScript types** for all data structures
3. **Responsive design** (mobile, tablet, desktop)
4. **Dark/light theme** toggle
5. **i18n support** (English, Spanish, German, French, Japanese, Arabic)
6. **Algolia search** integration
7. **SEO optimization** (meta tags, sitemap, robots.txt)
8. **Performance**: Lighthouse score >90
9. **Accessibility**: WCAG 2.1 AA compliance
10. **Deployment configs**: Vercel, Docker, GitHub Actions

---

## IMPLEMENTATION NOTES

- Use **Framer Motion** for scroll animations
- Use **React Query** for data fetching
- Use **Zod** for form validation
- Use **Lucide React** for icons
- Use **shadcn/ui** for component primitives
- Use **Tailwind CSS** for styling
- Use **ESLint** + **Prettier** for code quality
- Use **Jest** + **Playwright** for testing

---

## SUCCESS CRITERIA

- [ ] All 174 features documented
- [ ] All deployment methods covered
- [ ] macOS instructions accurate and tested
- [ ] Windows 10/11 WSL2 instructions accurate and tested
- [ ] Live ISO variants documented (Kali, Kodachi, Ubuntu, Debian, NixOS)
- [ ] API reference complete
- [ ] Mobile responsive
- [ ] Dark/light theme working
- [ ] Search functionality working
- [ ] All links functional
- [ ] Lighthouse score >90

---

**END OF PROMPT**
