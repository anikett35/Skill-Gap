# Run this from: A:\skill\SkillGap-Analyzer\frontend\
# In PowerShell: .\setup-frontend.ps1

Write-Host "=== SkillGap v3 Frontend Fix ===" -ForegroundColor Cyan

# 1. Write index.html at the frontend root
$indexHtml = @'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SkillGap Engine v3</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
'@
Set-Content -Path "index.html" -Value $indexHtml
Write-Host "[OK] index.html created" -ForegroundColor Green

# 2. Write src/main.jsx
$mainJsx = @'
import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App.jsx"
import "./styles/globals.css"

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
'@
Set-Content -Path "src\main.jsx" -Value $mainJsx
Write-Host "[OK] src/main.jsx created" -ForegroundColor Green

# 3. Write vite.config.js
$viteConfig = @'
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
'@
Set-Content -Path "vite.config.js" -Value $viteConfig
Write-Host "[OK] vite.config.js created" -ForegroundColor Green

# 4. Write .env
Set-Content -Path ".env" -Value "REACT_APP_API_URL=http://localhost:8000/api"
Write-Host "[OK] .env created" -ForegroundColor Green

# 5. Write package.json with Vite
$packageJson = @'
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
    "vite": "^5.3.0"
  },
  "scripts": {
    "start": "vite",
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
'@
Set-Content -Path "package.json" -Value $packageJson
Write-Host "[OK] package.json updated" -ForegroundColor Green

Write-Host ""
Write-Host "=== Now run: ===" -ForegroundColor Yellow
Write-Host "  npm install" -ForegroundColor White
Write-Host "  npm start" -ForegroundColor White
Write-Host ""
Write-Host "App will open at http://localhost:3000" -ForegroundColor Cyan
