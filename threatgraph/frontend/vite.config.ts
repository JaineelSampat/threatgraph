import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In local dev, the frontend proxies /api to the FastAPI backend so the
// browser never needs CORS configured for localhost. In production the
// app talks to VITE_API_BASE_URL directly (see src/api/client.ts).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
