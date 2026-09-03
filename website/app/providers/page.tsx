import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

const providers = [
  { name: 'OpenAI', key: 'OPENAI_API_KEY', models: 'gpt-4o, gpt-4-turbo, gpt-3.5-turbo', tier: 'cloud' },
  { name: 'Anthropic', key: 'ANTHROPIC_API_KEY', models: 'claude-opus-4, claude-sonnet-4, claude-haiku-4', tier: 'cloud' },
  { name: 'Google Gemini', key: 'GEMINI_API_KEY', models: 'gemini-2.0-flash, gemini-2.5-pro', tier: 'cloud' },
  { name: 'Groq', key: 'GROQ_API_KEY', models: 'llama-3.1-405b, mixtral-8x7b', tier: 'cloud' },
  { name: 'OpenRouter', key: 'OPENROUTER_API_KEY', models: '400+ models', tier: 'cloud' },
  { name: 'Venice AI', key: 'VENICE_AI_API_KEY', models: 'gemma-4-uncensored, llama-3.1-405b', tier: 'cloud' },
  { name: 'Agnes AI', key: 'AGNES_API_KEY', models: 'agnes-2.0-flash, agnes-2.0-pro', tier: 'cloud' },
  { name: 'HuggingFace', key: 'HUGGINGFACE_TOKEN', models: 'Open source models', tier: 'cloud' },
  { name: 'DeepSeek', key: 'DEEPSEEK_API_KEY', models: 'deepseek-chat, deepseek-coder', tier: 'cloud' },
  { name: 'Mistral', key: 'MISTRAL_API_KEY', models: 'mistral-large, mistral-medium', tier: 'cloud' },
  { name: 'Cohere', key: 'COHERE_API_KEY', models: 'command-r, command-r-plus', tier: 'cloud' },
  { name: 'Perplexity', key: 'PERPLEXITY_API_KEY', models: 'sonar, sonar-pro', tier: 'cloud' },
]

const localModels = [
  { name: 'qwen3.6-12b', role: 'Primary coder', size: '~7 GB' },
  { name: 'claude-code-9b', role: 'Code specialist', size: '~5 GB' },
  { name: 'qwythos-v2', role: 'Reasoning primary', size: '~5 GB' },
  { name: 'qwable-9b', role: 'General assistant', size: '~5 GB' },
  { name: 'moe-13b', role: 'Fast coder', size: '~8 GB' },
]

export default function Providers() {
  return (
    <div className="min-h-screen bg-[#020617] pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="page-nav-link mb-8 inline-flex" aria-label="Back to home">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            21+ <span className="gradient-text">AI Providers</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Connect to any AI provider with automatic fallback chains. Local and cloud — your choice.
          </p>
        </div>

        {/* Cloud providers */}
        <section className="mb-16">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-blue-400" />
            Cloud Providers
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {providers.map((provider) => (
              <div key={provider.name} className="page-card">
                <h3 className="text-base font-semibold text-white mb-2">{provider.name}</h3>
                <code className="page-code block mb-3">{provider.key}</code>
                <p className="text-slate-400 text-sm">{provider.models}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Local models */}
        <section className="mb-16">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-green-400" />
            Local GGUF Models
          </h2>
          <div className="overflow-x-auto">
            <table className="page-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Role</th>
                  <th>Size</th>
                </tr>
              </thead>
              <tbody>
                {localModels.map((m) => (
                  <tr key={m.name}>
                    <td className="text-blue-400 font-mono text-sm">{m.name}</td>
                    <td className="text-white">{m.role}</td>
                    <td className="text-slate-400">{m.size}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Configuration */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-6">Configuration</h2>
          <div className="page-card">
            <pre className="page-pre">{`# Add to .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AGNES_API_KEY=sk-gE940pJBd02SRt3c8hBZPvQ3RsnM2gM14EuWJO3DkXeSbtb4

# Route to specific model
curl -X POST localhost:8010/route \\
  -H "Content-Type: application/json" \\
  -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'`}</pre>
          </div>
        </section>
      </div>
    </div>
  )
}
