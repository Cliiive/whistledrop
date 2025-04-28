import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,  // 👈 Always use port 3000
    strictPort: true, // 👈 Crash if port 3000 is unavailable, don't pick random port
  }
})
