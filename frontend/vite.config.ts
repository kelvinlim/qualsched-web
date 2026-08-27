import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

const backend = process.env.VITE_BACKEND_URL || "http://127.0.0.1:8030";

// Local `vite` / `npm run dev` (and local compose): stay at `/` so
// http://localhost:8040/ is unchanged. The production image sets
// VITE_BASE=/qualsched/ (see frontend/Dockerfile) so the browser requests
// /qualsched/assets/… and /qualsched/api/…; host nginx strips that prefix.
const base = process.env.VITE_BASE || "/";

export default defineConfig({
  plugins: [svelte()],
  base,
  server: {
    port: 8040,
    strictPort: true,
    host: true,
    proxy: {
      "/api": { target: backend, changeOrigin: true },
      "/auth": { target: backend, changeOrigin: true },
      "/health": { target: backend, changeOrigin: true },
    },
  },
  preview: {
    port: 8040,
    strictPort: true,
  },
});
