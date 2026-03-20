import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'build',
  },
  // Expose env vars prefixed with VITE_ (or keep REACT_APP_ via envPrefix)
  envPrefix: ['VITE_', 'REACT_APP_'],
})
