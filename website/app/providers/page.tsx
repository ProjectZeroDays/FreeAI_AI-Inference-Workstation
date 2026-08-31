import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

const providers = [
  { name: 'OpenAI', key: 'OPENAI_API_KEY', models: 'gpt-4o, gpt-4-turbo, gpt-3.5-turbo' },
  { name: 'Anthropic', key: 'ANTHROPIC_API_KEY', models: 'claude-opus-4, claude-sonnet-4, claude-haiku-4' },
  { name: 'Google Gemini', key: 'GEMINI_API_KEY', models: 'gemini-2.0-flash, gemini-2.5-pro' },
  { name: 'Groq', key: 'GROQ_API_KEY', models: 'llama-3.1-405b, mixtral-8x7b' },
  { name: 'OpenRouter', key: 'OPENROUTER_API_KEY', models: '400+ models' },
  { name: 'Venice AI', key: 'VENICE_AI_API_KEY', models: 'gemma-4-uncensored, llama-3.1-405b' },
  { name: 'Agnes AI', key: 'AGNES_API_KEY', models: 'agnes-2.0-flash, agnes-2.0-pro' },
  { name: 'HuggingFace', key: 'HUGGINGFACE_TOKEN', models: 'Open source models' },
  { name: 'DeepSeek', key: 'DEEPSEEK_API_KEY', models: 'deepseek-chat, deepseek-coder' },
  { name: 'Mistral', key: 'MISTRAL_API_KEY', models: 'mistral-large, mistral-medium' },
  { name: 'Cohere', key: 'COHERE_API_KEY', models: 'command-r, command-r-plus' },
  { name: 'Perplexity', key: 'PERPLEXITY_API_KEY', models: 'sonar, sonar-pro' },
]

export default function Providers() {
  return (
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            21+ <span className="gradient-text">AI Providers</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Connect to any AI provider with automatic fallback chains.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {providers.map((provider) => (
            <div key={provider.name} className="p-6 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all">
              <h3 className="text-lg font-semibold text-white mb-2">{provider.name}</h3>
              <code className="text-xs text-blue-400 bg-blue-500/10 px-2 py-1 rounded block mb-3">
                {provider.key}
              </code>
              <p className="text-gray-400 text-sm">{provider.models}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 p-6 rounded-xl bg-white/5 border border-white/10">
          <h2 className="text-xl font-semibold text-white mb-4">Configuration</h2>
          <pre className="bg-black/50 rounded-lg p-4 text-sm text-green-400 overflow-x-auto font-mono">
{`# Add to .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AGNES_API_KEY=sk-gE940pJBd02SRt3c8hBZPvQ3RsnM2gM14EuWJO3DkXeSbtb4

# Route to specific model
curl -X POST localhost:8010/route \\
  -H "Content-Type: application/json" \\
  -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'`}
          </pre>
        </div>
      </div>
    </div>
  )
}
