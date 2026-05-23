# Memo — Multipurpose Notes App

A React notes app with tags, colors, pinning, archiving, checklists, and local storage.

## Setup

1. Install [Node.js](https://nodejs.org/) (LTS recommended).
2. In this folder, run:

```bash
npm install
npm run dev
```

3. Open the URL shown in the terminal (usually `http://localhost:5173`).

## Build for production

```bash
npm run build
npm run preview
```

## Deploy to GitHub Pages

This repo includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that builds and deploys on every push to `main`.

### One-time setup

1. **Create a GitHub repo** (e.g. `memo-notes`) at [github.com/new](https://github.com/new). Do not add a README if you already have one locally.

2. **Push this project** (install [Git](https://git-scm.com/) if needed):

```bash
cd path/to/website
git init
git add .
git commit -m "Initial commit: Memo notes app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/memo-notes.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `memo-notes` with your GitHub username and repo name.

3. **Enable GitHub Pages** on the repo:
   - Go to **Settings → Pages**
   - Under **Build and deployment**, set **Source** to **GitHub Actions**

4. After the workflow finishes (Actions tab), your site will be live at:

   `https://YOUR_USERNAME.github.io/memo-notes/`

The build sets the correct asset paths from your repo name automatically. If you rename the repo, push again—the next deploy will use the new URL.

To deploy manually without waiting for a push: **Actions → Deploy to GitHub Pages → Run workflow**.

## Features

- Create, edit, and delete notes
- Pin important notes to the top
- Tag notes and filter by tag
- Color-code notes
- Archive notes you want out of the main list
- Search by title or body
- Checklist mode for todo-style memos
- Auto-saves to your browser (localStorage)
