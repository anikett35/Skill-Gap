#!/bin/bash
# Run from A:/skill/SkillGap-Analyzer/frontend/
# Fixes: @import must precede all other statements

cat > src/styles/globals.css << 'EOF'
/* @import MUST be first — before @tailwind directives */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --font-sans: 'DM Sans', system-ui, sans-serif;
  --font-mono: 'DM Mono', monospace;
}

*, *::before, *::after { box-sizing: border-box; }
html { -webkit-font-smoothing: antialiased; }
body { font-family: var(--font-sans); background-color: #f9fafb; color: #111827; line-height: 1.5; }
a { text-decoration: none; color: inherit; }
button { cursor: pointer; font-family: inherit; }
input, textarea, select { font-family: inherit; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
EOF

echo "✓ globals.css fixed — run: npm start"
