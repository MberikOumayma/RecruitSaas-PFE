import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      // Même origine que le front : évite le blocage CORS pour le GLB (Three.js charge depuis 5173)
      '/avatars': {
        target: 'http://localhost:5202',
        changeOrigin: true
      }
    }
  }
})