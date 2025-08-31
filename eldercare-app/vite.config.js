import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    host: true, // Allow external connections
    allowedHosts: true,// Allow all hosts
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      rewrite: path => path.replace(/^\/api/, ''), 
          },
        },

  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  define: {
    // Vite doesn't automatically load .env variables like CRA
    // So we'll define them here if needed
    global: 'globalThis',
  },
})
