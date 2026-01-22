import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0', // Listen on all network interfaces
    // https: {
    //   key: fs.readFileSync(path.resolve(__dirname, '../key.pem')),
    //   cert: fs.readFileSync(path.resolve(__dirname, '../cert.pem')),
    // },
    // Proxy configuration if needed (though we use absolute URL in App.jsx now)
  }
})
