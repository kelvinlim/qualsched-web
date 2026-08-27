import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

const backend = process.env.VITE_BACKEND_URL || "http://127.0.0.1:8030";

export default defineConfig({
  plugins: [svelte()],
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
