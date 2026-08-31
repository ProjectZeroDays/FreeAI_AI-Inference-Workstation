import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'
import { motion } from 'framer-motion'

const posts = [
  {
    title: 'FreeAI v1.2.0 Released',
    date: 'August 31, 2026',
    excerpt: 'Autonomous SDLC agents, Aikido security scanning, and 174+ features.',
    tag: 'Release',
  },
  {
    title: 'Building the Model Router',
    date: 'August 28, 2026',
    excerpt: 'How we built a classifier that routes prompts to the best backend automatically.',
    tag: 'Technical',
  },
  {
    title: 'Security Through Automation',
    date: 'August 25, 2026',
    excerpt: 'Using AI agents for continuous security assessment and automatic patching.',
    tag: 'Security',
  },
  {
    title: 'Live ISO: FreeAIOS',
    date: 'August 20, 2026',
    excerpt: 'Bootable workstation with Ubuntu, Kali, Kodachi, Debian, and NixOS variants.',
    tag: 'Product',
  },
]

export default function Blog() {
  return (
    <div className="min-h-screen bg-navy-900 pt-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8">
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            <span className="gradient-text">Blog</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Latest updates, tutorials, and technical deep dives.
          </p>
        </motion.div>

        <div className="space-y-6">
          {posts.map((post, i) => (
            <motion.article
              key={post.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-6 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-all"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-primary/20 text-primary">
                  {post.tag}
                </span>
                <span className="text-gray-500 text-sm">{post.date}</span>
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">{post.title}</h2>
              <p className="text-gray-400 text-sm">{post.excerpt}</p>
              <Link href="#" className="inline-block mt-4 text-primary hover:text-primary-hover text-sm font-medium transition-colors">
                Read more →
              </Link>
            </motion.article>
          ))}
        </div>
      </div>
    </div>
  )
}
