# Deploy

## GitHub Pages

Live site: **https://kwonseokhyun1-jpg.github.io/commanderhelper/**

1. [Settings → Pages](https://github.com/kwonseokhyun1-jpg/commanderhelper/settings/pages) → **Source: GitHub Actions**
2. Push to `main` or run **Deploy to GitHub Pages** in Actions

## Vercel (edhhelp)

Live site: **https://edhhelp.vercel.app/**

Project: [edhhelp → Build and Deployment](https://vercel.com/kwonseokhyun1-jpgs-projects/edhhelp/settings/build-and-deployment)

### 1. Git (Settings → Git)

| Field | Value |
|-------|-------|
| Repository | `kwonseokhyun1-jpg/commanderhelper` |
| Production Branch | `main` |

If this points at a different repo, pushes to `commanderhelper` will never update edhhelp.

### 2. Build and Deployment

Use **one** of these setups. Turn **Override** on for each field you set manually.

#### Option A — recommended (repo root, uses `/vercel.json`)

| Field | Value |
|-------|-------|
| Framework Preset | **Other** (not Vite — Vite-only deploys skip `/api` functions) |
| Root Directory | *(leave empty)* |
| Install Command | `npm ci --prefix mtg` |
| Build Command | `npm run build --prefix mtg` |
| Output Directory | `mtg/dist` |
| Node.js Version | 22.x |

Groq serverless function: `/api/groq.ts` at repo root.

#### Option B (subdirectory)

| Field | Value |
|-------|-------|
| Framework Preset | **Other** |
| Root Directory | `mtg` |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Node.js Version | 22.x |

Groq serverless function: `mtg/api/groq.ts`.

### 3. Environment Variables (Settings → Environment Variables)

| Name | Environments |
|------|----------------|
| `GROQ_API_KEY` | Production, Preview, Development |

### 4. Redeploy

After changing settings: **Deployments** → latest → **Redeploy** (not just cache refresh).

### 5. Verify Groq proxy

```powershell
Invoke-WebRequest -Uri "https://edhhelp.vercel.app/api/groq" -Method POST `
  -Body '{"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":"hi"}]}' `
  -ContentType "application/json"
```

| Response | Meaning |
|----------|---------|
| JSON with `"choices"` | Working |
| JSON `"GROQ_API_KEY is not configured"` | Function works — add the env var |
| JSON `"Method not allowed"` on GET | Function works — use POST |
| HTML (`<!doctype html>`) | Still static-only — check Framework = **Other** and Root Directory |

Also confirm the main JS bundle hash changed after redeploy (not still `index-CWMM_PVl.js`).

## Local development

```bash
cd mtg
npm install
npm run dev
```

## Optional: AI keys

| Key | Used for | Where |
|-----|----------|-------|
| `GROQ_API_KEY` | Assistant tab | `mtg/.env.local` (dev) + Vercel env vars (production) |
| `VITE_OPENAI_API_KEY` | Deck review in editor | `.env.local` (local dev only) |

GitHub Pages is static only — the Assistant needs Vercel (or local dev) for the Groq proxy.
