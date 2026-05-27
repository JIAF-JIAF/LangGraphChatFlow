import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteExternalsPlugin } from 'vite-plugin-externals'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export default defineConfig({
  plugins: [
    react(),
    viteExternalsPlugin({
      'react': 'React',
      'react-dom': 'ReactDOM',
      '@ali/react-zongheng': 'ZONGHENG'
    })
  ],
  server: {
    port: 5173,
    open: '/db.html',
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        db: resolve(__dirname, 'db.html')
      },
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'preview': [
            './src/preview/FilePreview.jsx',
            './src/preview/previews/ExcelPreview.jsx',
            './src/preview/previews/PdfPreview.jsx',
            './src/preview/previews/WordPreview.jsx'
          ]
        }
      },
      treeshake: {
        preset: 'recommended',
        moduleSideEffects: false
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        dead_code: true,
        unused: true,
        drop_console: false
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'zustand', 'axios']
  }
})