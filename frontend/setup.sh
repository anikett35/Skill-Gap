#!/bin/bash
# ============================================================
# SkillGap Engine v3 — Complete Frontend Setup Script
# Run from: A:/skill/SkillGap-Analyzer/frontend/
# Usage: bash setup.sh
# ============================================================

set -e
echo ""
echo "=================================================="
echo "  SkillGap Engine v3 — Frontend Setup"
echo "=================================================="
echo ""

# ── 1. Write package.json with Tailwind + Vite ──────────────
echo "[1/7] Writing package.json..."
cat > package.json << 'EOF'
{
  "name": "skillgap-v3-frontend",
  "version": "3.0.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.23.1",
    "@tanstack/react-query": "^5.40.0",
    "axios": "^1.7.2",
    "recharts": "^2.12.7",
    "lucide-react": "^0.383.0",
    "react-hot-toast": "^2.4.1",
    "clsx": "^2.1.1",
    "date-fns": "^3.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.3.0",
    "tailwindcss": "^3.4.4",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.39"
  },
  "scripts": {
    "start": "vite",
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
EOF
echo "  ✓ package.json"

# ── 2. Write vite.config.js ──────────────────────────────────
echo "[2/7] Writing vite.config.js..."
cat > vite.config.js << 'EOF'
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: "build",
  },
  envPrefix: ["VITE_", "REACT_APP_"],
})
EOF
echo "  ✓ vite.config.js"

# ── 3. Write tailwind.config.js ──────────────────────────────
echo "[3/7] Writing tailwind.config.js..."
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF
echo "  ✓ tailwind.config.js"

# ── 4. Write postcss.config.js ───────────────────────────────
echo "[4/7] Writing postcss.config.js..."
cat > postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF
echo "  ✓ postcss.config.js"

# ── 5. Write index.html ───────────────────────────────────────
echo "[5/7] Writing index.html..."
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SkillGap Engine v3</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF
echo "  ✓ index.html"

# ── 6. Write src/main.jsx ─────────────────────────────────────
echo "[6/7] Writing src/main.jsx..."
mkdir -p src
cat > src/main.jsx << 'EOF'
import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App.jsx"
import "./styles/globals.css"

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
EOF
echo "  ✓ src/main.jsx"

# ── 7. Write globals.css with Tailwind directives ────────────
echo "[7/7] Writing src/styles/globals.css..."
mkdir -p src/styles
cat > src/styles/globals.css << 'EOF'
/* @import MUST be first — before any @tailwind directives */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

/* ── Design Tokens ──────────────────────────────────────── */
:root {
  --font-sans: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'DM Mono', monospace;
}

/* ── Base ───────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-font-smoothing: antialiased; }
body { font-family: var(--font-sans); background-color: #f9fafb; color: #111827; line-height: 1.5; }
a { text-decoration: none; color: inherit; }
button { cursor: pointer; font-family: inherit; }
input, textarea, select { font-family: inherit; }

/* ── Scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
EOF
echo "  ✓ src/styles/globals.css"

# ── Write .env ────────────────────────────────────────────────
cat > .env << 'EOF'
REACT_APP_API_URL=http://localhost:8000/api
EOF
echo "  ✓ .env"

# ── Install dependencies ───────────────────────────────────
echo ""
echo "=================================================="
echo "  Installing npm packages (this takes ~1 min)..."
echo "=================================================="
npm install

echo ""
echo "=================================================="
echo "  ✅ Setup complete!"
echo "=================================================="
echo ""
echo "  Start the app:   npm start"
echo "  Opens at:        http://localhost:3000"
echo ""
