import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    nodePolyfills({
      include: [
        'buffer',
        'process',
        'crypto',
        'stream',
        'util'
      ],
      globals: {
        Buffer: true,
        global: true,
        process: true,
      }
    })
  ],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      crypto: 'crypto-browserify',
      stream: 'stream-browserify',
      buffer: 'buffer',
      util: 'util'
    }
  },
  define: {
    'process.env': {},
    'global': 'globalThis',
    // В Vite define принимает только строки, которые заменяются как есть
    // Поэтому мы не можем использовать функции здесь
  },
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          'ton-connect': ['@tonconnect/ui'],
          'vue-related': ['vue', 'vue-router', 'pinia'],
          'ton-libs': ['@ton/core', '@ton/ton', '@ton/crypto', '@orbs-network/ton-access']
        }
      }
    },
    // Оптимизация для продакшена
    minify: 'terser',
    terserOptions: {
      compress: {
        // drop_console: true, // Удаляет console.* в продакшене
        // drop_debugger: true,
        // pure_funcs: [
        //   'console.log',
        //   'console.info',
        //   'console.debug',
        //   'console.warn',
        //   'console.trace',
        //   'console.error' // Добавили ошибки для полного отключения
        // ], // Оставляет только вызовы console.error
      },
    },
  },
  optimizeDeps: {
    include: [
      'tonweb',
      'buffer',
      'process',
      'crypto-browserify',
      'stream-browserify',
      'util'
    ]
  }
})