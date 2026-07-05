import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite plays two roles in development:
//
//  1. It serves the frontend (this folder) to your browser with hot reload.
//  2. It PROXIES every request starting with /api to the Python backend
//     on port 8000. The browser thinks it's talking to one server —
//     exactly the job a reverse proxy (nginx, a load balancer) does in
//     production. It also means no CORS headaches in development.
//
// So: browser → vite (:5173) → fastapi (:8000) for /api/*,
//     browser → vite (:5173) for everything else (HTML/JS/CSS).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  // Vitest configuration. jsdom fakes a browser (document, DOM nodes) in
  // plain Node, so component tests run fast, with no real browser.
  // globals exposes afterEach etc. — Testing Library hooks into it to
  // unmount components between tests, so tests can't leak into each other.
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
