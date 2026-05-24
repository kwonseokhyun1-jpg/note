import path from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import type { ProxyOptions } from 'vite'

// GitHub Pages serves project sites at /repo-name/
const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1]
const base = repoName ? `/${repoName}/` : '/'

function createProxies(openaiKey: string | undefined, groqKey: string | undefined) {
  const redditProxy: ProxyOptions = {
    target: 'https://www.reddit.com',
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api\/reddit/, ''),
    headers: {
      'User-Agent': 'CommanderHelper/1.0 (MTG deck tool)',
    },
  }

  const tcgplayerProxy: ProxyOptions = {
    target: 'https://infinite-api.tcgplayer.com',
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api\/tcgplayer/, ''),
    headers: {
      Origin: 'https://www.tcgplayer.com',
      Referer: 'https://www.tcgplayer.com/',
    },
  }

  const openaiProxy: ProxyOptions = {
    target: 'https://api.openai.com/v1',
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api\/openai/, ''),
    configure: (proxy) => {
      proxy.on('proxyReq', (proxyReq) => {
        if (openaiKey) {
          proxyReq.setHeader('Authorization', `Bearer ${openaiKey}`)
        }
      })
    },
  }

  const groqProxy: ProxyOptions = {
    target: 'https://api.groq.com/openai/v1',
    changeOrigin: true,
    rewrite: (path: string) =>
      path.replace(/^\/api\/groq(?:\/chat\/completions)?\/?$/, '/chat/completions'),
    configure: (proxy) => {
      proxy.on('proxyReq', (proxyReq) => {
        if (groqKey) {
          proxyReq.setHeader('Authorization', `Bearer ${groqKey}`)
        }
      })
    },
  }

  return {
    '/api/reddit': redditProxy,
    '/api/tcgplayer': tcgplayerProxy,
    '/api/openai': openaiProxy,
    '/api/groq': groqProxy,
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const openaiKey = env.VITE_OPENAI_API_KEY?.trim() || env.OPENAI_API_KEY?.trim()
  const groqKey = env.GROQ_API_KEY?.trim()
  const proxy = createProxies(openaiKey, groqKey)

  return {
    base,
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@mtg': path.resolve(__dirname, './src'),
        '@mtgminigames': path.resolve(__dirname, '../mtgminigames/src'),
      },
    },
    server: { proxy },
    preview: { proxy },
  }
})
